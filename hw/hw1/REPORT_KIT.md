# HW1 report kit

Everything you need to assemble the PDF. Numbers are final for `tiles.jpg`,
Task 2 and the bonus. Part (e) numbers regenerate once the photo points are
re-recorded.

**Gradescope reminder: start each lettered part on a new page and TAG every
part.** Nine parts, plus four bonus parts, plus the AI Assistant Usage section.
An untagged part is marked zero and Gradescope will not warn you.

---

## Front matter (before Task 1)

1. The signed policy declaration sheet.
2. A section titled **AI Assistant Usage** containing the literal line
   `AI Usage: XX%`.

On the percentage: an AI assistant wrote the geometry implementations
(`vanishing_point_estimates`, `perpendicular_distance`, `analyse_families`,
`fit_conic`, `algebraic_residuals`, the bonus functions), the two helper
scripts, and this scaffold. You recorded all 44 pixel coordinates, took the
photograph, chose the features, and wrote the analysis prose. Estimate the
fraction of *your submitted solution* honestly against that split — and note
that the handout asks for the fraction, not a defence of it.

---

## Task 1(a) — the eighteen recorded points

**Tool used:** the Matplotlib interactive window (handout §3.2 names it as
acceptable), driven by `pick_points.py`, with scroll-to-zoom; every point placed
at 200–400 %.

**Table 1 — recorded points on `tiles.jpg`**

| Family | Line | Point 1 (x, y) | Point 2 (x, y) | baseline px |
|---|---|---|---|---|
| A tile rows | 1 | (579.2, 383.5) | (909.4, 508.0) | 353 |
| A tile rows | 2 | (510.6, 571.8) | (1119.9, 783.9) | 645 |
| A tile rows | 3 | (662.1, 160.2) | (773.8, 209.7) | 122 |
| B tile columns | 1 | (172.4, 450.5) | (418.1, 227.2) | 332 |
| B tile columns | 2 | (670.1, 624.4) | (705.2, 338.9) | 288 |
| B tile columns | 3 | (1446.9, 748.8) | (1118.3, 366.0) | 504 |
| C tile diagonals | 1 | (451.6, 739.3) | (1057.7, 645.1) | 613 |
| C tile diagonals | 2 | (119.8, 303.8) | (872.7, 381.9) | 757 |
| C tile diagonals | 3 | (848.7, 302.2) | (1009.9, 327.7) | 163 |

**Figure 1:** `task1_recorded_points.png` — the points drawn on the image
before anything was computed, which is the only check available on this step.

---

## Task 1(b) — vanishing point estimates

**Your prediction goes here, stated as made before computing.** Then the
numbers.

**Table 2 — three estimates per family, `tiles.jpg`**

| Family | est. from lines (1,2) | (1,3) | (2,3) | spread px |
|---|---|---|---|---|
| A tile rows | (7911.0, 3147.9) | (4512.8, 1866.6) | (5547.5, 2325.2) | 3631.7 |
| B tile columns | (756.8, −80.6) | (744.5, −69.4) | (754.0, −58.3) | 25.4 |
| C tile diagonals | (1999.3, 498.8) | (2045.7, 491.5) | (2266.5, 526.5) | 269.5 |

**Table 3 — mean vanishing points**

| Family | mean VP | distance from (800, 600) |
|---|---|---|
| A tile rows | (5990.4, 2446.6) | 5509.1 |
| B tile columns | (751.8, −69.5) | 671.2 |
| C tile diagonals | (2103.8, 505.6) | 1307.2 |

**Did the prediction hold?** The material for your account:

- The ordering is B (25 px) < C (270 px) < A (3632 px), a factor of 143.
- Spread tracks *distance to the vanishing point* monotonically: 671 → 25,
  1307 → 270, 5509 → 3632.
- The mechanism: the three lines of a family converge at their VP, so a distant
  VP means the lines are nearly parallel *in the image*. `v = l_i × l_j` is
  ill-conditioned as the angle between the two lines goes to zero — a one-pixel
  click error rotates a line by an angle that scales with 1/baseline, and that
  angular error is amplified into a positional error proportional to the
  distance to the intersection.
- A secondary contribution: line A3 has a 122 px baseline and C3 has 163 px,
  the two shortest in the set. Short baselines make the direction estimate
  noisier before the conditioning even gets to it.
- If you predicted family C (diagonals) because they are not drawn and depend
  on counting tiles, say so, say it did not hold, and say that the measurement
  hazard you worried about was real but smaller than the conditioning effect.
  Note that the diagonals *were* recorded correctly — the plot in Figure 1
  confirms it — so the counting risk simply did not materialise.

---

## Task 1(c) — collinearity

Ordered by spread, best determined first: **B (25.4) → C (269.5) → A (3631.7)**.
Worst determined: **A, tile rows**.

Line through the two best mean VPs:
`l = [−575.062, 1352.06, 526234]`

**Collinearity residual = 264.94 px** (perpendicular distance from the mean VP
of family A to that line).

**Why the distance and not the determinant.** The numbers to quote:

```
det[v1 v2 v3] with each v_i = [x, y, 1]^T        = 3.89e+05
the same determinant after scaling v3 by 1e6     = 3.89e+11
```

Same three points. Same picture. A determinant six orders of magnitude larger.
Each `v_i` is a homogeneous vector fixed only up to scale, and the determinant
is linear in each column, so rescaling one column rescales the determinant —
which means the determinant's *magnitude* measures nothing about the geometry.
It answers "is this exactly zero?" and nothing else, and with real measurements
it is never exactly zero. The perpendicular distance divides by ‖(a, b)‖, so
every scale cancels and what is left is a length in pixels — a quantity you can
compare against the image, against your click precision, and against the same
number computed on a different photograph.

**What the number says about the claim.** 264.94 px against vanishing points
lying 671, 1307 and 5509 px from the image centre, the worst of them 5509 px
out — so the residual is about 4.8 % of the distance to the point being tested.
Write one sentence saying that this is consistent with the three vanishing
points being collinear to within recording error, and one sentence naming what
would have falsified it: a residual that stayed large as recording precision
improved, or one comparable to the spacing between the vanishing points
themselves.

---

## Task 1(d) — the vanishing line

`l_v = join(VP B, VP C) = [−575.062, 1352.06, 526234]`
normalized to a² + b² = 1: `[−0.391393, 0.920224, 358.16]`

All three vanishing points fall outside the frame (0 of 3 inside), which is why
two panels are needed.

**Figure 2:** `task1_vanishing.png` — near view and wide view, nine lines
extended, three vanishing points, `l_v`.

**The degenerate case.** Not "the vanishing point is far away" — that is an
ordinary pair of large numbers. The case is the limit just beyond: two lines of
a family that come out *exactly* parallel in the image. Then the family's
vanishing point is an **ideal point**, `l_i × l_j` returns `[a, b, 0]`, and a
Cartesian implementation that solves for the intersection has to divide by a
zero determinant and must special-case it. The cross product handles it with no
special case at all — it just returns a perfectly good homogeneous 3-vector
whose third entry happens to be zero.

**Where a test is still needed.** At the moment you go *back* to Cartesian
coordinates. `dehom()` still has to check whether the third entry is negligible,
and — this is the point — that check cannot be "is `x3` small", because a
homogeneous vector is fixed only up to scale; it has to be made relative to
`|x1|` and `|x2|`, which is exactly what the supplied `dehom()` does. So the
difficulty never lived in the intersection. It lives at the boundary where you
leave projective space and demand a finite answer, which is the only place the
distinction between a finite point and an ideal point means anything.

---

## Task 1(e) — my own photograph

**Media:** `myphoto.jpg` (4624 × 2084), a tiled floor shot obliquely.

**Table 4 - recorded points on `myphoto.jpg` (4624 x 2084)**

| Family | Line | Point 1 (x, y) | Point 2 (x, y) | baseline px |
|---|---|---|---|---|
| A  first family | 1 | (2440.1, 882.2) | (3146.4, 856.4) | 707 |
| A  first family | 2 | (2185.3, 1704.6) | (3298.0, 1711.1) | 1113 |
| A  first family | 3 | (3114.1, 640.3) | (3768.8, 592.0) | 656 |
| B  second family | 1 | (3207.7, 1182.2) | (3085.1, 463.0) | 730 |
| B  second family | 2 | (3643.1, 424.3) | (4607.4, 1714.3) | 1611 |
| B  second family | 3 | (2559.4, 504.9) | (2501.4, 669.4) | 174 |
| C  third family | 1 | (3207.7, 1182.2) | (3768.8, 595.2) | 812 |
| C  third family | 2 | (4230.0, 375.9) | (3933.3, 808.1) | 524 |
| C  third family | 3 | (3117.4, 650.0) | (3626.9, 417.8) | 560 |

**Table 5 - three estimates per family, `myphoto.jpg`**

| Family | est. (1,2) | (1,3) | (2,3) | spread px |
|---|---|---|---|---|
| A  first family | (-17005.0, 1592.5) | (-2719.6, 1070.7) | (-10322.0, 1631.5) | 14296.4 |
| B  second family | (2911.7, -554.1) | (2918.6, -513.8) | (2926.0, -535.0) | 42.8 |
| C  third family | (4871.1, -558.0) | (4178.8, 166.3) | (4462.7, 36.9) | 1001.9 |

**Table 6 - mean vanishing points, `myphoto.jpg`** (centre = (2312, 1042))

| Family | mean VP | distance from centre |
|---|---|---|
| A  first family | (-10015.5, 1431.6) | 12333.7 |
| B  second family | (2918.8, -534.3) | 1689.1 |
| C  third family | (4504.2, -118.3) | 2480.3 |

**Figure 3:** `task1e_recorded_points.png` — the eighteen points on the floor
grout, checked before computing.

Ordered by spread: **B (42.8) -> C (1001.9) -> A (14296.4)**. Worst determined:
family A.

`l_v = join(VP B, VP C) = [-416.024, 1585.43, 2.06137e+06]`
normalized to a^2 + b^2 = 1: `[-0.253812, 0.967254, 1257.62]`
All three vanishing points fall outside the frame, so two panels again.

**Figure 4:** `task1e_vanishing.png`

**COLLINEARITY RESIDUAL = 5184.37 px**

| image | residual | ratio |
|---|---|---|
| `tiles.jpg` (rendered, exact pinhole) | 264.94 px | 1x |
| `myphoto.jpg` (real lens) | 5184.37 px | **19.6x worse** |

The prediction of Task 1(b) is reproduced here: spread again tracks distance to
the vanishing point monotonically (1689 -> 42.8, 2480 -> 1002, 12334 -> 14296).

**Be honest about which effect dominates.** The residual is 19.6x worse, but
the largest single contribution here is not the lens — it is the conditioning of
family A. Those three grout lines run within about 4.5 degrees of each other in
the image (directions -2.1, +0.3 and -4.2 degrees), so the family is very nearly
parallel on the sensor and its vanishing point lands 12334 px away, well outside
a 4624 px frame. The three pairwise estimates then disagree by 14296 px, and the
worst-determined point is the very one whose distance to the line you are
reporting. Say this explicitly: the photograph was shot with one tile direction
nearly parallel to the image plane, and that choice of viewpoint, not the lens,
sets the scale of the number. This is also a near-miss of the degenerate case
named in part (d) — a family whose vanishing point is on the verge of being an
ideal point — which is worth pointing out as an accidental demonstration of it.

**The lens argument.** `tiles.jpg` is a *rendering*,
produced by an exact pinhole projection, so the collinearity of vanishing points
holds there to within your click precision alone. A real camera has a lens with
**radial distortion**: barrel or pincushion, strongest away from the optical
axis. Under radial distortion a straight line in the world no longer images to a
straight line, so the two points you record on it do not define the line's true
image, each family's three lines fail to be concurrent by more than click error,
and the vanishing points move — most of all for lines near the frame edge.
Perspective projection maps lines to lines; a distorted lens does not, and
collinearity of vanishing points is a consequence of the projective model that
distortion breaks.

**Telling distortion apart from careless recording.** The distinguishing test is
that lens distortion is *systematic and structured* while carelessness is
*random*. Concretely, any one of these:

- Re-record the same eighteen points a second time. Carelessness gives you a
  different residual each time, scattering about zero; distortion gives you
  substantially the same residual, because the error is a fixed function of
  position in the frame.
- Record points near the centre of the frame only. Radial distortion falls off
  toward the optical axis, so the residual should shrink markedly; recording
  error does not care where in the frame you are.
- Fit a line to the many points along one long grout line rather than two. Under
  distortion the residuals of that fit are a smooth, systematically signed curve
  (all bowing one way); under carelessness they are random in sign.

---

## Task 2(a) — the eight rim points

**Table 6 — recorded points on the outer rim of `plate.jpg`**

| # | x | y |  | # | x | y |
|---|---|---|---|---|---|---|
| 1 | 515.4 | 592.5 | | 5 | 1111.9 | 559.0 |
| 2 | 665.3 | 479.3 | | 6 | 965.2 | 707.4 |
| 3 | 848.7 | 418.6 | | 7 | 778.6 | 775.9 |
| 4 | 1022.6 | 425.0 | | 8 | 539.3 | 760.0 |

**Figure 4:** `task2_recorded_points.png`

---

## Task 2(b) — the fitted conic

Singular values of the design matrix:
`2.72e+06, 7.109e+05, 7.011e+04, 349.7, 53.22, 7.365e-04`

Note the last one is five orders below the next: the null direction is
well separated, which is what makes the fit trustworthy.

**C, scaled so ‖C‖_F = 1:**

```
[  4.4e-07    3.1e-07   -5.3853e-04 ]
[  3.1e-07    1.27e-06  -1.00968e-03 ]
[ -5.3853e-04 -1.00968e-03  9.9999869e-01 ]
```

**max_i |x_iᵀ C x_i| = 4.783e−04**, inside the 10⁻³–10⁻⁴ band the handout
predicts.

**What it measures, and why it is not a distance.** It is the *algebraic*
residual: how far each recorded point is from satisfying the conic equation,
not how far it sits from the curve in the image. `xᵀCx` is a quadratic form in
pixel coordinates, so its units are pixels² times the units of C — and since C
was fixed by an arbitrary normalisation (‖C‖_F = 1), the number carries no
geometric length at all. Two consequences worth stating: the same point at the
same geometric distance from the curve gives different `xᵀCx` depending where on
the conic it sits (the form grows faster where the curve is sharply bent), and
without the stated ‖C‖_F = 1 convention the number could be made anything at
all, since `xᵀCx` is linear in C. The geometric quantity would be the distance
from the point to the nearest point of the curve, which has no closed form and
is not what this fit minimises.

---

## Task 2(c) — classification

Coefficients rescaled so a² + b² + c² = 1:

```
a =  0.2991140    b =  0.4134745    c =  0.8599824
d = -727.2084     e = -1363.4235    f =  675172.0893
```

**Discriminant b² − 4ac = −0.857970** → negative → **ellipse**.
(The handout's expected check is "near −0.86". ✓)

Neither circle constraint survives:
`b = 0.4135` (a circle needs 0), `a − c = −0.5609` (a circle needs 0).

**Why a camera should not be expected to preserve them.** The object is a circle
*in the world plane*. The image is related to that plane by a projective
transformation H, and a conic transforms as `C ↦ H^-T C H^-1`. That congruence
mixes all six coefficients together — every entry of the new C is a combination
of every entry of the old one, with weights set by H. So "b = 0 and a = c" is
not a property the curve carries around with it; it is a statement about the
coefficients in one particular Euclidean frame, and it holds only for the
similarity transformations (rotation, uniform scale, translation) that preserve
angles. A camera in general position is not a similarity — it is a full
projectivity, with a vanishing line at finite distance — so there is no reason
for those two relations to be preserved, and they are not.

**What did survive.** Being a conic at all: `xᵀCx = 0` maps to `xᵀCx = 0`, so
the degree-2 algebraic form is preserved. Being *nondegenerate*: H is
invertible, so rank 3 stays rank 3. Being an **ellipse** specifically: the whole
circle lies on the camera's side of the vanishing line, so no point of it is
sent to infinity and the closed bounded curve stays closed and bounded — had the
plane's vanishing line cut the circle, it would have imaged as a hyperbola.
Tangency survived too, which is what Figure 5 checks. What is lost is everything
metric: radius, centre (the image of the circle's centre is *not* the centre of
the image ellipse), and the equality of all diameters.

---

## Task 2(d) — the tangent

At p = (515.4, 592.5):
`l = C p = [−1.2878032e−04, −9.7189636e−05, 1.2419972e−01]`

```
p^T C p = 2.414848e-04
l^T p   = 2.414848e-04
difference = 0.000000e+00
```

**Figure 5:** `task2_conic_and_tangent.png` — the fitted conic, eight points and
the tangent, with a zoomed panel showing the line touching at p without crossing.

**Why they must agree, and why that verifies nothing.** `l = Cp` by definition,
so `lᵀp = (Cp)ᵀp = pᵀCᵀp`, and C is symmetric by construction — the xy, x and y
coefficients are split evenly across the off-diagonal pairs — so `Cᵀ = C` and
`lᵀp = pᵀCp`. The two expressions are *the same expression*, rewritten. It is an
identity that holds for **any** symmetric 3×3 matrix and **any** vector p,
whether or not C came from a good fit, whether or not p lies anywhere near the
plate, whether or not the fit converged. Feeding it a random symmetric matrix
and a random point reproduces the agreement exactly. It confirms that C is
symmetric and that your matrix multiplication is correct, and it tells you
nothing whatever about whether the conic follows the rim. The check that does
carry information is the visual one: the zoomed panel showing the line touching
the curve at p and not crossing it.

---

## Bonus — all four parts

**(a)** Aiming line `l(α) = [−sin α, cos α, 0]^T`. Worked example values:
α = 0° → `[0, 1, 0]`; α = 45° → `[−0.707107, 0.707107, 0]`; α = 90° → `[−1, 0, 0]`.
α appears in the first two entries only; the third is 0 because every line
through the origin satisfies a·0 + b·0 + c = 0, forcing c = 0. Note α and
α + 180° give the same line up to the factor −1 — the line has no direction, and
that is the whole basis of part (b).

Subtended intervals: **target [69.4440°, 82.8750°]**, **armour [38.6598°, 84.2894°]**.
The target's interval is contained in the armour's, but containment alone is not
enough — you must show the armour is met *first*. For every α in the target's
interval the ray crosses y = 4 at x between **0.5000 and 1.5000**, all inside the
armour's span [0.4, 5.0], and y = 4 is crossed before y = 8. Hence no direct shot.

Meeting the aiming line with `l∞ = [0,0,1]^T` at α = 45° gives
`[0.707107, 0.707107, 0]` — an **ideal point**, namely `[cos α, sin α, 0]^T`,
the ray's own direction. `dehom()` returns `None`. Part (d) reuses it.

**(b)** At α = 250° the meet with the target's line is **(2.9118, 8.0000)**, and
the naive test reports **a hit** — 250° points down and to the left, away from
everything. The diagnosis is in (a): the aiming line has no direction, so it
extends backwards through the target as readily as forwards. Missing condition:
with d = (cos α, sin α) and q the meet, require **d·q > 0**. Here
**d·q = −8.5134 < 0**, so the corrected test reports **no hit**. The inequality
is strict because d·q = 0 puts the meet on the line through the player
perpendicular to d — at zero range, not in front of the player — which is not a
forward hit.

**(c)** Wall x = 7 normalized: `l = [−1, 0, 7]^T`.

```
M =  [ -1   0  14 ]        M @ M =  [ 1  0  0 ]
     [  0   1   0 ]                 [ 0  1  0 ]
     [  0   0   1 ]                 [ 0  0  1 ]
```

‖M² − I‖_F = **0.00e+00**. M² = I had to hold because reflecting twice in the
same line returns every point to where it started: a reflection is its own
inverse, so it is an involution.

**(d)** Target centre (2, 8) → mirror image **(12.0000, 8.0000)**.
Aim at it: **α = 33.690068°**.

| leg | check | value | verdict |
|---|---|---|---|
| 1 | crosses y = 4 at x = | 6.0000 | armour spans [0.4, 5.0] → **clears** |
| 1 | strikes wall at | (7.0000, 4.6667) | wall spans y ∈ [0, 6] → **hits** |
| — | incoming direction | [0.832050, 0.554700, 0] | ideal point |
| — | reflected by M | [−0.832050, 0.554700, 0] | third entry stays 0 |
| 2 | lands on y = 8 at x = | 2.000000 | bar spans [1, 3] → **hits centre** |
| 2 | error from bar centre | 3.11e−15 | — |

The third entry of the direction stays 0, so M's translation column (the 14)
multiplies zero and drops out — what comes back is a pure direction. A direction
*is* an ideal point, which is why one matrix serves for reflecting both points
and directions, and why part (a) was worth doing.

**Figure 6:** `bonus_bank_shot.png` — the two-leg path on the arena.
