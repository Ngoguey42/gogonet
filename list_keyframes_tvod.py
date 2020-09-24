"""List the keyframe of encounter video files to json"""

import os
import json
import sys
from concurrent.futures import ProcessPoolExecutor
import re
import itertools
import datetime
import time

import pandas as pd
import numpy as np
import scipy.spatial
import matplotlib.pyplot as plt
import cv2
import skimage.io
from tqdm import tqdm
import av

import tools
import constants as con

def process(encounter):
    ename = encounter.ename
    outpath = os.path.join(
        con.DB_PREFIX[os.path.sep],
        f"{ename}_keyframes_tvod.json",
    )
    if os.path.isfile(outpath):
        return
    path = os.path.join(
        con.DB_PREFIX[os.path.sep],
        f"{ename}.mp4",
    )
    c = av.open(path)
    s = c.streams.video[0]
    s.codec_context.skip_frame = "NONKEY"
    tq = tqdm(total=float(s.duration * s.time_base), unit="avsec",
              position=encounter.idx, desc=ename)
    tavs = []
    for i, f in enumerate(c.decode(streams=[s.index])):
        if len(tavs) % 20 == 0:
            tq.n = f.time
            tq.display()
        assert f.pict_type == "I"
        tav = f.time
        tavs.append(tav)

    tq.close()
    print(ename, f' | first_keyframe_tav=_t("{tools.time_totxt(tavs[0])}"),\n')
    tvods = (np.asarray(tavs) - tavs[0] + encounter.first_keyframe_tvod).tolist()
    with open(outpath, "w") as stream:
        stream.write(json.dumps(tvods))

if __name__ == "__main__":
    sys.argv += [".*", ".*", ".*", ".*"]
    ename_regexp = sys.argv[1]

    encounters = [
        encounter
        for encounter in con.ENCOUNTERS.values
        if re.match(ename_regexp, encounter.ename)
    ]
    print("Will do:")
    for i, encounter in enumerate(encounters):
        print("-", encounter.ename)
        encounter["idx"] = i
    with ProcessPoolExecutor(4) as ex:
        # list(map(process, encounters))
        list(ex.map(process, encounters))
