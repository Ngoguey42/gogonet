"""Looking for strategies to read from of my h265/mp4 files.

/!\ Files very disorganised! The conclusion of this file is the content of `tools_video.py.

# Tests

Loading 3 central frames in all the valid rounds

The video files are stored on an m.2. ssd.

Purging or not the page cache (called standby on windows) doesnt seem to change the perfs a lot.

All the tests (except the first) are made with page cache full

All tests were made from ipython from a windows terminal

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=3 | SPAN=10s | Reopen vidcap for each frame
   | tests.sort_values(["vpath", "frame"])
 total 3:13.986 (0.309387 * 627)
vidcap 1:26.221 (0.137513 * 627)
   set 1:42.064 (0.162782 * 627)
  read 5.651386 (0.009013 * 627)

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=3 | SPAN=10s | Reopen vidcap for each frame
   | tests.sort_values(["vpath", "frame"])
 total 3:11.868 (0.306010 * 627)
vidcap 1:25.627 (0.136566 * 627)
   set 1:40.636 (0.160505 * 627)
  read 5.568535 (0.008881 * 627)
conclusion: This is really a CPU job, page cache changes by 2 sec (if not noise)

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=3 | SPAN=10s | Vidcap cache
   | tests.sort_values(["vpath", "frame"])
 total 1:28.130 (0.140559 * 627)
vidcap 0.531376 (0.132844 * 4)
   set 1:23.320 (0.132888 * 627)
  read 4.737410 (0.007555 * 627)
conclusion: Vidcap object must be reused

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=3 | SPAN=1/60s | Vidcap cache
   | tests.sort_values(["vpath", "frame"])
 total 1:27.533 (0.138942 * 630)
vidcap 0.475003 (0.118750 * 4)
   set 1:22.785 (0.131405 * 630)
  read 4.675826 (0.007421 * 630)
conclusion: Locality is really not a parameter when using `.set` for each frame

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=3 | SPAN=1/60s | Vidcap cache
    | tests.sample(frac=1)
 total 1:26.383 (0.137116 * 630)
vidcap 0.470032 (0.117508 * 4)
   set 1:21.685 (0.129660 * 630)
  read 4.632678 (0.007353 * 630)
conclusion: Confirmation of previous test

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=3 | SPAN=1frame | Vidcap cache
   | tests.sort_values(["vpath", "frame"])
   | don't .set if already on right frame
 total 32.09283 (0.050941 * 630)
vidcap 0.464028 (0.116007 * 4)
   set 28.04907 (0.133567 * 210)
  read 3.978670 (0.006315 * 630)
conclusion: Calling `set` slows everything. I guess that `set` resets the decompression infos

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=9 | SPAN=1frame | Vidcap cache
    | tests.sort_values(["vpath", "frame"])
    | don't .set if already on right frame
 total 38.53929 (0.020391 * 1890)
vidcap 0.465029 (0.116257 * 4)
   set 27.45820 (0.130753 * 210)
  read 10.90418 (0.005769 * 1890)
conclusion: The extra `reads` are free in this setup

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=120 | SPAN=1frame | Vidcap cache
    | tests.sort_values(["vpath", "frame"])
    | don't .set if already on right frame
 total 1:37.051 (0.007702 * 12600)
vidcap 0.468002 (0.117000 * 4)
   set 25.95297 (0.123585 * 210)
  read 1:10.033 (0.005558 * 12600)
conclusion: In this setup the reads dominate the total time, they kept a constant time

### opencv | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=500 | SPAN=1frame | Vidcap cache
    | tests.sort_values(["vpath", "frame"])
    | don't .set if already on right frame
    | tests.head(10000)
 total 58.82580 (0.005882 * 10000)
vidcap 0.090977 (0.090977 * 1)
   set 2.109750 (0.105487 * 20)
  read 55.91536 (0.005591 * 10000)
conclusion: same. 170 fps with this setup, 7.1 fps with the .set setup

### opencv | FRAMES_ORIGIN="first_keyframes" | FRAME_COUNT=300 | Vidcap cache
    | tests.sort_values(["vpath", "frame"])
 total 59.90422 (0.199680 * 300)
vidcap 0.479044 (0.119761 * 4)
   set 57.64463 (0.194089 * 297)
  read 2.213560 (0.007378 * 300)
conclusion: opencv is slower to decode keyframes than random frames...

### opencv | FRAMES_ORIGIN="first_keyframes" | FRAME_COUNT=500 | Vidcap cache
    | tests.sort_values(["vpath", "frame"])
 total 1:39.851 (0.199702 * 500)
vidcap 0.479031 (0.119757 * 4)
   set 1:35.968 (0.193095 * 497)
  read 3.820794 (0.007641 * 500)

### av | FRAMES_ORIGIN="first_keyframes" | FRAME_COUNT=1000 | open cache
    | tests.sort_values(["vpath", "frame"])
     total 42.53146 (0.042531 * 1000)
     open 13.43563 (3.358908 * 4)
     seek 0.116660 (0.000116 * 1000)
   decode 0.010913 (0.000010 * 1000)
     next 26.83329 (0.026833 * 1000)
     tonp 15.34535 (0.015345 * 1000)
conclusions:
- many warning from av on one file but the image seem valid.
- way better perms on this task than opencv
- Only one thread used where opencv uses 5 or 6
- av is 4.68x faster per image and uses 5.5x less cpu (26.7x faster)

### av | FRAMES_ORIGIN="first_keyframes" | FRAME_COUNT=1000 | open cache
    | .sample
     total 42.30497 (0.042304 * 1000)
     open 13.41664 (3.354160 * 4)
     seek 0.123393 (0.000123 * 1000)
   decode 0.011973 (0.000011 * 1000)
     next 26.56819 (0.026568 * 1000)
     tonp 15.38991 (0.015389 * 1000)
conclusions: same perms with random access

### av | FRAMES_ORIGIN="mid_rounds" | FRAME_COUNT=1 | open cache
    | tests.sort_values(["vpath", "frame"])
    | Seek prev I and decode to target
    | Improved `tonp` phase
     total 1:17.138 (0.367327 * 210)
      open 13.47423 (3.368558 * 4)
  decode_i 5.071225 (0.024148 * 210)
 decode_bp 1:11.107 (0.004439 * 16016)
      tonp 0.550962 (0.002623 * 210)
- conclusions: Slower than opencv but still uses 1 cpu

### av | all keyframes  | open cache | tests.sort_values(["vpath", "frame"])
    | Seek with backward=False, and any_frame=False
     total 8:52.197 (0.027646 * 19250)
      open 13.57610 (3.394026 * 4)
  decode_i 7:44.495 (0.024129 * 19250)
 decode_bp 0.000000
      tonp 51.68662 (0.002685 * 19250)
- conclusion: way quicker than opencv on this task

"""
DRY_RUN = False
# DRY_RUN = True
# FRAME_COUNT = 300
FRAME_COUNT = 20
# FRAME_COUNT = 100000000
FRAMES_ORIGIN = "mid_rounds"
# FRAMES_ORIGIN = "first_keyframes"
# USING = "cv2"
USING = "av"
USING = "avreader"
THREAD_COUNT = 7

def SORT(df):
    return df.sample(frac=1)
    # return df.sort_values(["vpath", "frame"]) #.head(1000)
    # return df.sort_values(["vpath", "frame"])

import os
import json
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import re
import itertools
import datetime
import time
import collections
import threading
import contextlib

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
from tools import T
from tools_video import AVOpener, AVFilePool, EncounterReader

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
ginfos = list(con.GAMES.values)

if FRAMES_ORIGIN == "mid_rounds":
    rdf = tools.load_rdf()
    rdf = rdf[~rdf.partial_minimap].drop(columns=["partial_minimap"])
    rdf["fps"] = rdf.apply(lambda ser: con.GAMES[(ser.ename, ser.egidx)].vod_framerate, axis=1)
    rdf = rdf.set_index(["ename", "egidx", "round_idx"])
    l = []
    for i in range(FRAME_COUNT):
        l.append(
            rdf.tvod_start / 2 + rdf.tvod_end / 2 - (1 / rdf.fps) * i,
        )
    tests = pd.concat(l).reset_index().rename(columns={0: "tvod"})
    # tests = tests.sort_values(["ename", "egidx", "round_idx"])
elif "key" in FRAMES_ORIGIN:
    rows = []
    for encounter in con.ENCOUNTERS.values:
        tree = intervaltree.IntervalTree()
        path = os.path.join(
            con.DB_PREFIX[os.path.sep],
            f"{encounter.ename}_keyframes_tvod.json",
        )
        kfs = np.asarray(json.loads(open(path).read()))
        count = min(FRAME_COUNT // len(con.ENCOUNTERS), len(kfs))
        for i in range(count):
            rows.append(dict(
                ename=encounter.ename,
                round_idx=0, # osef
                egidx=0, # osef
                tvod=kfs[i],
            ))
    tests = pd.DataFrame(rows)

tests["loaded"] = False
tests["vpath"] = tests.apply(lambda ser: tools.path_of_vod(ser.ename, ser.egidx), axis=1)
tests["fps"] = tests.apply(lambda ser: con.GAMES[(ser.ename, ser.egidx)].vod_framerate, axis=1)
tests["vod_offset"] = tests.apply(lambda ser: con.GAMES[(ser.ename, ser.egidx)].vod_file_start_offset, axis=1)
tests["first_keyframe_tvod"] = tests.apply(lambda ser: con.GAMES[(ser.ename, ser.egidx)].first_keyframe_tvod, axis=1)
tests["first_keyframe_tav"] = tests.apply(lambda ser: con.GAMES[(ser.ename, ser.egidx)].first_keyframe_tav, axis=1)

tests["frame_float"] = (tests.tvod - tests.vod_offset) * tests.fps
tests["frame"] = tests.frame_float.round().astype(int)

tests["tav"]  = tests.tvod - tests.first_keyframe_tvod + tests.first_keyframe_tav

tests = SORT(tests)

readers = {
    e.ename: EncounterReader(e)
    for e in con.ENCOUNTERS.values
}

print(tests.head())
print(tests.shape)
if DRY_RUN:
    exit()

if USING == "avreader":
    t_total = T()
    t_open = T()
    tp = ThreadPoolExecutor(THREAD_COUNT)

    allocator = AVOpener(
        [r.pool for r in readers.values()],
        THREAD_COUNT
    )

    # time.sleep(3 * 60)
    def work(tup):
        (load_index, ser) = tup
        global t_total
        with T() as tmp0:
            img = readers[ser.ename].get(egidx=ser.egidx, tav=ser.tav, load_index=load_index)
            assert img.shape == (1080, 1920, 3)
        t_total += tmp0

    series = [t[1] for t in tests.iterrows()]
    it = tp.map(work, enumerate(series))
    it = tqdm(it, total=len(series), disable=False)
    list(it)

    print("Done")
    print("    total", t_total)
    print("     open", t_open)


elif USING == "av":
    t_total = T()
    t_open = T()
    t_decode_i = T()
    t_decode_bp = T()
    t_tonp = T()

    open_cache = {}
    for vpath in set(tests.vpath):
        print("opening with av", vpath)
        with T() as tmp0:
            open_cache[vpath] = av.open(vpath)
        t_open += tmp0

    for i, (_, ser) in enumerate(tqdm(tests.iterrows(), total=len(tests), disable=False)):
        with T() as tmp0:
            c = open_cache[ser.vpath]
            s = c.streams.video[0]
            # s.codec_context.skip_frame = "NONKEY"
            t = int(round(ser.tav / s.time_base))
            if "key" in FRAMES_ORIGIN:
                c.seek(t, any_frame=False, stream=s, backward=False)
                # assert False
                # c.seek(t, any_frame=True, stream=s, backward=True)
            else:
            # if True:
                c.seek(t, any_frame=False, stream=s, backward=True)
            gen = c.decode(streams=[s.index])

            with T() as tmp:
                f = next(gen)
            t_decode_i += tmp
            f0 = f

            # if "key" in FRAMES_ORIGIN:
                # assert bool(f.key_frame)
                # assert abs(f.time - ser.tav) < 0.5 / 60, (t, ser.tav, f.time, f.key_frame, f)
            # else:
            i_idxs = [-1]
            dist = round((ser.tav - f0.time) * ser.fps)
            for i in range(dist):
                with T() as tmp:
                    f = next(gen)
                t_decode_bp += tmp
                if f.key_frame:
                    i_idxs += [i]
            assert abs(f.time - ser.tav) < ser.fps * 1.2
            if len(i_idxs) != 1:
                print(f"|||| {i_idxs} {ser.ename} "
                      f"tvod:{tools.time_totxt(ser.tvod)} "
                      f"tav:{tools.time_totxt(ser.tav)} "
                      f"dist:{dist}"
                )


            with T() as tmp:
                img = f.to_rgb().to_ndarray()
            t_tonp += tmp
            assert img.shape == (1080, 1920, 3)

            # skimage.io.imsave(f"{ser.ename}_{tools.time_totxt(ser.tvod).replace(':', '-')}_usingav.png", img)

        t_total += tmp0
    print("Done")

    print("    total", t_total)
    print("     open", t_open)
    print(" decode_i", t_decode_i)
    print(" decode_bp", t_decode_bp)
    print("     tonp", t_tonp)


elif USING == "cv2":
    t_total = T()
    t_vidcap = T()
    t_set = T()
    t_read = T()

    vidcap_cache = {}
    for vpath in set(tests.vpath):
        print("opening with cv2", vpath)
        with T() as tmp0:
            vidcap_cache[vpath] = cv2.VideoCapture(vpath)
        t_vidcap += tmp0

    for i, (_, ser) in enumerate(tqdm(tests.iterrows(), total=len(tests))):
        with T() as tmp0:
            vidcap = vidcap_cache[ser.vpath]
            # with T() as tmp:
            #     vidcap = cv2.VideoCapture(tools.path_of_vod(ser.ename, ser.egidx))
            # t_vidcap += tmp

            if vidcap.get(cv2.CAP_PROP_POS_FRAMES) != ser.frame:
                with T() as tmp:
                    vidcap.set(cv2.CAP_PROP_POS_FRAMES, ser.frame)
                t_set += tmp

            with T() as tmp:
                success, img = vidcap.read()
            t_read += tmp
            assert success
            assert img.shape == (1080, 1920, 3)
        t_total += tmp0
    print("Done")

    print(" total", t_total)
    print("vidcap", t_vidcap)
    print("   set", t_set)
    print("  read", t_read)
