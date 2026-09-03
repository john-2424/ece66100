# ECE 661 — Homework 1

Shrikrishna Bhagirath Rajule (srajule@purdue.edu)

Vanishing points and the vanishing line (Task 1), a circle photographed from an
angle (Task 2), and the optional bank-shot bonus.

## How to run

```bash
conda env create -f environment.yml     # first time only
conda activate ece661
python hw1_ShrikrishnaRajule.py
```

That single command runs Task 1, Task 2 and the bonus in order, prints every
number reported in the PDF, and writes each figure to the working directory.

### Where the images have to be

The script reads from `hw1_images/`, which must sit next to
`hw1_ShrikrishnaRajule.py`:

```
hw1_ShrikrishnaRajule.py
hw1_images/
    tiles.jpg       # provided with the assignment
    plate.jpg       # provided with the assignment
    myphoto.jpg     # my own photograph, for Task 1(e)
```

To read them from somewhere else, set the environment variable the skeleton
already provides — no edit to the source is needed:

```bash
ECE661_HW1_DATA=/path/to/images python hw1_ShrikrishnaRajule.py
```

`tiles.jpg` and `plate.jpg` are not included in this submission, as Section 7.3
of the handout instructs. `myphoto.jpg` is my own work and is included.

## Files

| File | What it is |
| --- | --- |
| `hw1_ShrikrishnaRajule.py` | The submission. Safe to import: all work is in functions, all calls are behind `if __name__ == '__main__':`. |
| `environment.yml` | The conda environment, exported with `conda env export`. |
| `pick_points.py` | The tool I used to record pixel coordinates (see below). Not part of the graded solution. |
| `wire_points.py` | Wires recorded coordinates into the submission file and audits them. Not part of the graded solution. |

## Outputs

Running the script writes:

| Figure | Part |
| --- | --- |
| `task1_recorded_points.png` | 1(a) — the eighteen recorded points, checked before computing |
| `task1_vanishing.png` | 1(d) — two-panel plot: nine lines, three vanishing points, `l_v` |
| `task1e_recorded_points.png` | 1(e) — recorded points on my own photograph |
| `task1e_vanishing.png` | 1(e) — the same two-panel plot on my own photograph |
| `task2_recorded_points.png` | 2(a) — the eight rim points |
| `task2_conic_and_tangent.png` | 2(d) — fitted conic, points and tangent, with a zoom on the tangency |
| `bonus_bank_shot.png` | Bonus (d) — the two-leg path on the arena |

## Seeds

None. Nothing in the solution is random: the vanishing points come from cross
products, the conic from a deterministic SVD, and the bonus is closed form.
Re-running the script reproduces every number exactly. The only quantities that
would change between runs are the recorded pixel coordinates themselves, and
those are fixed literals in the source.

## How the pixel coordinates were recorded

Section 3.2 of the handout permits any tool that reports the cursor position and
names Matplotlib's interactive window as one of them. I used that, through
`pick_points.py`, which is the Matplotlib window with a click handler that writes
the coordinates to a file instead of my copying them by hand. It supports
scroll-to-zoom about the cursor, and I recorded every point at 200–400 % as the
handout advises. Right-click undoes a misplaced point.

```bash
python pick_points.py hw1_images/tiles.jpg   18 tiles_points.txt
python pick_points.py hw1_images/plate.jpg    8 rim_points.txt
python pick_points.py hw1_images/myphoto.jpg 18 photo_points.txt
python wire_points.py                        # writes them into the submission
```

`wire_points.py` also audits the recorded points before anything depends on
them: it checks that each family's three lines really do converge on a common
point, and flags a family in which one line-pair disagrees with the other two by
orders of magnitude, which is the signature of a miscounted diagonal.

## Compute setup

| | |
| --- | --- |
| OS | Windows 11 (24H2), AMD64 |
| CPU | Intel Core i7-8750H (6 cores / 12 threads) |
| Environment | conda env `ece661`, Python 3.11 |
| Libraries | numpy, matplotlib, pillow — no OpenCV, as the handout requires |
| Runtime | under 10 seconds end to end; no GPU is used or needed |

## References

1. Course notes, ECE 661 Computer Vision, Lecture 2: homogeneous coordinates,
   meet and join, ideal points and the line at infinity, conics and tangents.
   Purdue University, Fall 2026.
2. R. Hartley and A. Zisserman, *Multiple View Geometry in Computer Vision*,
   2nd ed., Cambridge University Press, 2004, ch. 2.
