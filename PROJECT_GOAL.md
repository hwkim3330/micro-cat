# Micro Cat product design goal

Owner: hwkim3330. A commercial, independently designed cat-shaped companion biped that keeps
the Microduck 14-axis policy interface (61 observations to 14 actions at 50 Hz) so the public
pretrained weights load unchanged.

## Why a separate repository

- `micro-rex` vendors Microduck hardware files (CC BY-SA-NC) and therefore stays noncommercial.
  Nothing in this repository may depend on it.
- `micro-x` is the T-rex line. Three appearance revisions there were rejected as not cute enough
  and the cost study showed it could not undercut a $399 complete robot. Micro Cat restarts the
  appearance from a cat, and carries over only the parts of that work that were measured and held
  up: the design-pose layout, the single-sided servo mounting, and the measurement tools.
- This repository contains no Microduck CAD, STL, body transforms, trained policies or
  hardware-derived model data. Joint pivots and axes are attributed functional measurements.

## What is carried over, and what is new

Carried over from micro-x (same owner, same toolchain):
- design pose at `qpos = 0` (straight legs), so every joint axis is world-aligned and brackets print flat;
- servo held by a U-channel in one link driving a single horn plate on the next;
- measured, not declared, joint travel (`tools/travel.py`), printability, interference and balance tools;
- the CAD-derived 14-axis MuJoCo model and the Lab/simulator web stack.

New in Micro Cat:
- round cat cranium with a short muzzle, solid printed ears, nose lens hood, button eyes;
- a tail that curls up and still works as the battery cover;
- paws whose soles reach 16 mm further back than the reference foot. This is the one change
  driven by a measurement rather than by taste: on the stock reference robot, backward tipping
  is the weakest static axis (6.7 deg, versus 11.9 forward and 23.0 lateral), and the aft support
  reach is what sets it. See `docs/DESIGN.md`.

## Acceptance and limits

- Every printable part is a valid closed CAD solid and a watertight mesh; the design pose has no
  exact-STEP overlaps; per-joint sweeps inside the measured travel are recorded.
- Servo interface dimensions are purchased-part data. Case hole pattern, cable exits and the
  voltage rail must be confirmed before ordering.
- Static CAD, simulated uprightness and ONNX loading are not walking acceptance. Acceptance needs
  measured velocity and yaw tracking, fall rates and reproducible training, then physical trials.
- The cost model uses retail servo pricing and stated assumptions. It is not a quote, and the
  recorded conclusion from micro-x still stands: 15 retail XL330-class servos alone exceed the
  price of a complete $399 robot. Anything sold here has to be justified on something other than
  beating that number on parts cost.

## Completion ledger

- [x] Rev 1 actuated cat CAD: 20 printed parts, 15 servo envelopes, battery/board/camera placement
- [ ] Measured travel, interference, printability and balance regenerated for the cat geometry
- [ ] CAD-derived 14-axis model; unchanged official weights evaluated on it
- [ ] Product page, Lab and simulator rebuilt on the cat rig
- [ ] Servo case retention and cable routing
- [ ] Printed coupons, one leg, full assembly; fit, endurance, drop and thermal tests
- [ ] Walking acceptance in simulation, then on hardware
- [ ] Supplier quotes, DFM, market and rights review before any sale
