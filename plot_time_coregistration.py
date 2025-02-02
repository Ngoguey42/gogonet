"""Explained in README"""

import json
import sys
from pprint import pprint
import os
from concurrent.futures import ProcessPoolExecutor
import re

import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt

import constants as con
import tools

def process(ginfo):
    # Open game and video *********************************************************************** **
    egidx = ginfo.idx_in_encounter
    ename = ginfo.ename
    evdf = tools.load_evdf(ename, egidx)
    to_tvod, to_tdem = tools.create_timestamp_conversions(evdf, ginfo.vod_anchors)
    vpath = tools.path_of_vod(ename, egidx)
    vidcap = cv2.VideoCapture(vpath)

    for i, (_, ser) in enumerate(evdf.iterrows()):
        ev, t, round_idx = ser.ev, ser.t, ser.round_idx
        outpath = os.path.join(
            con.DB_PREFIX[os.path.sep],
            "events_plot",
            f"{ename}_{egidx}_{ginfo.mname}_{i:02d}_{ev}_{round_idx}.png",
        )
        if os.path.isfile(outpath):
            continue

        # Find the 2 images ********************************************************************* **
        imgs = []
        print(ename, i, ev, round_idx, t, to_tvod(t))
        for offset in [0.000, 0.150]:
            t1 = int((to_tvod(t) - ginfo.vod_file_start_offset + offset) * 1000)
            vidcap.set(cv2.CAP_PROP_POS_MSEC, t1)
            success, image = vidcap.read()
            assert success
            image = image[:, :, ::-1]
            imgs.append(image)

        # Plot ********************************************************************************** **
        fig, axes = plt.subplots(nrows=2, ncols=1, constrained_layout=True)
        for j in range(2):
            ax = axes.flatten()[j]
            ax.imshow(imgs[j])
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
        plt.savefig(outpath, dpi=250)
        plt.close("all")

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
        print("-", ginfo.ename, ginfo.idx_in_encounter, ginfo.mname
)
    with ProcessPoolExecutor(4) as ex:
        list(ex.map(process, ginfos))
