#!/usr/bin/env python

##  hw1_skeleton.py

"""
This is the skeleton for Homework 1 of ECE 661, Computer Vision, Fall 2026.

The framework is written for you: reading the two supplied images, drawing the
overlays, saving the figures.  What is left for you to write is the geometry, and
every place that needs your work is marked TODO.

Everything in this homework is built out of four facts from Lecture 2:

    the line through two points            l  =  x1 cross x2
    the point where two lines meet         x  =  l1 cross l2
    a conic                                x^T C x  =  0
    the tangent to C at a point p on it    l  =  C p

Rename this file to hw1_<FirstName><LastName>.py before you submit it.  Note that
the work is all inside functions and that the calls at the bottom sit behind the
usual __main__ guard.  Keep it that way.  Your submission has to be safe to
import: a file that draws a window or reads an image at the moment it is imported
will fail on a machine that has neither a display nor the data directory.

    Usage:      python hw1_skeleton.py
    Requires:   numpy, matplotlib, pillow    (see the conda line in the handout)

Course policy on AI assistants applies to this file.  Your report must open with
a section titled "AI Assistant Usage" giving a percentage, and any function here
that was generated entirely by an AI assistant must say so in its own docstring.
"""

__author__ = "Shrikrishna Bhagirath Rajule (srajule@purdue.edu)"
__date__   = "2026-Sep-02"

import os
import numpy as np
import matplotlib

##  Choose a drawing backend before pyplot is imported. 
if not (os.environ.get("DISPLAY") or os.name == "nt" or
        os.environ.get("MPLBACKEND")):
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
from PIL import Image

"""
##  Uncomment this block if you want your recorded points and your figures to
##  come out the same on every run.  
seed = 0
random.seed(seed)
numpy.random.seed(seed)
"""


#______________________________  Lecture 2 in four functions  __________________________

##  These are given.  Read dehom() carefully: the comment inside it is the whole
##  reason we bother with homogeneous coordinates in the first place.

def hom(p):
    '''Physical point (x,y) as the homogeneous 3-vector [x, y, 1]^T.'''
    return np.array([p[0], p[1], 1.0])

def join(p, q):
    '''The line through the two physical points p and q.'''
    return np.cross(hom(p), hom(q))

def meet(l, m):
    '''The point where the two lines l and m cross.'''
    return np.cross(l, m)

def dehom(x, eps=1e-9):
    '''Homogeneous point back to physical, or None if the point is ideal.

    A homogeneous vector is defined only up to a nonzero scale, so asking
    whether "x3 is small" is meaningless on its own -- multiply the whole
    vector by a thousand and x3 grows with it.  The test has to be made
    relative to the other two entries, which is what is done below.

    Note also that [0, 0, c] with c nonzero is the ORIGIN and must come back
    as (0,0).  It is the zero vector that is not a point at all.
    '''
    if not np.any(x):
        return None
    scale = max(abs(x[0]), abs(x[1]))
    if abs(x[2]) <= eps * scale:
        return None
    return x[:2] / x[2]


#______________________________  Given framework  _______________________________________

##  Where the two supplied images live.  The default is the directory you get by
##  unzipping hw1_images.zip next to this file.  The environment variable is here
##  so that a grader can point the same code at a different directory without
##  editing it; you should not need to touch either.
DATA_DIR = os.environ.get("ECE661_HW1_DATA", "hw1_images")

def load_image(filename):
    '''Read an image from DATA_DIR as an (H, W, 3) array of uint8.'''
    path = os.path.join(DATA_DIR, filename)
    if not os.path.isfile(path):
        raise SystemExit(
            "Could not find %s.\n"
            "Unzip hw1_images.zip so that %s/ sits next to this file, or set the\n"
            "environment variable ECE661_HW1_DATA to the directory that has it."
            % (path, DATA_DIR))
    return np.array(Image.open(path).convert("RGB"))

def show_or_save(figure, filename):
    '''Put a figure on the screen if there is one, and always write it to disk.

    Every figure has to end up in your PDF report, so saving is not optional.
    Calling plt.show() with no display attached is an error, which is why this
    goes through the backend check made at the top of the file.
    '''
    figure.savefig(filename, dpi=110, bbox_inches="tight")
    if matplotlib.get_backend().lower() != "agg":
        plt.show()
    plt.close(figure)

def show_recorded_points(image, recorded, title):
    '''Draw the points you recorded on top of the image, and nothing else.

    Run this BEFORE you compute anything.  If a line you meant to record along
    a row of grout is drawn across the tiles instead, you will see it here.
    '''
    colors = ["#e4572e", "#2e86ab", "#3fa34d"]
    figure, axis = plt.subplots(figsize=(9, 7))
    axis.imshow(image)
    for (name, pairs), color in zip(recorded.items(), colors):
        for point_a, point_b in pairs:
            axis.plot([point_a[0], point_b[0]], [point_a[1], point_b[1]],
                      '-o', color=color, markersize=5, linewidth=1)
    axis.set_xlim(0, image.shape[1]);  axis.set_ylim(image.shape[0], 0)
    axis.set_title(title)
    return figure

def bounding_box_diagonal(points):
    '''The "spread" that Task-1(b) asks for: the diagonal of the bounding box.'''
    p = np.asarray(points, dtype=float)
    return float(np.hypot(np.ptp(p[:, 0]), np.ptp(p[:, 1])))

def draw_line_across(axis, line, xlim, color="#3fa34d", linewidth=2):
    '''Draw the line l = [a,b,c]^T across the given range of x.'''
    x = np.array(xlim, dtype=float)
    axis.plot(x, -(line[0] * x + line[2]) / line[1], '--',
              color=color, linewidth=linewidth)

def draw_conic(axis, C, image_shape, color="#e4572e", linewidth=2):
    '''Draw the curve x^T C x = 0 over the extent of an image.'''
    height, width = image_shape[:2]
    gx, gy = np.meshgrid(np.arange(0, width, 2.0), np.arange(0, height, 2.0))
    value = (C[0,0]*gx*gx + 2*C[0,1]*gx*gy + C[1,1]*gy*gy
             + 2*C[0,2]*gx + 2*C[1,2]*gy + C[2,2])
    axis.contour(gx, gy, value, levels=[0], colors=color, linewidths=linewidth)

def coefficients_to_matrix(c):
    '''The six coefficients [a,b,c,d,e,f] as the symmetric matrix of Lecture 2.'''
    a, b, cc, d, e, f = c
    return np.array([[a,   b/2, d/2],
                     [b/2, cc,  e/2],
                     [d/2, e/2, f  ]])

def two_panel_figure(image, recorded, vanishing_points, vanishing_line, title):
    '''The two-panel figure of Task-1(d).

    The near panel is scaled to the image, the wide panel to whatever vanishing
    points you actually computed, so this works on your own photograph in part
    (e) as well as on tiles.jpg.  If all of your vanishing points happen to
    land inside the frame, say so in your report and use one panel instead.
    '''
    height, width = image.shape[:2]
    vx = [v[0] for v in vanishing_points];  vy = [v[1] for v in vanishing_points]
    margin = 0.35 * max(width, height)
    wide_x = (min(-margin, min(vx) - margin), max(width + margin, max(vx) + margin))
    wide_y = (max(height + margin, max(vy) + margin), min(-margin, min(vy) - margin))
    near_x = (-0.35 * width, 1.6 * width)
    near_y = (1.15 * height, -0.4 * height)
    colors = ["#e4572e", "#2e86ab", "#3fa34d"]
    figure, axes = plt.subplots(1, 2, figsize=(14, 6.2))
    for axis, (xlim, ylim, subtitle) in zip(
            axes, [(near_x, near_y, "near view"), (wide_x, wide_y, "wide view")]):
        axis.imshow(image)
        for (name, pairs), color, v in zip(recorded.items(), colors, vanishing_points):
            for point_a, point_b in pairs:
                A = np.array(point_a, dtype=float);  B = np.array(point_b, dtype=float)
                t = np.linspace(-1, 9, 2)
                P = A + t[:, None] * (B - A)
                axis.plot(P[:,0], P[:,1], color=color, linewidth=1.0, alpha=0.85)
                axis.plot([point_a[0], point_b[0]], [point_a[1], point_b[1]],
                          'o', color=color, markersize=4)
            if xlim[0] <= v[0] <= xlim[1] and ylim[1] <= v[1] <= ylim[0]:
                axis.plot(v[0], v[1], '*', color=color, markersize=17,
                          markeredgecolor='k', label="VP " + name.split()[0])
        draw_line_across(axis, vanishing_line,
                         (xlim[0] - 4000, xlim[1] + 4000), color='k')
        axis.set_xlim(*xlim);  axis.set_ylim(*ylim)
        axis.legend(loc="lower right", fontsize=8)
        axis.set_title(subtitle, fontsize=9)
    figure.suptitle(title);  plt.tight_layout()
    return figure


#______________________________  Bonus (optional):  Shooting Around Cover  _____________

##  The arena, in an ordinary x-y plane with y upward.  The player is at the
##  origin and alpha is measured counter-clockwise from the +x axis.  No image
##  is involved in this section, and it is worth 10 bonus points.

TARGET = (np.array([1.0, 8.0]), np.array([3.0, 8.0]))
ARMOUR = (np.array([0.4, 4.0]), np.array([5.0, 4.0]))
WALL   = (np.array([7.0, 0.0]), np.array([7.0, 6.0]))

def draw_arena(axis):
    '''Given: the three segments and the player.'''
    for segment, color, label in [(TARGET, "#2e86ab", "target bar"),
                                  (ARMOUR, "#e4572e", "armour"),
                                  (WALL,   "#3fa34d", "mirror wall")]:
        axis.plot(*zip(*segment), color=color, linewidth=7,
                  solid_capstyle="butt", label=label)
    axis.plot(0, 0, 'ks', markersize=8)
    axis.set_aspect("equal");  axis.grid(alpha=0.25)
    axis.set_xlim(-1, 14.5);   axis.set_ylim(-1, 9.5)

def aiming_line(alpha_in_degrees):
    '''TODO (a): the aiming line, as a homogeneous 3-vector.

    It is the join of the origin and a point one unit away in the direction
    alpha.  Say in your report where alpha ends up in the three entries, and
    why the third entry comes out the way it does.
    '''
    raise NotImplementedError

def subtended_interval(segment):
    '''TODO (a): the angular interval a segment subtends at the origin.

    Return the SMALLER of the two arcs bounded by the two endpoint directions.
    Watch the case where that arc straddles the zero direction.
    '''
    raise NotImplementedError

def strikes_segment(segment, alpha_in_degrees, use_direction_test=True):
    '''TODO (b): does the shot at angle alpha strike this segment?

    Build the segment's line as the join of its endpoints, meet it with the
    aiming line, and decide whether the meet falls between the two endpoints.

    Write this FIRST with use_direction_test = False, run it at alpha = 250,
    and report what it claims about the target.  Then work out what is missing,
    add it under the flag, and run it again.
    '''
    raise NotImplementedError

def reflection_in_line(l):
    '''TODO (c): the reflection matrix M = I - 2 * n_tilde * l^T.

    The handout gives you the formula and the reason it is what it is.  This
    function should assume a^2 + b^2 = 1 and say so if that is not the case.
    '''
    raise NotImplementedError

def bonus():
    ##  TODO (a): report both intervals, and show that for every angle in the
    ##            target's interval the ray crosses y = 4 inside the armour.
    ##  TODO (a): meet the aiming line with l_infinity = [0,0,1]^T and say what
    ##            you get.  This is the first ideal point you will compute.
    ##  TODO (b): the naive test at alpha = 250, then the corrected one.
    ##  TODO (c): M for the wall x = 7; check that M @ M is the identity.
    ##  TODO (d): reflect the target bar in the wall, aim at the mirror image,
    ##            then trace the ray and check every leg of it.  Plot the path
    ##            on top of draw_arena().
    pass


#______________________________  Task-1:  Vanishing Points and the Vanishing Line  _____

##  TODO (a): replace the zeros with the coordinates YOU recorded in GIMP.
##
##  Families A and B run along grout lines.  Family C is the tile diagonals,
##  which are not drawn in the image: record a corner where four tiles meet,
##  then step diagonally across the grid and record another such corner.  Count
##  the tiles as you go.  A miscount gives you a line that is not in the family
##  and the image will not tell you so -- but show_recorded_points() will.

RECORDED_TILES = {
    "A  tile rows":      [((0, 0), (0, 0)),
                          ((0, 0), (0, 0)),
                          ((0, 0), (0, 0))],
    "B  tile columns":   [((0, 0), (0, 0)),
                          ((0, 0), (0, 0)),
                          ((0, 0), (0, 0))],
    "C  tile diagonals": [((0, 0), (0, 0)),
                          ((0, 0), (0, 0)),
                          ((0, 0), (0, 0))],
}

def vanishing_point_estimates(pairs_of_points):
    '''TODO (b): the vanishing point of one family, from all three line-pairs.

    Build the three lines as joins, then take all three pairs of those lines
    and meet each pair.  Return the three estimates.  They will not agree.

    Return their MEAN as well, and use the mean everywhere in (c) and (d).
    Which single pair you would otherwise pick is not a neutral choice: on
    tiles.jpg the residual of part (c) moves by a factor of several hundred
    across the possible choices.  The mean is the estimate this assignment
    marks against.
    '''
    raise NotImplementedError

def task_1():
    tiles = load_image("tiles.jpg")

    ##  Look before you compute.
    figure = show_recorded_points(tiles, RECORDED_TILES,
                                  "do these lie along the features you meant?")
    show_or_save(figure, "task1_recorded_points.png")

    ##  TODO (b): WRITE YOUR PREDICTION IN YOUR REPORT BEFORE RUNNING THIS.
    ##            Which family will give the least reliable vanishing point,
    ##            and why?  Then compute the three estimates per family, their
    ##            spread, each family's MEAN vanishing point, and its distance
    ##            from the image centre (800, 600), and say whether the
    ##            prediction held.
    ##  TODO (c): order the families by spread; compute the perpendicular
    ##            distance from the WORST-determined mean vanishing point to
    ##            the line through the other two mean vanishing points.
    ##  TODO (d): the vanishing line as the join of the two BEST-determined
    ##            vanishing points, then two_panel_figure().
    ##  TODO (e): the same on the photograph you took yourself.
    pass


#______________________________  Task-2:  A Circle Photographed From an Angle  _________

##  TODO (a): replace with the eight points YOU recorded around the OUTER edge
##            of the plate.  Do not mix in the inner ring where the glaze
##            changes shade; that is a second, smaller circle.

RECORDED_RIM = np.array([[0, 0], [0, 0], [0, 0], [0, 0],
                         [0, 0], [0, 0], [0, 0], [0, 0]], dtype=float)

def fit_conic(points):
    '''TODO (b): fit a conic to a set of points.

    Each point contributes one row [x^2, xy, y^2, x, y, 1] to a design matrix.
    Since C is fixed only up to scale, what you want is the null direction of
    that matrix: the right singular vector belonging to its SMALLEST singular
    value.  numpy.linalg.svd returns U, s and Vt, and the vector you want is
    the last ROW of Vt.

    Return C, scaled so that its Frobenius norm is 1.  Fixing the scale is not
    optional -- x^T C x is linear in C, so without a convention the residual
    you report in part (b) could be made any number at all.

    (Keep the shape of this in mind.  Building a design matrix whose null
    vector is the answer, because the answer is only defined up to scale, is
    exactly how you will estimate a homography in HW2.)
    '''
    raise NotImplementedError

def task_2():
    plate = load_image("plate.jpg")

    figure, axis = plt.subplots(figsize=(8, 6))
    axis.imshow(plate)
    axis.plot(RECORDED_RIM[:,0], RECORDED_RIM[:,1], 'o',
              color="#2e86ab", markersize=7, markeredgecolor='k')
    axis.set_xlim(0, plate.shape[1]);  axis.set_ylim(plate.shape[0], 0)
    axis.set_title("your recorded rim points")
    show_or_save(figure, "task2_recorded_points.png")

    ##  TODO (b): fit C and report max_i |x_i^T C x_i| with ||C||_F = 1.
    ##            Expect something of order 1e-3 to 1e-4.  If you get order 1,
    ##            you have taken the wrong singular vector.
    ##  TODO (c): rescale so that a^2 + b^2 + c^2 = 1, report b^2 - 4ac and
    ##            classify.  Expect a value near -0.86 on plate.jpg.
    ##  TODO (d): the tangent at one recorded point, l = C p.  Overlay the
    ##            conic, the points and the tangent, then zoom in on p and
    ##            confirm the line touches the curve there without crossing it.
    pass


#______________________________  main  _________________________________________________

if __name__ == '__main__':
    task_1()
    task_2()
    bonus()
