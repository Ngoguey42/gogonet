import json
import sys
from pprint import pprint

import numpy as np
import pandas as pd
import cv2

import constants as con
import tools

ename, egidx = sys.argv[1:]
egidx = int(egidx)
dfticks, dfevs = tools.load_json(ename, egidx)
ginfo = con.GAMES[(ename, egidx)]

to_vod, to_dem = tools.create_timestamp_conversions(dfevs, ginfo.vod_anchors)

path = tools.path_of_vod(ename, egidx)
vidcap = cv2.VideoCapture(path)

for i, (t, ev, round_idx) in enumerate(
        list(dfevs.itertuples())[:]
):
    if "freeze" not in ev: continue
    imgs = []

    print(i, ev, round_idx, t, to_vod(t))
    for offset in (np.arange(9) * 0.05 - 0.2):
        t1 = int((to_vod(t) - ginfo.vod_file_start_offset + offset) * 1000)
        print(" ", offset)
        vidcap.set(cv2.CAP_PROP_POS_MSEC, t1)
        success, image = vidcap.read()
        assert success
        image = image[:, :, ::-1]
        imgs.append(image)
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(nrows=3, ncols=3)
    for j in range(9):
        print(j, len(axes.flatten()), len(imgs))
        axes.flatten()[j].imshow(imgs[j])
    plt.savefig(f"{ename}_{egidx}_{ginfo.mname}_{i:02d}_{ev}_{round_idx}.png", dpi=300)
