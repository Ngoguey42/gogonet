import json
from pprint import pprint
import os

import numpy as np
import pandas as pd

import constants as con

def segment_rounds(evs):
    # State machine to identify full rounds with a sound chain of events
    rounds = []
    latest_timings = {}
    latest_unfreeze_ridx = None # Only trust round idx at unfreeze

    def not_bigger(a, b):
        if a is None: return True
        if b is None: return True
        return not (a > b)

    def flush():
        nonlocal latest_timings, latest_unfreeze_ridx
        t = latest_timings
        if (t.get("round_start") is not None and
            t.get("round_freeze_end") is not None
        ):
            assert latest_unfreeze_ridx is not None
            assert not_bigger(t.get("round_start"), t.get("round_freeze_end")), t
            assert not_bigger(t.get("round_freeze_end"), t.get("bomb_planted")), t
            assert not_bigger(t.get("bomb_planted"), t.get("bomb_defused")), t
            assert not_bigger(t.get("bomb_planted"), t.get("bomb_exploded")), t
            if "bomb_defused" in t:
                assert "bomb_planted" in t
            if "bomb_exploded" in t:
                assert "bomb_planted" in t
                assert "bomb_defused" not in t
            rounds.append(dict(
                round_idx=latest_unfreeze_ridx,
                **t
            ))
        latest_timings = {}
        latest_unfreeze_ridx = None

    for ev in evs:
        if ev["ev"] == "round_start":
            flush()
        assert latest_timings.get(ev["ev"]) == None, (latest_timings, ev)
        latest_timings[ev["ev"]] = ev["t"]
        if ev["ev"] == "round_freeze_end":
            latest_unfreeze_ridx = ev["round_idx"]

    flush()
    return rounds

def path_of_json(ename, egidx):
    prefix = con.DB_PREFIX[os.path.sep]
    mname = con.GAMES[(ename, egidx)].mname
    return os.path.join(prefix, f"{ename}_{egidx}_{mname}.json")

def path_of_vod(ename, egidx):
    prefix = con.DB_PREFIX[os.path.sep]
    mname = con.GAMES[(ename, egidx)].mname
    return os.path.join(prefix, f"{ename}.mp4")

def load_json(ename, egidx):
    path = path_of_json(ename, egidx)
    print("reading", path)
    j = open(path).read()

    print("parsing json")
    j = json.loads(j)
    print("slicing json")
    l = [ev for ev in j if ev["ev"] == "tickend"]

    print("making df")
    rows = []
    for ev in l:
        for pid, (x, y, z, alive) in ev["pinfo"].items():
            if not alive:
                continue
            rows.append(dict(
                x=x, y=y, z=z, t=ev["t"], pid=pid,
            ))
    dfticks = pd.DataFrame(rows).set_index(["t", "pid"], verify_integrity=True)
    print(dfticks)


    rows = []
    for r in segment_rounds([ev for ev in j if ev["ev"] != "tickend"]):
        round_idx = r.pop("round_idx")
        rows.extend([
            dict(ev=k, t=v, round_idx=round_idx)
            for k, v in r.items()
        ])
    dfevs = pd.DataFrame(rows).set_index("t", verify_integrity=True)
    print(dfevs)

    return dfticks, dfevs

def create_timestamp_conversions(dfevs, anchors):
    df = dfevs.reset_index().set_index(["ev", "round_idx"])
    anchors = [
        dict(tvod=t, tdem=df.loc[k, "t"])
        for k, t in anchors.items()
    ]
    def to_dem(tvod):
        if tvod < anchors[0]["tvod"]:
            left_anchor, right_anchor = anchors[:2]
        elif tvod > anchors[-1]["tvod"]:
            left_anchor, right_anchor = anchors[-2:]
        else:
            for left_anchor, right_anchor in zip(anchors, anchors[1:]):
                if left_anchor["tvod"] <= tvod <= right_anchor["tvod"]:
                    break
            else:
                assert False, "unreachable"
        root = left_anchor["tvod"]
        span = right_anchor["tvod"] - root
        assert span > 0
        fraction = (tvod - root) / span

        root = left_anchor["tdem"]
        span = right_anchor["tdem"] - root
        assert span > 0
        return root + fraction * span

    def to_vod(tdem):
        if tdem < anchors[0]["tdem"]:
            left_anchor, right_anchor = anchors[:2]
        elif tdem > anchors[-1]["tdem"]:
            left_anchor, right_anchor = anchors[-2:]
        else:
            for left_anchor, right_anchor in zip(anchors, anchors[1:]):
                if left_anchor["tdem"] <= tdem <= right_anchor["tdem"]:
                    break
            else:
                assert False, "unreachable"
        root = left_anchor["tdem"]
        span = right_anchor["tdem"] - root
        assert span > 0
        fraction = (tdem - root) / span

        root = left_anchor["tvod"]
        span = right_anchor["tvod"] - root
        assert span > 0
        return root + fraction * span

    return to_vod, to_dem
