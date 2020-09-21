import os
import tools
import constants as con
import shutil
l = []
for ginfo in con.GAMES.values:
    egidx = ginfo.idx_in_encounter
    ename = ginfo.ename
    dfticks, dfevs = tools.load_json(ename, egidx)
    ginfo = con.GAMES[(ename, egidx)]
    fps = ginfo.vod_framerate
    oinfo = con.OVERLAYS[ginfo.oname]
    to_vod, to_dem = tools.create_timestamp_conversions(dfevs, ginfo.vod_anchors)
    dfevs = dfevs.reset_index().set_index(["ev", "round_idx"], verify_integrity=True)
    for round_idx in sorted(set(dfevs.reset_index().round_idx)):
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
