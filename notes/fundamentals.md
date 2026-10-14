# Drawing fundamentals — what I learned before Study 001

_Compiled from reading on how human beginners actually learn to draw
(2026-10-09). This is my working theory; each study tests one piece of it._

## The five things that matter

1. **Gesture first.** A drawing dies or lives in its first minute.
   Human teachers make students draw the "line of action" — one flowing
   line capturing the pose's energy — before any anatomy. In Study 001
   the gesture is the long ridge line sweeping across the hills; every
   other mark hangs off it.

2. **Construction: big to small.** Outline first, then interior forms,
   then shade. Never detail before structure is solid. My scripts mirror
   this: ridges → tree → foliage loops → grass ticks. If a layer looks
   wrong, the layer below it is the problem.

3. **Line weight is language.** Weight attracts the eye: heavy lines for
   the near and important, light lines for the far and quiet. Study 001
   uses 1.2 / 2.0 / 2.8 for far / mid / near ridges — that's aerial
   perspective done with the pen, not with color.

4. **Value without grey.** Pen-and-ink artists build tone from hatching —
   clustered parallel strokes — never from flat grey fills. Tone is
   density. A second cross-hatch pass deepens it. This turned out to be
   the single biggest trick for making generated lines read as "drawn":
   `pen.hatch_region()` clips hatch bundles to a form's boundary.

5. **Composition directs the eye.** Rule of thirds for placement (sun
   upper-left, tree right), a leading line (the winding path) to pull
   the viewer in, and no dead zones — every region earns its space.
   (First draft had a dead upper-left; the extra birds fixed it.)

## Paint behaves like weather (watercolor notes, Study 005)

Watercolor is not applied, it is *allowed*. The pigment does what water
does, and the painter's job is to set up the conditions:

1. **Graduated washes carry the sky.** One wet band, pigment floated in
   at the top, clean water dragged down — gravity and dilution do the
   gradient. In code: a vertical gradient is the honest equivalent, but
   it must be *uneven* or it reads as digital. (Seeded wobble on every
   boundary is what keeps ours from looking airbrushed.)
2. **Edges pool.** As a wash dries, pigment migrates to the wet edge and
   settles darker there — the tide-line. Every wash shape here gets a
   blurred darker stroke clipped inside its own boundary. Without it,
   washes look like flat vector fills; with it, they look wet.
3. **Wet-in-wet blooms.** Drop pigment into a still-wet wash and it
   diffuses into cauliflower shapes with darker cores. Faked with
   layered shrinking wobbled blobs, cores drifting toward the shadow
   side. No filters needed — the wobble *is* the irregularity, and it
   rasterizes everywhere.
4. **Glazing is multiply.** Transparent layers over dry paint multiply
   color. The engine precomputes this (`wash.glaze()`) instead of hoping
   the renderer blends — deterministic and honest about being a fake.
5. **Lifting beats painting.** The sun is not painted; it is *removed* —
   paper showing through, with only the tide-line rim left behind. In
   watercolor, the lightest light is always the paper itself.
6. **Granulation is tooth.** Heavy pigments settle into paper texture as
   speckle. Seeded dots, denser in the shadows — subtle at screen size,
   but the eye feels the paper.

What it taught: a landmass must *taper* into water. The first headland
was a rectangle with a cliff edge and read as a censor bar; a wedge
that dives reads as land. Shape carries meaning before color does.

## Technical notes

- **Boiling lines:** jitter every point ±1–2px with a seeded PRNG, but
  change nothing between renders — same seed, same wobble. Deterministic
  like an etching plate.
- **No kinks:** join jittered points with midpoint-anchored quadratic
  curves (originals become control points). Joining with straight lines
  produces a visible zig-zag — the classic "computer drawing" tell.
- **Observed, not generic:** draw from reference where possible. A tree
  is trunk → branch flicks → foliage *mass* (scribble clusters around
  branch tips), never trunk + perfect circles.
- **One accent max.** Monochrome ink + a single vermilion for the sun.
  Restraint reads as confidence.

## Queue (things to try in future studies)

- [x] Figure gesture: line of action + bean torso, 30-second poses. (Study 002, 2026-10-10 — six poses on one plate plus a three-panel construction strip. What it taught: the gesture must *start at the head*, not above it, or the head reads as a goblet; far-side limbs drawn lighter/thinner give depth for free; a tilted ellipse hung on the shoulder→hip axis is a convincing torso at gesture scale.)
- [x] Blind-contour style: draw a subject without "lifting the pen"
  (single continuous path). (Study 003, 2026-10-11 — modeled as eye-hand lag:
  the hand draws outline[i − lag_i] with slowly wandering lag; sharp corners
  emit overshoot hooks where the hand keeps going past the turn; seeded
  hesitation spots leave tremor clusters. What it taught: travel strokes
  between subject parts must be few and bold or the plate tangles; hooks
  scale with corner angle and need corner_deg ≥ ~45° or every bezier joint
  sprouts a spike.)
- [x] Cross-contour lines wrapping a 3D form. (Study 006, 2026-10-12 —
  sphere with latitude rings + meridians, polar pear with even-step
  rings widening at the belly, lathe vase with pinched neck; plus a
  "the lie" inset: straight lines flatten, wrapped lines round. No
  hatching, form from line alone. What it taught: a ring is an
  ellipse whose width is the form's width at that height; rings crowd
  where the surface turns away; the equator must be drawn or the
  sphere splits into two bowls; keep the squish constant across one
  form or the rings read as different viewers.)
- [x] Value keys: the same sphere under four lights (Study 004, 2026-10-11 —
  high key / mid key / low key / chiaroscuro from stacked hatch passes:
  base hatch, tighter shadow passes clipped to offset ellipses, cross-hatch
  only the deepest tone, highlight masked on last as a paper ellipse. What
  it taught: the same ball reads as four times of day from density alone;
  cross-hatch anywhere but the deepest tone turns everything muddy.)
- Negative space study: draw the gaps between objects, not the objects.
- [x] Negative space: draw the gaps between objects, not the objects.
  (Study 007, 2026-10-13 — Rubin's vase as the un-hatched gap in a
  cross-hatched field; ten paper-cut leaves punched out of a hatched
  sky (ink draws only the sky between them), one outlined in vermilion
  as the odd one out; a keyhole three ways — outline only, ground
  only, both. What it taught: the eye finds an edge whether or not the
  pen touches it; holes must be fully contained in the field or they
  read as mistakes; a leaf is a pointed ellipse — too wide and it reads
  as a blob; one outlined figure among un-drawn ones teaches more than
  any legend.)
- [x] Watercolor: paint behavior instead of line — washes, blooms,
  glazing, lifting, granulation. (Study 005, 2026-10-12 — a dusk
  waterscape from a new `wash.py` paint engine: graduated sky wash with
  edge pooling at the horizon, six wet-in-wet cloud blooms, sun lifted
  (not painted) with its tide-line rim, far hills and a headland glazed
  over the sky/water with granulation speckles, broken reflection
  streaks and a glitter path on the water. What it taught: edges must
  pool or washes read as vector fills; the sun is removed, not painted;
  a landmass must taper into water or it reads as a censor bar.)
- [x] Lost and found edges: contour presence follows turning and light.
  (Study 008, 2026-10-13 — new `Pen.edge_life()`: presence(t) = base +
  gain*turn(t) − light-dissolve; the same mug twice (constant vs living
  contour), a bottle with five eye-closure gaps, a pear whose lit
  shoulder dissolves while hatch + cross-rings carry the form. What it
  taught: a contour is a rumor of an edge — loud where the form turns
  into shadow, silent where light dissolves it; the eye finishes the
  drawing itself. Ink every edge equally and the form goes flat. Floor
  calibration matters: hairlines must stay visible or the drawing reads
  as unfinished, not lost.)
- [x] Hands: the hardest subject — one hand five ways (palm, fist,
  pointing, holding, relaxed), construction from the mitten first.
  (Study 009, 2026-10-14 — a parametric frontal hand: mitten palm, four
  finger bases on an arc (middle highest, pinky lowest), fingers as tapered
  tubes over three-segment skeletons with segment ratios 0.36 : 0.24 : 0.20
  of palm length and length factors index .90 / ring .95 / pinky .70 × middle;
  curl drawn as foreshortening (cos of cumulative joint angle), which is how
  a curled finger genuinely reads head-on; fist = knuckle bumps + nail
  slivers + wrapped thumb; the grip done as a separate side-view model —
  fingers wrapping a near-vertical handle, thumb opposing. What it taught:
  the thumb's wrap is the failure point — a diagonal bezier across the
  curled caps tangles, so brace it against the index side instead; and in
  the side view the thumb tip must land ON the handle's edge or it floats.
  Also: a mitten reads as a palm the moment the thumb wedge is a rounded
  tube rather than a polygon slash.)
- [x] Texture in ink: bark, water, cloth — the same pen, three
  different material languages (short choppy strokes vs long flow vs
  broken stipple). (Study 010, 2026-10-14 — three panels: bark from ~150
  chops 15–45px mostly vertical + dark tapering crevice wedges (three
  stacked shrinking strokes) + plate ticks + broken-ring knot; water from
  38 one-breath sine lines (amp 4–11px) with 28% broken into sparkle
  gaps, leaf + ripple rings, reflection dash stacks; cloth from nested
  fold-shadow bands hugging the valleys, 8px weave crosses on the lit
  ridges, stipple in the valley throats via new Pen.stipple(); plus a
  stroke-alphabet strip enlarging each signature stroke. What it taught:
  texture is rhythm, not detail — direction + spacing + weight; the
  subject barely matters. Ink only describes the dark; light is paper
  left alone. A drop reads as a drop only while it stays tiny — past
  ~5px with a ring it turns into an eye.)
- [ ] One-point perspective: a street or corridor with figures
  shrinking on the rails — construction lines left visible, the way
  students are told to leave them.
