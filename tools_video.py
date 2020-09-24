"""Utility functions to procude ndarrays from video files in a training-ready way"""

import threading
import os
import json
import contextlib

import av
import numpy as np
import intervaltree

import tools
import constants as con

class AVOpener:
    """Since we can only open one file at a time with pyav, let's dedicate a thread to do that."""
    def __init__(self, pools, open_count_per_pool):
        self._t = threading.Thread(
            target=self._routine,
            args=(pools, open_count_per_pool),
            daemon=True,
        )
        self._t.start()
        self.done = False

    def _routine(self, pools, open_count_per_pool):
        pools = list(pools)
        pool_prio_value = lambda p: (
            min(p.waiting_indices) if p.waiting_indices else np.inf, p.open_count
        )
        while pools:
            # The next file to open should be where the most urgent thread is waiting
            pool = min(pools, key=pool_prio_value)
            pool.open_one_more()
            if pool.open_count == open_count_per_pool:
                pools.remove(pool)
        self.done = True

class AVFilePool:
    """Thread safe container of pyav pointers to a file.

    Initially the pool has no file opened and the `acquire` calls will be blocking. Calls to
    `open_one_more` will create new files, most likely performed by the AVOpener.
    """
    def __init__(self, path):
        self.sem = threading.Semaphore(0)
        self.path = path
        self.open_count = 0
        self._idle = []
        self.waiting_indices = set()

    def acquire(self, load_index):
        @contextlib.contextmanager
        def _acquire():
            self.waiting_indices.add(load_index)
            self.sem.acquire()
            self.waiting_indices.remove(load_index)

            obj = self._idle.pop() # If sem acquired, idle can't be empty
            try:
                yield obj
            finally:
                self._idle.append(obj)
                self.sem.release()
        return _acquire()

    def open_one_more(self):
        obj = av.open(self.path)
        # print("> Opened", self.path, obj, id(obj))
        self._idle.append(obj)
        self.open_count += 1
        self.sem.release()

class EncounterReader:
    """Optimized video frame reading with pyav. Thread safe.

    As soon as 3 threads are reading, pyav is quicker than opencv, but the files are very long
    to open with pyav and they have to bo opened sequencially. One `AVOpener` should be spawned to
    open the files.

    # Perfs as soon as all the files have been opened, for random frames
           python  frames   diminishing
           thread    per       return
    driver  count   second
      av      1      2,76         0%
      av      2      5,12         7%
      av      3      6,91         17%
      av      4      8,40         24%
      av      5      9,46         32%
      av      6      10,24        38%
      av      7      11,20        42%
      cv      1      6,92   (internally uses 5 or 6 threads)

    # Perfs as soon as all the files have been loaded, per frame, without diminishing return
    - For a key frame: 1/35 second
    - For other frames: 1/225 second times the distance to the previous keyframe.
      - Worst case ~120 => 0.56 second.
      - Mean case ~60 => 0.30 second.

    # Caveats
    - Doesn't cover before first keyframe, but might be possible.
    - Doesn't cover after last keyframe
    """
    def __init__(self, encounter):
        self.encounter = encounter
        self.vpath = os.path.join(
            con.DB_PREFIX[os.path.sep],
            f"{encounter.ename}.mp4",
        )
        self.pool = AVFilePool(self.vpath)

        # We need that interval tree to quickly find the keyframe preceding a frame.
        # Luckily its really quick to instanciate and to fetch
        self.intervals = intervaltree.IntervalTree()
        path = os.path.join(
            con.DB_PREFIX[os.path.sep],
            f"{encounter.ename}_keyframes_tvod.json",
        )
        kfs = np.asarray(json.loads(open(path).read()))
        kfs_left = (kfs - 0.5 / encounter.vod_framerate).clip(0, np.inf)
        kfs_left_left = np.nextafter(kfs_left, -np.inf).clip(0, np.inf)
        kfs_right_right = (kfs + 0.5 / encounter.vod_framerate)
        kfs_right = np.nextafter(kfs_right_right, -np.inf)

        for i in range(len(kfs) - 1):
            self.intervals[kfs_left[i]:kfs_right[i]] = ("on", kfs[i])
            self.intervals[kfs_right_right[i]:kfs_left_left[i+1]] = ("after", kfs[i])
        self.intervals[kfs_left[-1]:kfs_right[-1] = ("on", kfs[-1])

        self._to_tvod_per_egidx = {
            g.idx_in_encounter: to_tvod
            for g in encounter.games
            for evdf in [tools.load_evdf(g.ename, g.idx_in_encounter)]
            for to_tvod, _ in [tools.create_timestamp_conversions(evdf, g.vod_anchors)]
        }

    def get(self, egidx=None, mname=None, tvod=None, tav=None, load_index=None):
        # Convert args ************************************************************************** **
        assert (tvod is None) ^ (tav is None) == 2, "Need exactly one input time"
        if tvod is not None:
            tav = tvod - kf0_tvod + kf0_tav
        elif tav is not None:
            tvod = tav + kf0_tvod - kf0_tav

        kf0_tvod, kf0_tav = self.encounter.first_keyframe_tvod, self.encounter.first_keyframe_tav
        fps = self.encounter.vod_framerate

        # Find keyframe ************************************************************************* **
        (_, _, (where, kf_tvod)), = self.intervals.at(tvod)
        kf_tav = kf_tvod - kf0_tvod + kf0_tav

        with self.pool.acquire(load_index) as c:
            s = c.streams.video[0]
            t = int(round(kf_tav / s.time_base))

            # This combination of bool parameters is the only reliable to fetch a frame:
            # - `any_frame=True` to fetch a non-key frame doesnt work
            # - `backward=True` to fetch a keyframe is unreliable
            c.seek(t, any_frame=False, stream=s, backward=False)

            # Fetch keyframe ******************************************************************** **
            gen = c.decode(streams=[s.index])
            f = next(gen)
            assert abs(f.time - kf_tav) < fps * 0.5
            if where == "on":
                return f.to_rgb().to_ndarray()
            elif where == "after":
                # Move to needed frame from keyframe ******************************************** **
                # (pyav recommends this technique to fetch a non-key frame)
                dist = round((tav - f.time) * fps)
                assert 0 <= dist < fps * 60 # Small sanity check to avoid infinite loops
                for _ in range(dist):
                    f = next(gen)
                assert abs(f.time - kf_tav) < fps * 0.5
                return f.to_rgb().to_ndarray()
            else:
                assert False, "unreachable"
