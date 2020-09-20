import pandas as pd

# encounters (at least 2 maps) => games (at least 15 rounds) => rounds

def _toser(o):
    if isinstance(o, (list, tuple)):
        return tuple([
            _toser(v)
            for v in o
        ])
    elif isinstance(o, dict):
        return pd.Series({
            k: _toser(v)
            for k, v in o.items()
        })
    else:
        return o

def _t(t):
    h, m, s = map(float, t.split(":"))
    return h * 3600 + m * 60 + s

ENCOUNTERS = (
    dict(
        ename="2343670_big-vs-godsent-esl-pro-league-season-12-europe",
        caster_type="ESL_0",
        hltv_url="https://www.hltv.org/matches/2343670/big-vs-godsent-esl-pro-league-season-12-europe",
        vod_url="https://www.twitch.tv/videos/742919310",
        vod_framerate=60,
        vod_height=1080,
        vod_slice_start=_t("00:55:00.000"),
        vod_slice_end=_t("05:00:00.000"),
        vod_file_start_offset=_t("00:00:01.711"),
    ),
    dict(
        ename="2343922_gambit-youngsters-vs-sprout-nine-to-five-4",
        caster_type="9to5_0",
        hltv_url="https://www.hltv.org/matches/2343922/gambit-youngsters-vs-sprout-nine-to-five-4",
        vod_url="https://www.twitch.tv/videos/741603761",
        vod_framerate=50,
        vod_height=1080,
        vod_slice_start=_t("00:25:00.000"),
        vod_slice_end=_t("04:10:00.000"),
        vod_file_start_offset=_t("00:00:03.088"),
    ),
)
ENCOUNTERS = _toser({
    d["ename"]: d
    for d in ENCOUNTERS
})

GAMES=(
    dict(
        **ENCOUNTERS["2343670_big-vs-godsent-esl-pro-league-season-12-europe"],
        mname="vertigo",
        idx_in_encounter=0,
        minimap_count=2,
        round_count=34,
        vod_anchors=(

            # ("clap", "round_freeze_end", 0 + 0, occluded
            ("clap", "round_first_displacement", 0 + 1, _t("00:03:07.247")),
            ("clap", "round_first_displacement", 4 + 3, _t("00:14:48.865")),
            ("clap", "round_first_displacement", 8 + 4, _t("00:22:34.230")),
            # ("clap", "round_freeze_end", 9 + 4, occluded
            # ("clap", "round_freeze_end", 10 + 4, occluded

            ("break", "round_start", 11 + 4),
            ("clap", "round_first_displacement", 11 + 4, _t("00:31:52.254")), # 15
            # ("clap", "round_first_displacement", 12 + 7, _t("00:39:59.874")), # 19
            # ("clap", "round_first_displacement", 13 + 7, _t("00:42:14.325")), # 20
            ("clap", "round_first_displacement", 14 + 7, _t("00:44:30.311")), # 21
            # ("clap", "round_first_displacement", 22 occluded
            # ("clap", "round_first_displacement", 23 occluded
            ("clap", "round_first_displacement", 15 + 14, _t("00:59:41.221")), # 29

            ("break", "round_start", 15 + 15),

            ("clap", "round_first_displacement", 15 + 15, _t("01:06:31.281")),
            ("clap", "round_first_displacement", 15 + 16, _t("01:08:22.359")),
            ("clap", "round_first_displacement", 15 + 18, _t("01:12:36.045")),
        ),
    ),
    dict(
        **ENCOUNTERS["2343670_big-vs-godsent-esl-pro-league-season-12-europe"],
        mname="mirage",
        idx_in_encounter=1,
        minimap_count=1,
        round_count=41,
        vod_anchors=(
            # ("clap", "round_freeze_end", 1, _t("01:32:35.277")), # on overlay
            # ("clap", "round_freeze_end", 20, _t("02:16:37.233")), # on overlay
            # ("clap", "round_freeze_end", 40, _t("02:58:59.623")), # on overlay
            ("clap", "round_first_displacement", 1, _t("01:32:35.210")),
            ("clap", "round_first_displacement", 20, _t("02:16:37.166")),
            ("clap", "round_first_displacement", 40, _t("02:58:59.556")),
        ),
    ),
    dict(
        **ENCOUNTERS["2343670_big-vs-godsent-esl-pro-league-season-12-europe"],
        mname="nuke",
        idx_in_encounter=2,
        minimap_count=2,
        round_count=23,
        vod_anchors=(
            ("clap", "round_first_displacement", 1 + 0, _t("03:20:13.896")),
            ("clap", "round_first_displacement", 11 + 2, _t("03:43:58.936")),
            ("clap", "round_first_displacement", 15 + 7, _t("04:01:39.178")),
        ),
    ),

    dict(
        **ENCOUNTERS["2343922_gambit-youngsters-vs-sprout-nine-to-five-4"],
        mname="train",
        idx_in_encounter=0,
        minimap_count=1,
        round_count=42,
        vod_anchors=(
            # ("clap", "round_freeze_end", 1, _t("00:06:49.088")), # on overlay
            # ("clap", "round_freeze_end", 21, _t("00:46:08.548")), # on overlay
            # ("clap", "round_freeze_end", 41, _t("01:26:41.548")), # on overlay
            ("clap", "round_first_displacement", 1, _t("00:06:49.128")),
            ("clap", "round_first_displacement", 21, _t("00:46:08.608")),
            ("clap", "round_first_displacement", 41, _t("01:26:41.588")),
        ),
    ),
    dict(
        **ENCOUNTERS["2343922_gambit-youngsters-vs-sprout-nine-to-five-4"],
        mname="vertigo",
        idx_in_encounter=1,
        minimap_count=1,
        round_count=30,
        vod_anchors=(
            # ("clap", "round_first_displacement", 0 + 0, hard to say
            # ("clap", "round_first_displacement", 0 + 1, occluded
            ("clap", "round_first_displacement", 0 + 2, _t("01:49:44.768")),
            ("clap", "round_first_displacement", 2 + 9, _t("02:08:44.268")),
            # 5+10 is visible, but the 3 following are not
            ("clap", "round_first_displacement", 8 + 11, _t("02:26:12.508")),
            ("clap", "round_first_displacement", 13 + 12, _t("02:37:54.488")),
            ("clap", "round_first_displacement", 15 + 13, _t("02:44:57.768")),
            # ("clap", "round_first_displacement", 15 + 14, occluded
        ),
    ),
    dict(
        **ENCOUNTERS["2343922_gambit-youngsters-vs-sprout-nine-to-five-4"],
        mname="mirage",
        idx_in_encounter=2,
        minimap_count=1,
        round_count=24,
        vod_anchors=(
            # ("clap", "round_first_displacement", 0 + 0, _t("03:00:15.028")), # not in dem
            # ("clap", "round_first_displacement", 1 + 0, occluded

            ("clap", "round_first_displacement", 2 + 0, _t("03:02:01.228")),
            ("clap", "round_first_displacement", 4 + 7, _t("03:18:24.428")),
            ("clap", "round_first_displacement", 6 + 11, _t("03:31:17.688")),
            ("clap", "round_first_displacement", 8 + 15, _t("03:42:59.948")),
        ),
    ),
)
GAMES = _toser({
    (d["ename"], d["idx_in_encounter"]): d
    for d in GAMES
})

def _test():
    for g in GAMES:
        if "vod_anchors" not in g.index:
            continue
        clap_times = [
            a[3]
            for a in g.vod_anchors
            if a[0] == "clap"
        ]
        for t, u in zip(clap_times, clap_times[1:]):
            assert t + 1 < u, (g.mname, g.ename, clap_times)
        round_idxs = [
            a[2]
            for a in g.vod_anchors
        ]
        for t, u in zip(round_idxs, round_idxs[1:]):
            assert t <= u, (g.mname, g.ename, round_idxs)
        events = [
            (a[1], a[2])
            for a in g.vod_anchors
        ]
        assert len(set(events)) == len(events), (g.mname, g.ename, events)
_test()

DB_PREFIX = {
    "/": "/mnt/y/d/csgo",
    "\\": "Y:\\d\\csgo",
}
