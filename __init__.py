"""Welcome! Read the README first.

# Annex to the README (A bit disorganized)

The maps handled are vertigo mirage nuke train overpass inferno dust2.

Each player has a `digit` assigned to him to identify him on the minimap.

There is no (strong) need to train on segments with a hidden minimap because of the shift invariance of the network.

Another strategy for the minimap would have been to locate static elements and point them on the minimap.

The stylish `vods` that use 2 minimaps to represent the different floors on `vertigo` or `nuke` have not been co-registered
and will not be supervised on this task, but they will be on the final coordinate prediction.

<!-- ******************************************************************************************* -->

## Looking Back on Step 3 and 4. How precise should be the annotations?
There are 2 types of manual annotations in this project:
- Identifying the right __time__ in Step 4
- Pointing the right continuous __coordinates__ in Step 3.

I made small errors in both of them:
- With the process described in step 3 I can ascertain that my timings are correct to a 75ms precision from one another, but they might all be skewed in the same direction.
- When manually fitting the disks on the minimap if feels like the maximum error is between ½ and 1 pixel.

When correlating the minimap annotations with the world coordinates from the `dem` file (using linear algebra) __both__ types of errors worsen the result. But I was still able to contain both types of errors:
- Coordinates errors are dampened by the fact that I click several icons
- Timings errors are dampened by the fact that I didn't count the coordinates 4 coordinates moving the most in the time frame around the screeshot. Maybe I should have taken frames where players are spreaded and don't move.

If my imprecisions follow a gaussian, the network will know how to generalise but it may slow down the training and lead to coarse decision boundaries.

If my imprecisions are all skewed in the same direction:
- The shift-invariant parts of the network will be fooled
- The network converting to world coordinates will learn to shift accordingly. (But i'm still unsure what method to use to implement the unit conversion in the network).

Finally let's convert the problem into tangible units.
A player runs at 250 world-unit per second (with a knife in hand), and a minimap pixel has a size of 10 to 15 world-units.
If `250 unit/s == 9 km/h` then `250 unit/s = 2.5 m/s` then `1 unit = 1 cm` then `10cm ≤ 1 minimap-pixel ≤ 15cm`.

A `10 cm` (`1 minimap-pixel`) error in `csgo` is a certain death for a professional player but it is most acceptable for the task as hand.

<!-- ******************************************************************************************* -->

## Why the network has to say is there is a minimap or not
The reason is a bit convoluted:
Since the players may overlap each other on the minimap, a prediction may require informations from previous frames.
This implies that a _sequence model_ is needed
and since such a model requires an initial _hidden state_ for the initial frame where the minimap appears (or reappears).
The act of _resetting_ the _hidden state_ when the minimap reappears has to be automated within the program, hence the minimap visibility prediction.
(TODO: What if I let the LSTM solve this problem?)

<!-- ******************************************************************************************* -->

## train test split
One broadcaster               will be kept for testing - the goal being to generalize to unknown UI layouts.
One map   of each broadcaster will be kept for testing.
One round of each game        will be kept for testing.
The network will not be able to generalise to unknown maps.

<!-- ******************************************************************************************* -->

## Why the network has to say where the minimap is
This will be useful to reduce the number of convolutions by focusing where the minimap has been located.

<!-- ******************************************************************************************* -->

## Terminology used throughout the project
- `vod` for `Video On Demand` - the video files.
- `dem` for `DEMo file` - the CSGO replay files.
- `overlay` is the UI layout specific to a broadcast.
- `encounter` is a collection of games (usually best of 3). One encounter <=> One video.
- `game` is a collection of rounds (usually best of 30).
- A `round` has at least a start, a freeze_end, a stop. Only the round where the minimap isn't
  hidden from `freeze_end` to `stop` are kept for training and testing (roughly 2/3 of them).

### Timings
- `tvod` and `tdem` are timings on the `vod` and the `dem`.
  Note that a `tvod` doesn't represent a specific vod frame, it has to be rounded first.
  The same goes for `tdem` and the dem ticks.
- `to_tvod` and `to_tdem` are the conversion functions for the 2 types of timings. See `tools.py`
  for the implementation.
- `tvod` is the timing used by `avidmux` and `opencv`
- `tav` is the timing of the `vod` using the `av` library.

### DataFrames (per game)
- `evdf` is the pandas DataFrame containing the cleaned events. It is computed from a
  `*_events.json`.
- `codf` is the massive pandas DataFrame containing the players coordinates 128 ticks/s.
  It is computed from a `*_coords.json`
- `compodf` is the pandas DataFrame containing the composition of the teams throughout to
  connection and deconnections of players. Is is computed from a `*_compo.json`
- `iconsdf` is the pandas DataFrame containg the coordinates of the players of the minimap.
  It is computed from a geojson.

### DataFrames (all games)
- `rdv` is the pandas DataFrame containing the rounds from all games. It is computed from the
  `evdf` DataFrames.

<!-- ******************************************************************************************* -->

# TODOs
- How to make `codf` lighter and quicker to load?
- Extract: Players' death (what is event `other_death`?) to avoid those moments on training/testing

## TODO CNN
- Augmentation is needed but not because of the size of the dataset (I bet I will do less than 1 epoch will be necessary) but:
  1. Need shift augmentation because static overlay elements will be overfitted by the deepest kernels.
  2. Augmenting the data may improve the generalisation to other overlays
  What about non-discrete augmentation? Scale minimap, <1 shifts?

- How to pass shared hidden state to `seqnet` ? conv and Global max pooling ? Or detected rect of the minimap?
- What tasks should and should not be performed by `convnet`, same for `seqnet`?
- How many training step? 1 might not be possible. Training the `seqnet` after might
  allow the precomputation of the shared hidden states.
- Should the `seqnet` have any concept of elevation?
- Which set weights are specialized for one maps? Some meta-learning magic?
- Some triplet loss magic to enforce some constraints of the SHS or the conv kernel?
  (Could constrain conv some weights to be similar, per-map)

Supervision ideas for `convnet`:
- player count in "super" pixels for each stride, directly from shared hidden state
- predict vector and proba, directly from shared hidden state, for each large-pixel, for each index.
  But kill loss (or grad) if one of the pred cannot be made because players are close. (player count will still help generalise)
- a mask-rcnn like instanciation
- the z histogram history of players, for eachs stride, for each pixel. (Not possible on the nuke/vertigo that havent been annotated (yet?))

## TODO README Step 5
- Talk about receptive field
- Talk about augmentation
- Introduce `convnet` `seqnet` and the shared hidden state


"""
