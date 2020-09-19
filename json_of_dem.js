const fs = require("fs");
const demofile = require("demofile");
const util = require('util');

const p = process.argv[2]
console.log('>   dem input path:', p);
const q = p.slice(0, -3) + "json"
console.log('> json output path:', q);

var j = []
var state = null
var global_player_ids = []

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
    /* if (demoFile.currentTime % 1 != 0) return DEBUG*/
    const ts = bind_get(bind_get(bind_get(demoFile, "teams"), 2), "members")
    const cts = bind_get(bind_get(bind_get(demoFile, "teams"), 3), "members")
    const coords = {}
    const local_player_ids = {}
    for (var i = 0; i < 5; i++) {
      {
        const p = bind_get(ts, i)
        xyz = bind_get(p, "position")
        id = bind_get(p, "userId")
        if (xyz == null || id == null)
          break
        local_player_ids[id] = p.name
        coords[id] = [xyz.x, xyz.y, xyz.z]
      }
      {
        const p = bind_get(cts, i)
        xyz = bind_get(p, "position")
        id = bind_get(p, "userId")
        if (xyz == null || id == null)
          break
        local_player_ids[id] = p.name
        coords[id] = [xyz.x, xyz.y, xyz.z]
      }
    }
    if (Object.keys(local_player_ids).length == 10) {
      if (global_player_ids.length == 0 ||
          !util.isDeepStrictEqual(
            global_player_ids[global_player_ids.length - 1]["ids"],
            local_player_ids
          )) {
            global_player_ids.push({
              "t0": demoFile.currentTime,
              "ids": local_player_ids,
            })
            console.log(local_player_ids)
      }

      const coords1 = []
      for (id of Object.keys(local_player_ids).map(Number).sort((a, b) => a - b))
        coords1.push(coords[String(id)])
      j.push({"ev": "tickend", "t": demoFile.currentTime, "coords": coords1})

      /* if (demoFile.currentTick >= 1) { demoFile.cancel() }*/
    }

  });

  demoFile.gameEvents.on("round_end", e => {
    console.log('> %d round_end (%d/%d)', demoFile.currentTime, demoFile.teams[2].score, demoFile.teams[3].score)
    /* if (demoFile.teams[2].score + demoFile.teams[3].score == 5) { demoFile.cancel() }*/
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
    console.log(j[j.length - 1], j.length)
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
    console.log(j)
    fs.writeFileSync(q, JSON.stringify(j));
  });
  demoFile.parse(buffer);
});
