import pandas as pd

# encounters (at least 2 maps) => games (at least 15 rounds) => rounds

def _toser(o):
    if isinstance(o, (list, tuple)):
        return tuple([_toser(v) for v in o])
    if isinstance(o, (set, frozenset)):
        return frozenset(_toser(v) for v in o)
    elif isinstance(o, dict):
        return pd.Series({k: _toser(v) for k, v in o.items()})
    else:
        return o

def _t(t):
    h, m, s = map(float, t.split(":"))
    return h * 3600 + m * 60 + s

# ESL vertigo mirage nuke
# ESL train overpass inferno dust2

OVERLAYS = (
    dict(
        oname="ESL_0",
        approx_minimap_slice=(slice(18, 18 + 383), slice(38, 38 + 352)),
    ),
    dict(
        oname="9to5_0",
        approx_minimap_slice=(slice(26, 26 + 362), slice(43, 43 + 362)),
    ),
)
def _inflate():
    for o in OVERLAYS:
        sli, slj = o["approx_minimap_slice"]
        o["approx_minimap_height"] = sli.stop - sli.start
        o["approx_minimap_width"] = slj.stop - slj.start
_inflate()
OVERLAYS = _toser({
    d["oname"]: d
    for d in OVERLAYS
})

ENCOUNTERS = (
    # First batch******************************************************************************** **
    dict(
        ename="2343670_big-vs-godsent-esl-pro-league-season-12-europe",
        oname="ESL_0",
        hltv_url="https://www.hltv.org/matches/2343670/big-vs-godsent-esl-pro-league-season-12-europe",
        vod_url="https://www.twitch.tv/videos/742919310",
        vod_framerate=60,
        vod_height=1080,
        vod_slice_start=_t("00:55:00.000"),
        vod_slice_end=_t("05:00:00.000"),
        vod_file_start_offset=_t("00:00:01.711"),
        total_games=3,
        kept_game_indices=(0, 1, 2),
    ),
    dict(
        ename="2343922_gambit-youngsters-vs-sprout-nine-to-five-4",
        oname="9to5_0",
        hltv_url="https://www.hltv.org/matches/2343922/gambit-youngsters-vs-sprout-nine-to-five-4",
        vod_url="https://www.twitch.tv/videos/741603761",
        vod_framerate=50,
        vod_height=1080,
        vod_slice_start=_t("00:25:00.000"),
        vod_slice_end=_t("04:10:00.000"),
        vod_file_start_offset=_t("00:00:03.088"),
        total_games=3,
        kept_game_indices=(0, 1, 2),
    ),

    # Second batch******************************************************************************* **
    dict(
        ename="2343666_vitality-vs-fnatic-esl-pro-league-season-12-europe",
        oname="ESL_0",
        hltv_url="https://www.hltv.org/matches/2343666/vitality-vs-fnatic-esl-pro-league-season-12-europe",
        vod_url="https://www.twitch.tv/videos/741690460",
        vod_framerate=60,
        vod_height=1080,
        vod_slice_start=_t("04:15:00.000"),
        vod_slice_end=_t("06:35:00.000"),
        vod_file_start_offset=_t("00:00:01.340"),
        total_games=2,
        kept_game_indices=(0, 1),
    ),

    dict(
        ename="2343663_natus-vincere-vs-og-esl-pro-league-season-12-europe",
        oname="ESL_0",
        hltv_url="https://www.hltv.org/matches/2343663/natus-vincere-vs-og-esl-pro-league-season-12-europe",
        vod_url="https://www.twitch.tv/videos/739846263",
        vod_framerate=60,
        vod_height=1080,
        vod_slice_start=_t("04:45:00.000"),
        vod_slice_end=_t("06:55:00.000"),
        vod_file_start_offset=_t("00:00:00.033"),
        total_games=3,
        kept_game_indices=(0, 1),
    ),

    # dict(
    #     ename="",
    #     oname="",
    #     hltv_url="",
    #     vod_url="",
    #     # vod_framerate=,
    #     # vod_height=,
    #     # vod_slice_start=_t("::00.000"),
    #     # vod_slice_end=_t("::00.000"),
    #     # vod_file_start_offset=_t("00:00:0"),
    # ),
    # dict(
    #     **ENCOUNTERS[""],
    #     mname="",
    #     idx_in_encounter=,
    #     minimap_count=,
    #     round_count=,
    #     # vod_anchors=(),
    # ),
)
ENCOUNTERS = _toser({
    d["ename"]: d
    for d in ENCOUNTERS
})

GAMES=(
    # First batch ******************************************************************************* **
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
        # partial_minimap_rounds={0, 13, 16, 29, 33},
        partial_minimap_rounds={0, 13, 14, 16, 22, 30, 32},
        players_order=(
            "tiziaN", "k1to", "tabseN", "XANTARES", "syrsoN",
            "STYKO", "maden", "kRYSTAL", "Farlig", "Zehn",
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
        # partial_minimap_rounds={0, 8, 13, 14, 15, 19, 20, 23, 25, 27, 29, 30, 31, 33, 35, 38, 40},
        partial_minimap_rounds={0, 1, 10, 11, 13, 15, 16, 18, 22, 25, 27, 30, 33, 38},
        players_order=(
            "maden", "STYKO", "Farlig", "Zehn", "kRYSTAL",
            "syrsoN", "XANTARES", "k1to", "tabseN", "tiziaN",
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
            # ("clap", "round_first_displacement", 15 + 6, _t("03:59:33.002")),
            ("clap", "round_first_displacement", 15 + 7, _t("04:01:39.178")),
        ),
        # partial_minimap_rounds={
        #     5, 6, 9, 11, 12, 14, 15, 18, 19, 21, 22,
        #     0, # On round 0a player has an `undefined` minimap text
        # },
        partial_minimap_rounds={0, 6, 7, 11, 16, 18, 19, },
        players_order=(
            "syrsoN", "tiziaN", "k1to", "tabseN", "XANTARES",
            "Farlig", "maden", "kRYSTAL", "STYKO", "Zehn",
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
        partial_minimap_rounds={5, 18, 19, 23, 32, 35, },
        players_order=(
            "interz", "HObbit", "nafany", "sh1ro", "Ax1Le",
             "dycha", "snatchie", "denis", "faveN", "Spiidi",
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
        partial_minimap_rounds={1, 17, 18, 24, 29},
        players_order=(
            "interz", "sh1ro", "nafany", "HObbit", "Ax1Le",
            "faveN", "dycha", "snatchie", "Spiidi", "denis",
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
        partial_minimap_rounds={1, 9, 12},
        # partial_minimap_rounds={},
        players_order=(
            "dycha", "snatchie", "Spiidi", "denis", "faveN",
            "interz", "sh1ro", "nafany", "HObbit", "Ax1Le",
        ),
    ),

    # Second batch ****************************************************************************** **
    dict(
        **ENCOUNTERS["2343666_vitality-vs-fnatic-esl-pro-league-season-12-europe"],
        mname="inferno",
        idx_in_encounter=0,
        minimap_count=1,
        round_count=29,
        vod_anchors=(
            ("clap", "round_first_displacement", 0 + 0, _t("00:04:46.925")),
            ("clap", "round_first_displacement", 8 + 4, _t("00:30:12.333")),
            ("clap", "round_first_displacement", 15 + 13, _t("01:09:18.460")),
        ),
        # partial_minimap_rounds={7, 8, 10, 14, 17, 23, 28},
        partial_minimap_rounds={5, 7, 8, 10, 14, 15, 17, 22, 23, 25},
        players_order=(
            "misutaaa", "ZywOo", "apEX", "RpK", "shox",
            "flusha", "JW", "KRIMZ", "Golden", "Brollan",
        ),
    ),
    dict(
        **ENCOUNTERS["2343666_vitality-vs-fnatic-esl-pro-league-season-12-europe"],
        mname="dust2",
        idx_in_encounter=1,
        minimap_count=1,
        round_count=24,
        vod_anchors=(
            ("clap", "round_first_displacement", 0 + 1, _t("01:27:39.810")),
            ("clap", "round_first_displacement", 6 + 5, _t("01:48:05.801")),
            ("clap", "round_first_displacement", 8 + 15, _t("02:13:34.912")),
        ),
        # partial_minimap_rounds={0, 1, 2, 7, 8, 9, 10, 11, 14, 18, 19, 20, 22, 23},
        partial_minimap_rounds={0, 2, 4, 6, 7, 12, 13, 17, 19, 22},
        players_order=(
            "flusha", "KRIMZ", "Brollan", "Golden", "JW",
            "misutaaa", "ZywOo", "shox", "apEX", "RpK",
        ),
    ),
    dict(
        **ENCOUNTERS["2343663_natus-vincere-vs-og-esl-pro-league-season-12-europe"],
        mname="train",
        idx_in_encounter=0,
        minimap_count=1,
        round_count=26,
        vod_anchors=(
            ("clap", "round_first_displacement", 0 + 0, _t("00:02:49.953")),
            ("clap", "round_first_displacement", 7 + 4, _t("00:21:17.409")),
            ("clap", "round_first_displacement", 15 + 10, _t("00:51:16.590")),
        ),
        # partial_minimap_rounds={4, 12, 13, 14, 25},
        partial_minimap_rounds={2, 4, 6, 8, 12, 13, 14, 15, 20, 23, 24},
        players_order=(
            "electronic", "Perfecto", "Boombl4", "flamie", "s1mple",
            "Aleksib", "valde", "mantuu", "NBK-", "ISSAA",
        ),
    ),
    dict(
        **ENCOUNTERS["2343663_natus-vincere-vs-og-esl-pro-league-season-12-europe"],
        mname="overpass",
        idx_in_encounter=1,
        minimap_count=1,
        round_count=24,
        vod_anchors=(
            ("clap", "round_first_displacement", 1 + 0, _t("01:12:39.439")),
            ("clap", "round_first_displacement", 4 + 6, _t("01:32:52.350")),
            ("clap", "round_first_displacement", 13 + 8, _t("02:00:36.262")),
        ),
        # partial_minimap_rounds={4, 10, 12, 14, 18, 20, 21, 22, 23},
        partial_minimap_rounds={0, 4, 5, 9, 11, 12, 14, 19, 20, 21, 23},
        players_order=(
            "ISSAA", "valde", "Aleksib", "NBK-", "mantuu",
            "Perfecto", "Boombl4", "flamie", "s1mple", "electronic",
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

_is_set = False
def _setup_pretty_print():
    global _is_set
    if _is_set:
        return
    _is_set = True

    import pandas as pd
    import numpy as np

    pd.set_option('display.width', 500)
    pd.set_option('display.max_colwidth', 260)
    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    pd.set_option('display.max_columns', 25)
    pd.set_option('display.max_rows', 1000)

    np.set_printoptions(linewidth=250, threshold=999999999999, suppress=True)

_setup_pretty_print()
