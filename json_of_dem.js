/* A very dirty file to extract what I need from the `dem` files */

const fs = require("fs");
const demofile = require("demofile");
const util = require('util');

/* const STEP = 1.*/
const STEP = null

const p = process.argv[2]
console.log('>   dem input path:', p);
const q0 = p.slice(0, -4) + "_events.json"
const q1 = p.slice(0, -4) + "_coords.json"
const q2 = p.slice(0, -4) + "_compo.json"
console.log('> json output paths:', q0);
console.log('                    ', q1);
console.log('                    ', q2);

var events = []
var coords = []
var compositions = []

function bind_get(val, propname) {
  if (val == null)
    return null
  if (val == undefined)
    return null

  val = val[propname]
  if (val == undefined)
    return null
  return val
}

fs.readFile(p, (err, buffer) => {
  const demoFile = new demofile.DemoFile();

  demoFile.on("tickend", _ => {

    /* Get arrays */
    var t_members = bind_get(bind_get(bind_get(demoFile, "teams"), 2), "members")
    var ct_members = bind_get(bind_get(bind_get(demoFile, "teams"), 3), "members")
    if (t_members == null || ct_members == null)
      return

    /* Get players */
    function is_valid_player(p) {
      return bind_get(p, "userId") != null &&
             bind_get(p, "name") != null &&
             bind_get(p, "isAlive") != null &&
             bind_get(p, "position") != null
    }
    t_members = t_members.filter(is_valid_player)
    ct_members = ct_members.filter(is_valid_player)
    const t_pids = t_members.map(p => bind_get(p, "userId")).sort((a, b) => a - b);
    const ct_pids = ct_members.map(p => bind_get(p, "userId")).sort((a, b) => a - b);

    /* Get players info*/
    const pinfo_of_pid = {}
    const pname_of_pid = {}
    for (const team of [t_members, ct_members]) {
      for (const p of team) {
        xyz = p.position
        id = p.userId
        isAlive = p.isAlive
        if (pinfo_of_pid[id] != undefined) {
          console.log(p, pinfo_of_pid)
          throw "oops"
        }
        pinfo_of_pid[id] = [isAlive, xyz.x, xyz.y, xyz.z]
        pname_of_pid[id] = p.name
      }
    }

    /* Save composition*/
    var compo = {
      "t": (compositions.length == 0 ? 0. : demoFile.currentTime),
      "terro": t_pids.map(pid => pname_of_pid[pid]),
      "ct": ct_pids.map(pid => pname_of_pid[pid]),
    }
    if (compositions.length == 0 ||
        !util.isDeepStrictEqual(compositions[compositions.length - 1]["terro"], compo["terro"]) ||
        !util.isDeepStrictEqual(compositions[compositions.length - 1]["ct"], compo["ct"])
    ) {
      compositions.push(compo)
      console.log(compositions[compositions.length - 1], compositions.length)
    }

    /* Save coordinates*/
    if (demoFile.currentTime >= 0 && (STEP != null ? demoFile.currentTime % STEP == 0 : true)) {
      var d = {}
      for (pid of t_pids.concat(ct_pids))
        d[pname_of_pid[pid]] = pinfo_of_pid[pid]
      coords.push([demoFile.currentTime, d])
      /* console.log(coords[coords.length - 1], coords.length)*/
    }

  });

  /* demoFile.gameEvents.on("event", e => {
   *   if (
   *     e.name.includes("item") ||
   *     e.name.includes("weapon") ||
   *     e.name.includes("grenade") ||
   *     e.name.includes("damage") ||
   *     e.name.includes("flashbang") ||
   *     e.name.includes("bomb") ||
   *     e.name == "player_spawn" ||
   *     e.name == "player_jump" ||
   *     e.name == "player_hurt" ||
   *     e.name == "player_team" ||
   *     e.name == "player_footstep" ||
   *     e.name == "player_death" ||
   *     e.name == "player_blind" ||
   *     e.name == "other_death" ||
   *     e.name == "hltv_status" ||
   *     e.name == "hltv_chase" ||
   *     e.name == "round_mvp"  ||
   *     false
   *   )
   *     return
   *   console.log(demoFile.currentTime, e)
   *   if (!(
   *     e.name == "server_cvar" ||
   *     e.name == "cs_pre_restart" ||
   *     e.name == "round_prestart" ||
   *     e.name == "round_start" ||
   *     e.name == "round_poststart" ||
   *     e.name == "begin_new_match" ||
   *     e.name == "cs_round_start_beep" ||
   *     e.name == "round_announce_match_start" ||
   *     e.name == "round_freeze_end" ||
   *     e.name == "cs_round_final_beep" ||
   *     e.name == "player_disconnect" ||
   *     e.name == "announce_phase_end" ||
   *     e.name == "cs_win_panel_round" ||
   *     e.name == "round_end" ||
   *     e.name == "player_connect" ||
   *     e.name == "player_connect_full"  ||
   *     false
   *   ))
   *     demoFile.cancel()
   * })*/

  demoFile.gameEvents.on("round_officially_ended", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    events.push({"ev": "round_officially_ended", "round_idx": idx, "t": demoFile.currentTime})
    console.log(events[events.length - 1], events.length, demoFile.teams[2].score, demoFile.teams[3].score)
  });

  demoFile.gameEvents.on("round_end", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    events.push({"ev": "round_end", "round_idx": idx, "t": demoFile.currentTime})
    console.log(events[events.length - 1], events.length, demoFile.teams[2].score, demoFile.teams[3].score)
  });

  demoFile.gameEvents.on("round_freeze_end", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    events.push({"ev": "round_freeze_end", "round_idx": idx, "t": demoFile.currentTime})
    console.log(events[events.length - 1], events.length)
  });

  demoFile.gameEvents.on("round_start", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    events.push({"ev": "round_start", "round_idx": idx, "t": demoFile.currentTime})
    console.log(events[events.length - 1], events.length, demoFile.teams[2].score, demoFile.teams[3].score)
  });

  demoFile.gameEvents.on("bomb_planted", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    events.push({"ev": "bomb_planted", "round_idx": idx, "t": demoFile.currentTime})
    console.log(events[events.length - 1], events.length)
  });

  demoFile.gameEvents.on("bomb_exploded", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    events.push({"ev": "bomb_exploded", "round_idx": idx, "t": demoFile.currentTime})
    console.log(events[events.length - 1], events.length)
  });

  demoFile.gameEvents.on("bomb_defused", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    events.push({"ev": "bomb_defused", "round_idx": idx, "t": demoFile.currentTime})
    console.log(events[events.length - 1], events.length)
  });

  demoFile.on("end", e => {
    a = demoFile.teams[2].score
    b = demoFile.teams[3].score
    console.log('> %d end %d (%d/%d)', demoFile.currentTime, a + b, a, b);
    fs.writeFileSync(q0, JSON.stringify(events))
    fs.writeFileSync(q1, JSON.stringify(coords))
    fs.writeFileSync(q2, JSON.stringify(compositions))
  });

  demoFile.on("error", e => {
    /* Server killed - do nothing - end will be called */
    console.log(e)
  });

  demoFile.parse(buffer);
});
