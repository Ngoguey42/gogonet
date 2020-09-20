import json
from pprint import pprint
import os

import numpy as np
import pandas as pd

import constants as con

def segment_rounds(evs):
    # State machine to identify full rounds with a sound chain of events
    # A round have at least: `round_start`, `round_freeze_end`, `round_end` and `round_officially_ended`
    # bomb events might occur after `round_officially_ended`
    # Some rounds might be squeezed because of missing `round_start` etc..
    # Some events might be simultaneous (like bomb event and end of round)
    rounds = []
    latest_timings = {}
    latest_unfreeze_ridx = None # Only trust round idx at unfreeze

    def not_bigger(a, b):
        if a is None: return True
        if b is None: return True
        return not (a > b)

    def flush(tail=False):
        nonlocal latest_timings, latest_unfreeze_ridx
        t = latest_timings
        # print("Flush!", latest_unfreeze_ridx, t)
        if (t.get("round_start") is not None and
            t.get("round_freeze_end") is not None and
            t.get("round_end") is not None and

            # Tolerate missing official end if last round
            ((t.get("round_officially_ended") is not None) or (tail is True))
        ):
            assert latest_unfreeze_ridx is not None
            assert not_bigger(t.get("round_start"), t.get("round_freeze_end")), t
            assert not_bigger(t.get("round_freeze_end"), t.get("bomb_planted")), t
            assert not_bigger(t.get("bomb_planted"), t.get("bomb_defused")), t
            assert not_bigger(t.get("bomb_planted"), t.get("bomb_exploded")), t
            assert not_bigger(t.get("bomb_defused"), t.get("round_end")), t
            if "bomb_defused" in t:
                assert "bomb_planted" in t
            if "bomb_exploded" in t:
                assert "bomb_planted" in t
                assert "bomb_defused" not in t
            if rounds:
                assert latest_unfreeze_ridx > rounds[-1]["round_idx"]
                assert t["round_start"] >= rounds[-1]["round_end"]
            if "round_officially_ended" in t:
                del t["round_officially_ended"]
            rounds.append(dict(
                round_idx=latest_unfreeze_ridx,
                **t
            ))
        latest_timings = {}
        latest_unfreeze_ridx = None

    for ev in evs:
        if ev["ev"] == "round_start":
            flush()
        if ev["ev"] == "round_freeze_end" and ev["t"] == latest_timings.get("round_end"):
            # Round freeze end simultaneous to end of game on some servers. Let's ignore that event
            continue
        if ev["ev"] in latest_timings is not None:
            flush()
        latest_timings[ev["ev"]] = ev["t"]
        if ev["ev"] == "round_freeze_end":
            latest_unfreeze_ridx = ev["round_idx"]
    flush(tail=True)

    return rounds

def path_of_json(ename, egidx):
    prefix = con.DB_PREFIX[os.path.sep]
    mname = con.GAMES[(ename, egidx)].mname
    return os.path.join(prefix, f"{ename}_{egidx}_{mname}.json")

def path_of_vod(ename, egidx):
    prefix = con.DB_PREFIX[os.path.sep]
    mname = con.GAMES[(ename, egidx)].mname
    return os.path.join(prefix, f"{ename}.mp4")

def time_totxt(v):
    sign = "" if (v >= 0) else "-"
    v = abs(v)
    h = v // 3600
    m = (v - h * 3600) // 60
    s = (v - h * 3600 - m * 60)
    return f"{sign}{h:02.0f}:{m:02.0f}:{s:06.3f}"

def load_json(ename, egidx):
    path = path_of_json(ename, egidx)
    # print("reading", path)
    j = open(path).read()

    # print("parsing json")
    j = json.loads(j)
    # print("slicing json")
    l = [ev for ev in j if ev["ev"] == "tickend"]

    # print("making df")
    rows = []
    for ev in l:
        for pid, (x, y, z, alive) in ev["pinfo"].items():
            if not alive:
                continue
            rows.append(dict(
                x=x, y=y, z=z, t=ev["t"], pid=pid,
            ))
    dfticks = pd.DataFrame(rows).set_index(["t", "pid"], verify_integrity=True)
    # print(dfticks)

    rows = []
    for r in segment_rounds([ev for ev in j if ev["ev"] != "tickend"]):
        # print("**********************************************************************")
        # pprint(r)
        round_idx = r.pop("round_idx")
        rows.extend([
            dict(ev=k, t=v, round_idx=round_idx)
            for k, v in r.items()
        ])
    dfevs = pd.DataFrame(rows) #.set_index("t", verify_integrity=True)
    # print(dfevs)

    return dfticks, dfevs

def create_timestamp_conversions(dfevs, anchors):
    df = dfevs.reset_index().set_index(["ev", "round_idx"])

    def get_tdem(ev, round_idx):
        """Find the event in df"""
        if ev == "round_first_displacement":
            ev = "round_freeze_end" # TODO: Find the time displacement between those 2 events
        return float(df.loc[(ev, round_idx), "t"])

    def create_lerp_on_floats(xleft, xright, yleft, yright):
        """Linear interpolation and extrapolation"""
        rootx = xleft
        spanx = xright - rootx
        assert spanx > 0
        rooty = yleft
        spany = yright - rooty
        assert spany > 0
        def lerp(x):
            fractionx = (x - rootx) / spanx
            return rooty + fractionx * spany
        return lerp

    def yield_3_by_3(l):
        for i in range(len(l) - 2):
            yield l[i:i+3]

    anchors = [["start"]] + list(anchors) + [["end"]]
    tdem_intervals, tvod_intervals, to_dems, to_vods = [], [], [], []
    for a0, a1, a2 in yield_3_by_3(anchors):
        tag = (a0[0], a1[0], a2[0])
        if tag == ("start", "clap", "clap"):
            # ]-inf; a1], lerp on a1/a2
            left, right = a1, a2
            to_dem = create_lerp_on_floats(
                left[3], right[3],
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
            )
            to_vod = create_lerp_on_floats(
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
                left[3], right[3],
            )
            tdem_start = -np.inf
            tdem_end = get_tdem(a1[1], a1[2])
            tvod_start = -np.inf
            tvod_end = a1[3]
        elif tag == ("clap", "clap", "clap"):
            # [a0; a1], lerp on a0/a1
            left, right = a0, a1
            to_dem = create_lerp_on_floats(
                left[3], right[3],
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
            )
            to_vod = create_lerp_on_floats(
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
                left[3], right[3],
            )
            tdem_start = get_tdem(a0[1], a0[2])
            tdem_end = get_tdem(a1[1], a1[2])
            tvod_start = a0[3]
            tvod_end = a1[3]
        elif tag == ("clap", "clap", "break"):
            # [a0; break], lerp on a0/a1
            left, right = a0, a1
            to_dem = create_lerp_on_floats(
                left[3], right[3],
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
            )
            to_vod = create_lerp_on_floats(
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
                left[3], right[3],
            )
            tdem_start = get_tdem(a0[1], a0[2])
            tdem_end = get_tdem(a2[1], a2[2])
            tvod_start = a0[3]
            tvod_end = to_vod(tdem_end) # extrapolated from the current lerp
        elif tag == ("clap", "break", "clap"):
            continue # covered by previous case
        elif tag == ("break", "clap", "clap"):
            # [break; a1], lerp on a1/a2
            left, right = a1, a2
            to_dem = create_lerp_on_floats(
                left[3], right[3],
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
            )
            to_vod = create_lerp_on_floats(
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
                left[3], right[3],
            )
            tdem_start = get_tdem(a0[1], a0[2])
            tdem_end = get_tdem(a1[1], a1[2])
            tvod_start = to_vods[-1](tdem_start) # extrapolated from the previous lerp
            tvod_end = a1[3]
        elif tag == ("clap", "clap", "end"):
            # [a0; +inf[, lerp on a0/a1
            left, right = a0, a1
            to_dem = create_lerp_on_floats(
                left[3], right[3],
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
            )
            to_vod = create_lerp_on_floats(
                get_tdem(left[1], left[2]), get_tdem(right[1], right[2]),
                left[3], right[3],
            )
            tdem_start = get_tdem(a0[1], a0[2])
            tdem_end = +np.inf
            tvod_start = a0[3]
            tvod_end = +np.inf
        else:
            assert False, tag
        # print("> ", tag)
        if tdem_start != -np.inf:
            assert tdem_intervals[-1][1] == tdem_start, (tdem_intervals[-1][1], tdem_start)
            assert tvod_intervals[-1][1] == tvod_start, (tvod_intervals[-1][1], tvod_start)
        tdem_intervals.append((tdem_start, tdem_end))
        tvod_intervals.append((tvod_start, tvod_end))
        to_dems.append(to_dem)
        to_vods.append(to_vod)

    assert tdem_intervals[0][0] == -np.inf
    assert tdem_intervals[-1][1] == np.inf
    assert tvod_intervals[0][0] == -np.inf
    assert tvod_intervals[-1][1] == np.inf

    def to_dem(tvod):
        """Not monotonic because of breaks, surjective
        """
        for i, (start, end) in enumerate(tvod_intervals):
            if start <= tvod <= end:
                return to_dems[i](tvod)
        assert False, "unreachable"

    def to_vod(tdem):
        """Monotonic, injective
        """
        for i, (start, end) in enumerate(tdem_intervals):
            if start <= tdem <= end:
                return to_vods[i](tdem)
        assert False, "unreachable"

    return to_vod, to_dem
