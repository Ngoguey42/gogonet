"""Tiny script to move away the png from the rounds with a hidden minimap"""
import os
import tools
import shutil

import constants as con

l = []
for ginfo in con.GAMES.values:
    egidx = ginfo.idx_in_encounter
    ename = ginfo.ename
    evdf = tools.load_evdf(ename, egidx)
    ginfo = con.GAMES[(ename, egidx)]
    fps = ginfo.vod_framerate
    oinfo = con.OVERLAYS[ginfo.oname]
    to_tvod, to_tdem = tools.create_timestamp_conversions(evdf, ginfo.vod_anchors)
    evdf = evdf.reset_index().set_index(["ev", "round_idx"], verify_integrity=True)
    for round_idx in sorted(set(evdf.reset_index().round_idx)):
        if round_idx not in ginfo.partial_minimap_rounds:
            continue
        outpath = os.path.join(
            con.DB_PREFIX[os.path.sep],
            "mm_occlusions",
            f"{ename}_{egidx}_{ginfo.mname}_round{round_idx:02d}.png",
        )
        print(outpath)
        assert os.path.isfile(outpath)
        l.append(outpath)
pref = os.path.join(
    con.DB_PREFIX[os.path.sep],
    "mm_occlusions",
    "occ",
)
os.makedirs(pref, exist_ok=True)
for p in l:
    shutil.move(p, pref)
#
