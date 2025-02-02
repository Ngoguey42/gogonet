"""The light datas are all manually hard coded into this file. The rest sits on the filesystem
at `DB_PREFIX`.
"""

import pandas as pd

DB_PREFIX = {
    "/": "/mnt/y/d/csgo",
    "\\": "Y:\\d\\csgo",
}

def _toser(o):
    """Recursively convert a constant to a more convenient type"""
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

OVERLAYS = (
    dict(
        oname="ESL_0",
        approx_minimap_slice=(slice(18, 18 + 383), slice(38, 38 + 352)),
        minimap_transform=dict(
            # Calculated from 2343670_big-vs-godsent-esl-pro-league-season-12-europe@01:37:13.535
            # fit errors (pixels): rmse=1.46, max=4.07, evicted-coords:XANTARES@y/.joinZehn@y/.jointiziaN@x/.jointabseN@y
            mirage=dict(scale=0.08338703293273778, xoffset=265.4881278781594, yoffset=122.56393671444916),

            # Calculated from 2343666_vitality-vs-fnatic-esl-pro-league-season-12-europe@00:08:38.940
            # fit errors (pixels): rmse=1.04, max=2.86, evicted-coords:Brollan@x/.joinapEX@y/.joinKRIMZ@x/.joinapEX@x
            inferno=dict(scale=0.07558824979751766, xoffset=176.97981616249112, yoffset=295.7595512186543),

            # Calculated from 2343666_vitality-vs-fnatic-esl-pro-league-season-12-europe@01:48:16.833
            # fit errors (pixels): rmse=1.67, max=3.28, evicted-coords:JW@x/.joinRpK@x/.joinKRIMZ@y/.joinZywOo@y
            dust2=dict(scale=0.07815224939987528, xoffset=232.1693759733323, yoffset=273.6822446009504),

            # Calculated from 2343663_natus-vincere-vs-og-esl-pro-league-season-12-europe@00:36:08.046
            # fit errors (pixels): rmse=0.44, max=0.87, evicted-coords:NBK-@x/.joins1mple@x/.joinBoombl4@y/.joinmantuu@y
            train=dict(scale=0.07826002473919963, xoffset=223.27199797631818, yoffset=192.40853282004218),

            # Calculated from 2343663_natus-vincere-vs-og-esl-pro-league-season-12-europe@01:51:15.343
            # fit errors (pixels): rmse=0.44, max=1.06, evicted-coords:electronic@y/.joinelectronic@x/.joinvalde@y/.joinISSAA@x
            overpass=dict(scale=0.06624024362529557, xoffset=357.50342728501727, yoffset=136.03716372498346),
        ),
    ),
    dict(
        oname="9to5_0",
        approx_minimap_slice=(slice(26, 26 + 362), slice(43, 43 + 362)),
        minimap_transform=dict(
            # Calculated from 2343922_gambit-youngsters-vs-sprout-nine-to-five-4@00:28:48.175
            # fit errors (pixels): rmse=0.59, max=1.57, evicted-coords:dycha@x/.joinHObbit@x/.joininterz@x/.joinSpiidi@y
            train=dict(scale=0.075646902113509, xoffset=228.57316667628038, yoffset=206.8117503179393),

            # Calculated from 2343922_gambit-youngsters-vs-sprout-nine-to-five-4@02:33:38.265
            # fit errors (pixels): rmse=0.34, max=0.69, evicted-coords:HObbit@y/.joinHObbit@x/.joinnafany@x/.joinsnatchie@x
            vertigo=dict(scale=0.09597378245608361, xoffset=357.8209561344714, yoffset=175.74522826990432),

            # Calculated from 2343922_gambit-youngsters-vs-sprout-nine-to-five-4@03:03:52.214
            # fit errors (pixels): rmse=0.57, max=1.33, evicted-coords:nafany@y/.joinsh1ro@x/.joindenis@x/.joininterz@y
            mirage=dict(scale=0.07176271207124993, xoffset=271.4584511310774, yoffset=145.39809505939385),
        ),
    )
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
        vod_framerate=59.94006023456136,
        vod_height=1080,
        vod_slice_start=_t("00:55:00.000"),
        vod_slice_end=_t("05:00:00.000"),
        vod_file_start_offset=_t("00:00:01.711"),
        first_keyframe_tvod=_t("00:00:01.711"),
        first_keyframe_tav=_t("00:00:01.581"),
        total_games=3,
        # kept_game_indices=(0, 1, 2),
    ),
    dict(
        ename="2343922_gambit-youngsters-vs-sprout-nine-to-five-4",
        oname="9to5_0",
        hltv_url="https://www.hltv.org/matches/2343922/gambit-youngsters-vs-sprout-nine-to-five-4",
        vod_url="https://www.twitch.tv/videos/741603761",
        vod_framerate=50.0,
        vod_height=1080,
        vod_slice_start=_t("00:25:00.000"),
        vod_slice_end=_t("04:10:00.000"),
        vod_file_start_offset=_t("00:00:03.088"),
        first_keyframe_tvod=_t("00:00:03.088"),
        first_keyframe_tav=_t("00:00:02.960"),
        total_games=3,
        # kept_game_indices=(0, 1, 2),
    ),

    # Second batch******************************************************************************* **
    dict(
        ename="2343666_vitality-vs-fnatic-esl-pro-league-season-12-europe",
        oname="ESL_0",
        hltv_url="https://www.hltv.org/matches/2343666/vitality-vs-fnatic-esl-pro-league-season-12-europe",
        vod_url="https://www.twitch.tv/videos/741690460",
        vod_framerate=59.94006057443512,
        vod_height=1080,
        vod_slice_start=_t("04:15:00.000"),
        vod_slice_end=_t("06:35:00.000"),
        vod_file_start_offset=_t("00:00:01.340"),
        first_keyframe_tvod=_t("00:00:01.340"),
        first_keyframe_tav=_t("00:00:01.219"),
        total_games=2,
        # kept_game_indices=(0, 1),
    ),
    dict(
        ename="2343663_natus-vincere-vs-og-esl-pro-league-season-12-europe",
        oname="ESL_0",
        hltv_url="https://www.hltv.org/matches/2343663/natus-vincere-vs-og-esl-pro-league-season-12-europe",
        vod_url="https://www.twitch.tv/videos/739846263",
        vod_framerate=59.94005742125734,
        vod_height=1080,
        vod_slice_start=_t("04:45:00.000"),
        vod_slice_end=_t("06:55:00.000"),
        vod_file_start_offset=_t("00:00:00.033"),
        first_keyframe_tvod=_t("00:00:02.018"),
        first_keyframe_tav=_t("00:00:01.868"),
        total_games=3,
        # kept_game_indices=(0, 1),
    ),
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
            ("clap", "round_first_displacement", 3 + 0, _t("01:36:10.025")),
            # ("clap", "bomb_planted", 3 + 0, _t("01:37:57.649")),
            ("clap", "round_first_displacement", 20, _t("02:16:37.166")),
            ("clap", "round_first_displacement", 40, _t("02:58:59.556")),
        ),
        partial_minimap_rounds={0, 1, 10, 11, 13, 15, 16, 18, 22, 25, 27, 30, 33, 38},
        players_order=(
            "maden", "STYKO", "Farlig", "Zehn", "kRYSTAL",
            "syrsoN", "XANTARES", "k1to", "tabseN", "tiziaN",
        ),
        annotated_vod_frame=_t("01:37:13.535"),
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
        # On round 0 a player has an `undefined` minimap text
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
        annotated_vod_frame=_t("00:28:48.175"),
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
            "faveN", "dycha", "snatchie", "Spiidi", "denis",
            "interz", "sh1ro", "nafany", "HObbit", "Ax1Le",
        ),
        annotated_vod_frame=_t("02:33:38.265"),
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
        players_order=(
            "dycha", "snatchie", "Spiidi", "denis", "faveN",
            "interz", "sh1ro", "nafany", "HObbit", "Ax1Le",
        ),
        annotated_vod_frame=_t("03:03:52.214"),
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
        partial_minimap_rounds={5, 7, 8, 10, 14, 15, 17, 22, 23, 25},
        players_order=(
            "misutaaa", "ZywOo", "apEX", "RpK", "shox",
            "flusha", "JW", "KRIMZ", "Golden", "Brollan",
        ),
        annotated_vod_frame=_t("00:08:38.940"),
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
        partial_minimap_rounds={0, 2, 4, 6, 7, 12, 13, 17, 19, 22},
        players_order=(
            "flusha", "KRIMZ", "Brollan", "Golden", "JW",
            "misutaaa", "ZywOo", "shox", "apEX", "RpK",
        ),
        annotated_vod_frame=_t("01:48:16.833"),
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
        partial_minimap_rounds={2, 4, 6, 8, 12, 13, 14, 15, 20, 23, 24},
        players_order=(
            "electronic", "Perfecto", "Boombl4", "flamie", "s1mple",
            "Aleksib", "valde", "mantuu", "NBK-", "ISSAA",
        ),
        annotated_vod_frame=_t("00:36:08.046"),
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
        partial_minimap_rounds={0, 4, 5, 9, 11, 12, 14, 19, 20, 21, 23},
        players_order=(
            "ISSAA", "valde", "Aleksib", "NBK-", "mantuu",
            "Perfecto", "Boombl4", "flamie", "s1mple", "electronic",
        ),
        annotated_vod_frame=_t("01:51:15.343"),
    ),

)
GAMES = _toser({
    (d["ename"], d["idx_in_encounter"]): d
    for d in GAMES
})
def _inflate():
    for e in ENCOUNTERS.values:
        e["kept_game_indices"] = []
        e["game_indices_of_mname"] = {}
        e["games"] = []
    for g in GAMES.values:
        i = g.idx_in_encounter
        m = g.mname
        e = ENCOUNTERS[g.ename]
        e["kept_game_indices"].append(i)
        assert m not in e["game_indices_of_mname"]
        e["game_indices_of_mname"][m] = i
        e["games"].append(g)
    e["games"] = tuple(sorted(e.games, key=lambda g: g.idx_in_encounter))
    e["kept_game_indices"] = tuple(sorted(e.kept_game_indices))

_inflate()


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
