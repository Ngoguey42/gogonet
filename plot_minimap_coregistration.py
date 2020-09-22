"""A script to help in the process of computing the transformation matrix from the minimap
space to the world space.

It is pretty clean but some pieces of logic are a bit convoluted, especially with pandas.
"""

import os
import json
import sys
from concurrent.futures import ProcessPoolExecutor
import re
import itertools

import pandas as pd
import numpy as np
import scipy.spatial
import matplotlib.pyplot as plt
import cv2
import skimage.io
from tqdm import tqdm

import tools
import constants as con

def lstsq(worldx, mmx, worldy, mmy, maskx, masky):
    # Need to negate `y` to transform
    c0 = np.r_[worldx, -worldy]
    c1 = np.r_[np.ones_like(worldx), np.zeros_like(worldy)]
    c2 = np.r_[np.zeros_like(worldx), np.ones_like(worldy)]
    c3 = np.r_[mmx, mmy]
    mask = np.r_[maskx, masky]
    scale, offsetx, offsety = np.linalg.lstsq(np.c_[c0, c1, c2][mask], c3[mask], rcond=None)[0]
    c3_bis = c0 * scale + c1 * offsetx + c2 * offsety
    mmerr = np.abs(c3_bis - c3)
    rmse = (mmerr ** 2).mean() ** 0.5
    return scale, offsetx, offsety, mmerr.mean(), mmerr.max(), np.median(mmerr), rmse

def process(ginfo):
    egidx = ginfo.idx_in_encounter
    ename = ginfo.ename
    ginfo = con.GAMES[(ename, egidx)]
    oinfo = con.OVERLAYS[ginfo.oname]

    print("*" * 100)
    print(f"** {ename} ** {egidx} ** {ginfo.mname} ****************************************")
    evdf = tools.load_evdf(ename, egidx)
    compodf = tools.load_compodf(ename, egidx)
    codf = tools.load_codf(ename, egidx)
    to_tvod, to_tdem = tools.create_timestamp_conversions(evdf, ginfo.vod_anchors)
    classify_tdem = tools.create_tdem_classifier(evdf)

    # Print teams composition to help feeding `players_order` in constants.py ******************* **
    print("> Teams composition")
    tmp = compodf.copy()
    tmp["terro"] = tmp.terro.apply(lambda l: "".join(map('"{}", '.format, l)))
    tmp["ct"] = tmp.ct.apply(lambda l: "".join(map('"{}", '.format, l)))
    print(tmp.query("ct_count == 5 & terro_count == 5"))

    # Find timestamp for `annotated_vod_frame` in constants.py ********************************** **
    if "annotated_vod_frame" not in ginfo:
        print("> Searching for a good annotation frame where players are alive and spread")
        rounds = sorted(set(range(ginfo.round_count)) - ginfo.partial_minimap_rounds)

        # Throwing out invalid rounds
        tmp = evdf.set_index(["round_idx", "ev"])
        mask = codf.t.apply(lambda _: False)
        for round_idx in set(evdf.round_idx) - ginfo.partial_minimap_rounds:
            t0 = float(tmp.loc[(round_idx, "round_freeze_end")])
            t1 = float(tmp.loc[(round_idx, "round_end")])
            mask = mask | ((codf.t >= t0) & (codf.t < t1))

        # Keeping 1 frame per second
        mask = mask & (codf.t % 1. < 0.45 / 128)
        assert mask.sum() > 0

        # Let's find the timestamp with the highest min-dist-between-players, with >= 9 players alive
        group_per_tdem = [
            df
            for _, df in codf[mask].groupby("t")
            if len(df) >= 9
        ]
        print(f"  {len(group_per_tdem)} frame candidates")
        coords_per_tdem = [np.c_[df.x, df.y] for df in group_per_tdem]
        dmat_per_tdem = [scipy.spatial.distance_matrix(a, a) for a in coords_per_tdem]
        mindist_per_tdem = np.asarray([
            dmat[~np.diag(np.ones(len(dmat))).astype(bool)].min()
            for dmat in dmat_per_tdem
        ])
        small_codf = group_per_tdem[mindist_per_tdem.argmax()]
        tdem = small_codf.t.iloc[0]
        tvod = to_tvod(tdem)
        _, round_idx = classify_tdem(tdem)
    else:
        print("> Got an annotated frame...")
        tvod = ginfo.annotated_vod_frame
        tdem = to_tdem(tvod)
        _, round_idx = classify_tdem(tdem)
        small_codf = codf[(codf.t >= tdem - 0.5/128) & (codf.t <= tdem + 0.5/128)]

    print(f"  Ref frame at tdem={tools.time_totxt(tdem)} at "
          f"tvod={tools.time_totxt(tvod)}({tvod}) "
          f"on round_idx={round_idx} with {len(small_codf)} players alive")
    assert 9 <= len(small_codf) <= 10

    # Retrieve frame from vod and save it for annotation with QGis ****************************** **
    outpath = os.path.join(
        con.DB_PREFIX[os.path.sep],
        "mm_localisation",
        f"{ename}_{egidx}_{ginfo.mname}_{tools.time_totxt(tvod).replace(':', '-')}.png",
    )
    if not os.path.isfile(outpath):
        print(f"> Create {outpath}")
        vpath = tools.path_of_vod(ename, egidx)
        vidcap = cv2.VideoCapture(vpath)
        fps = vidcap.get(cv2.CAP_PROP_FPS) # Use the fps from `cv2`, not the official one
        f0_float = (to_tvod(tdem) - ginfo.vod_file_start_offset) * fps
        f0 = int(round(f0_float))
        diff_with_tvod = (f0 - f0_float) / fps
        print(f"frame: {f0} ({f0_float:.5f}, {diff_with_tvod:+.5f}sec)")
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, f0)
        success, img = vidcap.read()
        assert success
        img = img[:, :, ::-1]
        skimage.io.imsave(outpath, img)

    # Stop here if annotation not available yet ************************************************* **
    if "annotated_vod_frame" not in ginfo:
        return
    iconsdf = tools.load_iconsdf(ename, egidx)

    # Plots to ascertain the quality of manual clicks ******************************************* **
    outpath = os.path.join(
        con.DB_PREFIX[os.path.sep],
        "mm_localisation",
        f"{ename}_{egidx}_{ginfo.mname}_{tools.time_totxt(tvod).replace(':', '-')}_check.png",
    )
    print(f"> Create {outpath}")
    if not os.path.isfile(outpath):
        img = img[:oinfo.approx_minimap_slice[0].stop, :oinfo.approx_minimap_slice[1].stop]
        figure, ax = plt.subplots()
        ax.imshow(img)
        for _, ser in iconsdf.iterrows():
            ax.add_artist(plt.Circle((ser.x, ser.y), 8.))
        plt.savefig(outpath, dpi=2000)
        plt.close("all")

    # Compute the `minimap_transform` field for constants.py ************************************ **
    print("> Computing the transformation matrix from world to minimap")
    df = iconsdf.merge(small_codf, on="pname", suffixes=['mm', 'world']).set_index("label")
    df = df[["pname", "xmm", "xworld", "ymm", "yworld"]]

    # Let's not use the coordinates that vary near the annotated frame
    span = 0.050
    span_codf = codf[(codf.t >= tdem - span) & (codf.t <= tdem + span)]
    print(f"  Warching player coords on {len(span_codf)} frames around")
    most_varying_coords = (
        span_codf.groupby("pname").std()[["x", "y"]]
        .reset_index().set_index("pname").unstack().sort_values()
        .iloc[-4:].index
    )
    maskx = df.xmm.apply(lambda _: True)
    masky = df.xmm.apply(lambda _: True)
    for coordname, pname in most_varying_coords:
        if coordname == "x":
            maskx = maskx & (df.pname != pname)
        else:
            masky = masky & (df.pname != pname)

    scale, offsetx, offsety, mmerr_mean, mmerr_max, mmerr_med, mmerr_rmse = lstsq(
        df.xworld, df.xmm, df.yworld, df.ymm, maskx, masky
    )
    df["xmm_bis"] = df.xworld * scale + offsetx
    df["ymm_bis"] = df.yworld * -scale + offsety
    df["xmm_err"] = df.xmm_bis - df.xmm
    df["ymm_err"] = df.ymm_bis - df.ymm
    df = df[["pname", "xworld", "xmm", "xmm_bis", "xmm_err", "yworld", "ymm", "ymm_bis", "ymm_err"]]
    print(df)

    # Print what's needed for constants.py
    s = '/.join'.join(f"{pname}@{c}" for c, pname in most_varying_coords)
    print(f"  # Calculated from {ename}@{tools.time_totxt(tvod)}")
    print(f"  # fit errors (pixels): rmse={mmerr_rmse:.2f}, max={mmerr_max:.2f}, evicted-coords:{s}")
    print(f"  {ginfo.mname}=dict(scale={scale}, xoffset={offsetx}, yoffset={offsety}),")

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
