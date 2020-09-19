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
        vod_anchors={
            # ("round_freeze_end", 1): _t("00:03:07.281"),
            # ("round_freeze_end", ): _t(""),
            # ("round_freeze_end", ): _t(""),
        },
    ),
    dict(
        **ENCOUNTERS["2343670_big-vs-godsent-esl-pro-league-season-12-europe"],
        mname="mirage",
        idx_in_encounter=1,
        minimap_count=1,
        round_count=41,
        vod_anchors={
            ("round_freeze_end", 1): _t("01:32:35.277"),
            ("round_freeze_end", 20): _t("02:16:37.233"),
            ("round_freeze_end", 40): _t("02:58:59.623"),
        },
    ),
    dict(
        **ENCOUNTERS["2343670_big-vs-godsent-esl-pro-league-season-12-europe"],
        mname="nuke",
        idx_in_encounter=2,
        minimap_count=2,
        round_count=23,
    ),

    dict(
        **ENCOUNTERS["2343922_gambit-youngsters-vs-sprout-nine-to-five-4"],
        mname="train",
        idx_in_encounter=0,
        minimap_count=1,
        round_count=42,
        vod_anchors={
            ("round_freeze_end", 1): _t("00:06:49.088"),
            ("round_freeze_end", 21): _t("00:46:08.548"),
            ("round_freeze_end", 41): _t("01:26:41.548"),
        },
    ),
    dict(
        **ENCOUNTERS["2343922_gambit-youngsters-vs-sprout-nine-to-five-4"],
        mname="vertigo",
        idx_in_encounter=1,
        minimap_count=1,
        round_count=30,
    ),
    dict(
        **ENCOUNTERS["2343922_gambit-youngsters-vs-sprout-nine-to-five-4"],
        mname="mirage",
        idx_in_encounter=2,
        minimap_count=1,
        round_count=24,
    ),
)
GAMES = _toser({
    (d["ename"], d["idx_in_encounter"]): d
    for d in GAMES
})

DB_PREFIX = {
    "/": "/mnt/y/d/csgo",
    "\\": "Y:\\d\\csgo",
}
