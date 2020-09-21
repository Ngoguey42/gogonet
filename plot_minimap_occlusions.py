import json
import sys
from pprint import pprint
import re
from concurrent.futures import ProcessPoolExecutor
import os

import numpy as np
import pandas as pd
import cv2
from tqdm import tqdm
import skimage.transform as skt
import skimage.io
import constants as con
import tools

DOWNSAMPLE_SCALE = 0.25

def process(ginfo):
    egidx = ginfo.idx_in_encounter
    ename = ginfo.ename
    dfticks, dfevs = tools.load_json(ename, egidx)
    ginfo = con.GAMES[(ename, egidx)]
    oinfo = con.OVERLAYS[ginfo.oname]
    to_vod, to_dem = tools.create_timestamp_conversions(dfevs, ginfo.vod_anchors)

    path = tools.path_of_vod(ename, egidx)
    print("> opening", path)
    vidcap = cv2.VideoCapture(path)
    fps = vidcap.get(cv2.CAP_PROP_FPS) # Use the one from `cv2`, not the official one

    dfevs = dfevs.reset_index().set_index(["ev", "round_idx"], verify_integrity=True)
    for round_idx in sorted(set(dfevs.reset_index().round_idx)):
        outpath = os.path.join(
            con.DB_PREFIX[os.path.sep],
            "mm_occlusions",
            f"{ename}_{egidx}_{ginfo.mname}_round{round_idx:02d}.png",
        )
        if os.path.isfile(outpath):
            continue
        print("> Starting", outpath)
        tdem0 = dfevs.loc[("round_freeze_end", round_idx), "t"]
        tdem1 = dfevs.loc[("round_end", round_idx), "t"]
        assert isinstance(tdem0, float), tdem0
        assert isinstance(tdem1, float), tdem1
        print(f"  > round {round_idx}"
              f", tdem {tools.time_totxt((tdem0))} -> {tools.time_totxt((tdem1))} "
              f", tvod {tools.time_totxt(to_vod(tdem0))} -> {tools.time_totxt(to_vod(tdem1))}"
              f", len {tools.time_totxt(tdem1 - tdem0)}"
        )

        f0_float = (to_vod(tdem0) - ginfo.vod_file_start_offset) * fps
        f0 = int(round(f0_float))
        print(f"  > first frame: {f0} ({f0_float:.5f}, {(f0 - f0_float) / fps:+.5f}sec)")

        fcount_float = (tdem1 - tdem0) * fps
        fcount = int(np.floor(np.around(fcount_float, 5)))
        print(f"  > frame count: {fcount} ({fcount_float:.5f}, {(fcount - fcount_float) / fps:+.5f}sec)")

        vidcap.set(cv2.CAP_PROP_POS_FRAMES, f0)

        mmh = int(np.ceil(DOWNSAMPLE_SCALE * oinfo.approx_minimap_height))
        mmw = int(np.ceil(DOWNSAMPLE_SCALE * oinfo.approx_minimap_width))
        assert fcount * mmh * mmw * 3 < 1000 ** 3, "About to allocate a tensor >1GB"
        mms = np.empty((fcount, mmh, mmw, 3), "uint8")
        print("  > preallocated minimaps tensor:", mms.dtype, mms.shape, mms.size / 1000 ** 2, "MB")
        for i, f in tqdm(enumerate(range(f0, f0 + fcount)), total=fcount, disable=True):
            assert vidcap.get(cv2.CAP_PROP_POS_FRAMES) == f0 + i
            success, img = vidcap.read()
            assert success
            img = img[:, :, ::-1]
            img = img[oinfo.approx_minimap_slice]
            img = cv2.resize(img, (mmw, mmh), interpolation=cv2.INTER_CUBIC)
            mms[i] = img

        mean_adiffs = np.abs(np.diff(mms.astype("int16"), axis=0)).astype("int32").mean(axis=(1, 2, 3))
        def get_k_largest_indices(a, k): # unordered
            return sorted(np.argpartition(a, len(a) - k)[-k:])

        tiles = []
        for lefti in get_k_largest_indices(mean_adiffs, 8 * 9):
            img = np.hstack([mms[lefti], mms[lefti + 1]])
            img = np.pad(img, [(1, 1), (1, 1), (0, 0)], constant_values=255)
            tiles.append(img)
        tiles = np.asarray(tiles).reshape(9, 8, *tiles[0].shape)
        tiles = np.vstack([np.hstack(list(a)) for a in tiles])
        skimage.io.imsave(outpath, tiles)

if __name__ == "__main__":
    sys.argv += [".*", ".*", ".*", ".*"]
    ename_regexp = sys.argv[1]
    egidx_regexp = sys.argv[2]
    mname_regexp = sys.argv[3]

    ginfos = [
        ginfo
        for ginfo in con.GAMES.values
        if re.match(ename_regexp, ginfo.ename)
        and re.match(egidx_regexp, str(ginfo.idx_in_encounter))
        and re.match(mname_regexp, ginfo.mname)
    ]
    print("Will do:")
    for ginfo in ginfos:
        print("-", ginfo.ename, ginfo.idx_in_encounter, ginfo.mname)

    with ProcessPoolExecutor(3) as ex:
        list(ex.map(process, ginfos))
