import json
import sys
from pprint import pprint

import numpy as np
import pandas as pd
import cv2

import constants as con
import tools

for (ename, egidx), ginfo in con.GAMES.items():
    if "vod_anchors" not in ginfo.index:
        continue

    print("***************************************************************************")
    print(ename)
    print(egidx, ginfo.mname)

    _, dfevs = tools.load_json(ename, egidx)
    print("first `dem` event:", dict(dfevs.iloc[0]))

    dfevs = dfevs.reset_index().set_index(["ev", "round_idx"])
    def get_tdem(ev, round_idx):
        """Find the event in df"""
        if ev == "round_first_displacement":
            ev = "round_freeze_end" # TODO: Find the time displacement between those 2 events
        return float(dfevs.loc[(ev, round_idx), "t"])

    claps = [
        pd.Series(dict(idx=i, tvod=a[3],
             tdem=get_tdem(a[1], a[2]),
             ev=a[1], round_idx=a[2]))
        for i, a in enumerate(ginfo.vod_anchors)
        if a[0] == "clap"
    ]
    for left_out_clap in claps:
        anchors = list(ginfo.vod_anchors)
        anchors.pop(left_out_clap.idx)
        to_vod, _ = tools.create_timestamp_conversions(dfevs, anchors)
        left_out_clap["tvod_pred"] = to_vod(left_out_clap.tdem)

    df = pd.DataFrame(claps)
    df["error"] = df.tvod_pred - df.tvod
    df["error"] = df.error.apply(
        lambda err:
        f"\033[32m{err:+.3f}\033[0m" if abs(err) < 0.025 else
        f"\033[36m{err:+.3f}\033[0m" if abs(err) < 0.050 else
        f"\033[33m{err:+.3f}\033[0m" if abs(err) < 0.100 else
        f"\033[31m{err:+.3f}\033[0m"
    )
    df = df[["idx", "ev", "round_idx", "tdem", "tvod", "tvod_pred", "error"]]
    print(df)
