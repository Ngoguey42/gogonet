import os
import json
import sys
from concurrent.futures import ProcessPoolExecutor
import re

import pandas as pd
import numpy as np
import scipy.spatial
import matplotlib.pyplot as plt
import cv2
import skimage.io

import tools
import constants as con

def process(ginfo):
    egidx = ginfo.idx_in_encounter
    ename = ginfo.ename
    ginfo = con.GAMES[(ename, egidx)]
    codf, evdf = tools.load_codf(ename, egidx), tools.load_evdf(ename, egidx)
    compodf = tools.load_compodf(ename, egidx)

    print(f"** {ename} ** {egidx} ** {ginfo.mname} ****************************************")
    oinfo = con.OVERLAYS[ginfo.oname]
    to_vod, to_dem = tools.create_timestamp_conversions(evdf, ginfo.vod_anchors)

    classify_tdem = tools.create_tdem_classifier(evdf)
    classif_per_row = {
        i: classify_tdem(row.t)
        for i, row in codf.iterrows()
    }
    codf["game_state"] = codf.reset_index()["index"].apply(lambda idx: classif_per_row[idx][0])
    codf["round_idx"] = codf.reset_index()["index"].apply(lambda idx: classif_per_row[idx][1])

    codf = codf[codf.game_state == "playing"]
    codf["round_idx"] = codf["round_idx"].astype(int)
    codf = codf[codf.round_idx.apply(lambda i: i not in ginfo.partial_minimap_rounds)]

    # Print player composition ****************************************************************** **
    tmp = compodf.copy()
    tmp["terro"] = tmp.terro.apply(
        lambda l: "".join(map('"{}", '.format, l))
    )
    tmp["ct"] = tmp.ct.apply(
        lambda l: "".join(map('"{}", '.format, l))
    )
    print(tmp.query("ct_count == 5 & terro_count == 5"))

    # Players movement speed ******************************************************************** **
    speeds = []
    for _, df in codf.groupby(["pname", "round_idx"]):
        dxy = ((df.x.diff() ** 2 + df.y.diff() ** 2) ** 0.5)
        dt = df.t.diff()
        speeds.append((dxy / dt).sort_values().dropna().values)
    speeds = np.sort(np.concatenate(speeds))
    speeds = speeds[speeds > 0]
    plt.hist(speeds, 150)
    plt.xticks(np.linspace(speeds.min(), speeds.max(), 35), fontsize=7, rotation=90)
    plt.xlabel('instant speed (worldunit/sec)')
    plt.ylabel('size of bin (log plot)')
    plt.yscale('log')
    plt.grid(True)
    outpath = os.path.join(
        con.DB_PREFIX[os.path.sep],
        "mm_localisation",
        f"{ename}_{egidx}_{ginfo.mname}_speed.png",
    )
    plt.savefig(outpath, dpi=500)
    plt.close("all")

    # Most spread timestamp ********************************************************************* **
    groups = [
        (tdem, df, round_idx)
        for (round_idx, tdem), df in codf.reset_index().groupby(["round_idx", "t"])
        if len(df) >= 9
    ]
    coords = [np.c_[df.x, df.y] for (_, df, _) in groups]
    dmats = [scipy.spatial.distance_matrix(a, a) for a in coords]
    mindists = np.asarray([
        dmat[mask].min()
        for dmat in dmats
        for mask in [~np.diag(np.ones(len(dmat))).astype(bool)]
    ])
    i = mindists.argmax()
    tdem, df, round_idx = groups[i]
    tvod = to_vod(tdem)
    print(f"{mindists.shape[0]} timesteps with enough alive players")
    print(f"mindist={mindists[i]:.1f} at idx={i} at "
          f"tdem={tools.time_totxt(tdem)} at tvod={tools.time_totxt(tvod)} "
          f"on round_idx={round_idx} with {len(groups[i][1])} players alive")
    print(groups[i][1])

    # Retrieve image from vod ******************************************************************* **
    vpath = tools.path_of_vod(ename, egidx)
    vidcap = cv2.VideoCapture(vpath)
    outpath = os.path.join(
        con.DB_PREFIX[os.path.sep],
        "mm_localisation",
        f"{ename}_{egidx}_{ginfo.mname}_{tools.time_totxt(tvod).replace(':', '-')}.png",
    )
    fps = vidcap.get(cv2.CAP_PROP_FPS) # Use the one from `cv2`, not the official one

    f0_float = (to_vod(tdem) - ginfo.vod_file_start_offset) * fps
    f0 = int(round(f0_float))
    print(f"frame: {f0} ({f0_float:.5f}, {(f0 - f0_float) / fps:+.5f}sec)")
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    success, img = vidcap.read()
    assert success
    img = img[:, :, ::-1]
    skimage.io.imsave(outpath, img)

    # Plot more infos to check manual clicks **************************************************** **
    try:
        iconsdf = tools.load_iconsdf(ename, egidx, tvod)
    except FileNotFoundError:
        return
    print(iconsdf)

    outpath = os.path.join(
        con.DB_PREFIX[os.path.sep],
        "mm_localisation",
        f"{ename}_{egidx}_{ginfo.mname}_{tools.time_totxt(tvod).replace(':', '-')}_check.png",
    )
    img = img[:oinfo.approx_minimap_slice[0].stop,
              :oinfo.approx_minimap_slice[1].stop]
    figure, ax = plt.subplots()
    ax.imshow(img)
    for _, ser in iconsdf.iterrows():
        ax.add_artist(plt.Circle(tuple(ser.xy), 8.))
    plt.savefig(outpath, dpi=2000)
    plt.close("all")

if __name__ == "__main__":
    sys.argv += [".*", ".*", ".*", ".*"]
    ename_regexp = sys.argv[1]
    egidx_regexp = sys.argv[2]
    mname_regexp = sys.argv[3]

    ginfos = [
        ginfo
        for ginfo in con.GAMES.values
        if re.match(".*" + ename_regexp + ".*", ginfo.ename)
        and re.match(".*" + egidx_regexp + ".*", str(ginfo.idx_in_encounter))
        and re.match(".*" + mname_regexp + ".*", ginfo.mname)
    ]
    print("Will do:")
    for ginfo in ginfos:
        print("-", ginfo.ename, ginfo.idx_in_encounter, ginfo.mname)
    with ProcessPoolExecutor(7) as ex:
        list(map(process, ginfos))
        # list(ex.map(process, ginfos))

#
