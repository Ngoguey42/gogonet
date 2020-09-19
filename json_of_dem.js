const fs = require("fs");
const demofile = require("demofile");
const util = require('util');

const STEP = 1.

const p = process.argv[2]
console.log('>   dem input path:', p);
const q = p.slice(0, -3) + "json"
console.log('> json output path:', q);

var j = []
var state = null
var pname_of_pid = {}

function bind_get(val, propname) {
  if (val == null)
    return null
  return val[propname]
}

function bind_set(val, k, v) {
  if (v !== null)
    val[k] = v
}

fs.readFile(p, (err, buffer) => {
  const demoFile = new demofile.DemoFile();

  demoFile.on("tickend", e => {
    if (demoFile.currentTime % STEP != 0)
      return

    const ts = bind_get(bind_get(bind_get(demoFile, "teams"), 2), "members")
    const cts = bind_get(bind_get(bind_get(demoFile, "teams"), 3), "members")
    const pinfo = {}
    for (team of [ts, cts]) {
      for (var i = 0; i < 5; i++) {
        const p = bind_get(team, i)
        xyz = bind_get(p, "position")
        id = bind_get(p, "userId")
        isAlive = bind_get(p, "isAlive")
        if (xyz == null || id == null || isAlive == null)
          continue
        if (pname_of_pid[id] == undefined)
          pname_of_pid[id] = p.name
        if (pname_of_pid[id] != p.name) {
          console.log(p.id, p.name, pname_of_pid)
          throw "oops"
        }
        pinfo[id] = [xyz.x, xyz.y, xyz.z, isAlive]
      }
    }
    if (Object.keys(pinfo).length > 0) {
      j.push({"ev": "tickend", "t": demoFile.currentTime, "pinfo": pinfo})
    }

  });

  demoFile.gameEvents.on("round_end", e => {
    console.log('> %d round_end (%d/%d)', demoFile.currentTime, demoFile.teams[2].score, demoFile.teams[3].score)
  });

  demoFile.gameEvents.on("round_freeze_end", e => {
    const old_state = state;
    state = "moving";
    if (old_state == null || old_state == "start") {
      idx = demoFile.teams[2].score + demoFile.teams[3].score
      j.push({"ev": "round_freeze_end", "round_idx": idx, "t": demoFile.currentTime})
      console.log(j[j.length - 1], j.length)
    }
  });

  demoFile.gameEvents.on("round_start", e => {
    old_state = state;
    state = "start";
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    j.push({"ev": "round_start", "round_idx": idx, "t": demoFile.currentTime})
    console.log(j[j.length - 1], j.length, demoFile.teams[2].score, demoFile.teams[3].score)
  });

  demoFile.gameEvents.on("bomb_planted", e => {
    old_state = state;
    state = "planted";
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    j.push({"ev": "bomb_planted", "round_idx": idx, "t": demoFile.currentTime})
    console.log(j[j.length - 1], j.length)
  });

  demoFile.gameEvents.on("bomb_exploded", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    j.push({"ev": "bomb_exploded", "round_idx": idx, "t": demoFile.currentTime})
    console.log(j[j.length - 1], j.length)
  });

  demoFile.gameEvents.on("bomb_defused", e => {
    idx = demoFile.teams[2].score + demoFile.teams[3].score
    j.push({"ev": "bomb_defused", "round_idx": idx, "t": demoFile.currentTime})
    console.log(j[j.length - 1], j.length)
  });

  demoFile.on("end", e => {
    a = demoFile.teams[2].score
    b = demoFile.teams[3].score
    console.log('> %d end %d (%d/%d)', demoFile.currentTime, a + b, a, b);
    fs.writeFileSync(q, JSON.stringify(j));
  });

  demoFile.on("error", e => {
    /* Server killed - do nothing - end will be called */
    console.log(e)
  });

  demoFile.parse(buffer);
});
