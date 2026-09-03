#!/usr/bin/env python

##  hw1_ShrikrishnaRajule.py

"""
Homework 1 of ECE 661, Computer Vision, Fall 2026.

Everything here is built out of four facts from Lecture 2:

    the line through two points            l  =  x1 cross x2
    the point where two lines meet         x  =  l1 cross l2
    a conic                                x^T C x  =  0
    the tangent to C at a point p on it    l  =  C p

    Usage:      python hw1_ShrikrishnaRajule.py
    Requires:   numpy, matplotlib, pillow

AI Assistant Usage is declared at the front of the accompanying report.  Any
function below that was generated entirely by an AI assistant says so in its
own docstring.
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
##  unzipping hw1_images.zip next to this file.
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
    '''Put a figure on the screen if there is one, and always write it to disk.'''
    figure.savefig(filename, dpi=110, bbox_inches="tight")
    if matplotlib.get_backend().lower() != "agg":
        plt.show()
    plt.close(figure)

def show_recorded_points(image, recorded, title):
    '''Draw the points you recorded on top of the image, and nothing else.'''
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

def matrix_to_coefficients(C):
    '''The inverse of coefficients_to_matrix(): recover [a,b,c,d,e,f] from C.'''
    return np.array([C[0,0], 2*C[0,1], C[1,1], 2*C[0,2], 2*C[1,2], C[2,2]])

def two_panel_figure(image, recorded, vanishing_points, vanishing_line, title):
    '''The two-panel figure of Task-1(d).'''
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


#______________________________  Task-1:  Vanishing Points and the Vanishing Line  _____

##  (a)  The eighteen points recorded by hand.  Families A and B run along grout
##       lines.  Family C is the tile diagonals, which are not drawn in the
##       image: a corner where four tiles meet, then a diagonal step of n tiles
##       across the grid to another such corner.
##
##       Tool used: the Matplotlib interactive window (pick_points.py), which the
##       handout names as an acceptable alternative to GIMP.

RECORDED_TILES = {
    "A  tile rows":       [((579.2, 383.5), (909.4, 508.0)),
                           ((510.6, 571.8), (1119.9, 783.9)),
                           ((662.1, 160.2), (773.8, 209.7))],
    "B  tile columns":    [((172.4, 450.5), (418.1, 227.2)),
                           ((670.1, 624.4), (705.2, 338.9)),
                           ((1446.9, 748.8), (1118.3, 366.0))],
    "C  tile diagonals":  [((451.6, 739.3), (1057.7, 645.1)),
                           ((119.8, 303.8), (872.7, 381.9)),
                           ((848.7, 302.2), (1009.9, 327.7))],
}


def vanishing_point_estimates(pairs_of_points):
    '''The vanishing point of one family, from all three line-pairs.

    Each recorded pair of points gives a line l = x1 x x2.  Three lines give
    three pairs, and each pair meets in one estimate of the family's vanishing
    point.  How badly the three disagree is the "spread" of part (b).

    The three estimates are dehomogenized FIRST and averaged SECOND.  A
    homogeneous 3-vector is fixed only up to scale, so the mean of three
    3-vectors is not a defined operation: rescaling one of them would move the
    answer without moving any of the three points it stands for.

    Returns
    -------
    estimates  : (3, 2) array, the three Cartesian estimates
    mean_point : (2,)  array, their mean, used everywhere downstream
    '''
    lines = [join(point_a, point_b) for point_a, point_b in pairs_of_points]

    estimates = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            point = dehom(meet(lines[i], lines[j]))
            if point is None:
                raise ValueError(
                    "lines %d and %d of this family meet at an ideal point: "
                    "they came out exactly parallel in the image, so this "
                    "family has no finite vanishing point." % (i, j))
            estimates.append(point)

    estimates = np.array(estimates, dtype=float)
    return estimates, estimates.mean(axis=0)


def perpendicular_distance(point, line):
    '''Perpendicular distance in pixels from a physical point to l = [a,b,c]^T.

    |a x + b y + c| / sqrt(a^2 + b^2).  Dividing by the norm of (a, b) is what
    turns a scale-dependent number into a length: rescaling l multiplies
    numerator and denominator by the same factor and the distance is unchanged.
    '''
    a, b, c = line
    return abs(a * point[0] + b * point[1] + c) / np.hypot(a, b)


def analyse_families(image, recorded, label, centre, figure_prefix):
    '''Run parts (b), (c) and (d) on one image and print the report tables.

    Called twice: once on tiles.jpg and once on the photograph of part (e).
    Returns the collinearity residual in pixels so the two can be compared.
    '''
    print("\n" + "=" * 78)
    print("  %s" % label)
    print("=" * 78)

    ##  (b)  three estimates per family, their spread, and the family mean.
    names, means, spreads, all_estimates = [], [], [], []
    for name, pairs in recorded.items():
        estimates, mean_point = vanishing_point_estimates(pairs)
        names.append(name)
        means.append(mean_point)
        spreads.append(bounding_box_diagonal(estimates))
        all_estimates.append(estimates)

    print("\n-- Task 1(b): the three estimates per family --------------------")
    print("%-20s %-52s %14s" % ("family", "estimates from pairs (12) (13) (23)",
                                "spread px"))
    for name, estimates, spread in zip(names, all_estimates, spreads):
        text = " ".join("(%9.1f,%9.1f)" % (e[0], e[1]) for e in estimates)
        print("%-20s %s %14.1f" % (name, text, spread))

    print("\n%-20s %28s %20s" % ("family", "mean vanishing point",
                                 "distance from centre"))
    for name, mean_point in zip(names, means):
        distance = np.hypot(mean_point[0] - centre[0], mean_point[1] - centre[1])
        print("%-20s (%12.1f, %12.1f) %20.1f" %
              (name, mean_point[0], mean_point[1], distance))

    ##  (c)  collinearity.  Order by spread, then measure how far the
    ##       worst-determined vanishing point sits off the line through the
    ##       other two.
    order = np.argsort(spreads)               # ascending: best determined first
    line_through_best_two = join(means[order[0]], means[order[1]])
    residual = perpendicular_distance(means[order[2]], line_through_best_two)

    print("\n-- Task 1(c): collinearity --------------------------------------")
    print("families ordered by spread, best determined first:")
    for rank, index in enumerate(order):
        print("   %d. %-20s spread = %12.1f px" %
              (rank + 1, names[index], spreads[index]))
    print("worst determined family : %s" % names[order[2]])
    print("line through the two best mean VPs : [%.6g, %.6g, %.6g]" %
          tuple(line_through_best_two))
    print("COLLINEARITY RESIDUAL (perpendicular distance) = %.3f px" % residual)

    ##  The determinant, printed only to make the point of part (c): it is not
    ##  a usable measure because each v_i is fixed only up to scale.
    matrix = np.column_stack([hom(m) for m in means])
    print("det[v1 v2 v3] with each v_i as [x, y, 1]^T : %.6g" %
          np.linalg.det(matrix))
    scaled = matrix.copy();  scaled[:, 2] *= 1e6
    print("the same determinant after scaling v3 by 1e6 : %.6g"
          "   (same three points, different number)" % np.linalg.det(scaled))

    ##  (d)  the vanishing line is the join of the two BEST determined
    ##       vanishing points; the worst one is deliberately left out of it.
    vanishing_line = line_through_best_two
    normalized = vanishing_line / np.hypot(vanishing_line[0], vanishing_line[1])
    print("\n-- Task 1(d): the vanishing line ---------------------------------")
    print("l_v = join(VP %s, VP %s)" %
          (names[order[0]].split()[0], names[order[1]].split()[0]))
    print("l_v = [%.6g, %.6g, %.6g]" % tuple(vanishing_line))
    print("l_v normalized to a^2 + b^2 = 1 : [%.6g, %.6g, %.6g]" % tuple(normalized))

    inside = sum(0 <= m[0] <= image.shape[1] and 0 <= m[1] <= image.shape[0]
                 for m in means)
    print("vanishing points that land inside the frame : %d of 3" % inside)

    figure = two_panel_figure(
        image, recorded, means, vanishing_line,
        "%s: nine lines, three vanishing points, and l_v" % label)
    show_or_save(figure, "%s_vanishing.png" % figure_prefix)

    return residual


#______________________________  Task-1(e):  my own photograph  ________________________

##  (e)  A photograph taken with a real camera, with three families of parallel
##       lines lying in one plane of the world.  Set MY_PHOTO to None to skip.
MY_PHOTO = "myphoto.jpg"

RECORDED_MY_PHOTO = {
    "A  first family":   [((2440.1, 882.2), (3146.4, 856.4)),
                          ((2185.3, 1704.6), (3298.0, 1711.1)),
                          ((3114.1, 640.3), (3768.8, 592.0))],
    "B  second family":  [((3207.7, 1182.2), (3085.1, 463.0)),
                          ((3643.1, 424.3), (4607.4, 1714.3)),
                          ((2559.4, 504.9), (2501.4, 669.4))],
    "C  third family":   [((3207.7, 1182.2), (3768.8, 595.2)),
                          ((4230.0, 375.9), (3933.3, 808.1)),
                          ((3117.4, 650.0), (3626.9, 417.8))],
}


def points_are_filled(recorded):
    '''True once the placeholder zeros have been replaced by real coordinates.'''
    return any(tuple(point) != (0, 0)
               for pairs in recorded.values()
               for pair in pairs
               for point in pair)


def task_1():
    tiles = load_image("tiles.jpg")

    ##  Look before you compute.
    figure = show_recorded_points(tiles, RECORDED_TILES,
                                  "do these lie along the features you meant?")
    show_or_save(figure, "task1_recorded_points.png")

    ##  (b), (c) and (d) on the supplied rendering.
    residual_tiles = analyse_families(
        tiles, RECORDED_TILES, "tiles.jpg  (1600 x 1200 rendering)",
        centre=(800, 600), figure_prefix="task1")

    ##  (e) the same on a photograph taken with a real camera.
    if MY_PHOTO is not None and points_are_filled(RECORDED_MY_PHOTO):
        photo = load_image(MY_PHOTO)
        height, width = photo.shape[:2]

        figure = show_recorded_points(
            photo, RECORDED_MY_PHOTO, "part (e): recorded points on my photograph")
        show_or_save(figure, "task1e_recorded_points.png")

        residual_photo = analyse_families(
            photo, RECORDED_MY_PHOTO, "my photograph  (%d x %d)" % (width, height),
            centre=(width / 2.0, height / 2.0), figure_prefix="task1e")

        print("\n-- Task 1(e): comparison of residuals ----------------------------")
        print("tiles.jpg  (rendered, exact pinhole) : %12.3f px" % residual_tiles)
        print("my photograph  (real lens)           : %12.3f px" % residual_photo)
        print("ratio                                : %12.2f x" %
              (residual_photo / residual_tiles))
    else:
        print("\n[part (e) skipped: fill in MY_PHOTO and RECORDED_MY_PHOTO]")


#______________________________  Task-2:  A Circle Photographed From an Angle  _________

##  (a)  Eight points recorded around the OUTER edge of the plate, where it
##       meets the table.  Points from the inner ring, where the glaze changes
##       shade, are a different and smaller circle and are excluded.

RECORDED_RIM = np.array([[515.4, 592.5], [665.3, 479.3],
                         [848.7, 418.6], [1022.6, 425.0],
                         [1111.9, 559.0], [965.2, 707.4],
                         [778.6, 775.9], [539.3, 760.0]], dtype=float)


def fit_conic(points):
    '''Fit a conic to a set of points and return C with ||C||_F = 1.

    Each point contributes one row [x^2, xy, y^2, x, y, 1] to a design matrix
    A, so that A c = 0 holds exactly for points that lie on the conic with
    coefficient vector c.  Since C is fixed only up to scale there is no
    "solve" to be done: what is wanted is the null direction of A, which for
    noisy measurements is the right singular vector belonging to the SMALLEST
    singular value -- the last ROW of Vt from numpy.linalg.svd.

    C is returned with Frobenius norm 1.  Fixing the scale is not optional:
    x^T C x is linear in C, so without a stated convention the residual of
    part (b) could be made any number at all.
    '''
    p = np.asarray(points, dtype=float)
    x, y = p[:, 0], p[:, 1]

    design = np.column_stack([x * x, x * y, y * y, x, y, np.ones_like(x)])

    _, singular_values, vt = np.linalg.svd(design)
    coefficients = vt[-1]                     # null direction of the design matrix

    C = coefficients_to_matrix(coefficients)
    return C / np.linalg.norm(C), singular_values


def algebraic_residuals(C, points):
    '''|x^T C x| at each recorded point.  Zero for a point exactly on the conic.'''
    return np.array([abs(hom(p) @ C @ hom(p)) for p in points])


def task_2():
    plate = load_image("plate.jpg")

    ##  (a)  look at the recorded points before computing anything.
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.imshow(plate)
    axis.plot(RECORDED_RIM[:,0], RECORDED_RIM[:,1], 'o',
              color="#2e86ab", markersize=7, markeredgecolor='k')
    axis.set_xlim(0, plate.shape[1]);  axis.set_ylim(plate.shape[0], 0)
    axis.set_title("your recorded rim points")
    show_or_save(figure, "task2_recorded_points.png")

    print("\n" + "=" * 78)
    print("  Task 2: a circle photographed from an angle")
    print("=" * 78)

    ##  (b)  fit the conic and report the residual at ||C||_F = 1.
    C, singular_values = fit_conic(RECORDED_RIM)

    print("\n-- Task 2(b): the fitted conic -----------------------------------")
    print("singular values of the design matrix:")
    print("   " + "  ".join("%.4g" % s for s in singular_values))
    print("\nC, scaled so that ||C||_F = 1:")
    for row in C:
        print("   [%14.8f %14.8f %14.8f]" % tuple(row))
    print("\n||C||_F = %.6f" % np.linalg.norm(C))

    residuals = algebraic_residuals(C, RECORDED_RIM)
    print("\n|x_i^T C x_i| at each recorded point:")
    for index, value in enumerate(residuals):
        print("   point %d : %.6e" % (index + 1, value))
    print("max_i |x_i^T C x_i| = %.6e" % residuals.max())

    ##  (c)  rescale so that a^2 + b^2 + c^2 = 1 and classify.
    a, b, c, d, e, f = matrix_to_coefficients(C)
    scale = np.hypot(np.hypot(a, b), c)
    a, b, c, d, e, f = np.array([a, b, c, d, e, f]) / scale
    discriminant = b * b - 4 * a * c

    print("\n-- Task 2(c): classification -------------------------------------")
    print("coefficients rescaled so that a^2 + b^2 + c^2 = 1:")
    print("   a = %11.7f   b = %11.7f   c = %11.7f" % (a, b, c))
    print("   d = %11.7f   e = %11.7f   f = %11.7f" % (d, e, f))
    print("check a^2 + b^2 + c^2 = %.9f" % (a*a + b*b + c*c))
    print("discriminant b^2 - 4ac = %.6f" % discriminant)
    print("classification: %s" %
          ("ellipse" if discriminant < 0 else
           "hyperbola" if discriminant > 0 else "parabola"))
    print("the two circle constraints, neither of which survives:")
    print("   b     = %11.7f   (a circle needs 0)" % b)
    print("   a - c = %11.7f   (a circle needs 0)" % (a - c))

    ##  (d)  the tangent at one recorded point, l = C p.
    tangent_point = RECORDED_RIM[0]
    p = hom(tangent_point)
    tangent = C @ p

    print("\n-- Task 2(d): the tangent ----------------------------------------")
    print("p = (%.1f, %.1f)" % (tangent_point[0], tangent_point[1]))
    print("l = C p = [%.8g, %.8g, %.8g]" % tuple(tangent))
    print("p^T C p = %.6e" % (p @ C @ p))
    print("l^T p   = %.6e" % (tangent @ p))
    print("difference between the two = %.6e" % abs(p @ C @ p - tangent @ p))

    ##  Overlay: the conic, the eight points and the tangent, plus a zoom on p
    ##  close enough to see that the line touches the curve without crossing it.
    figure, axes = plt.subplots(1, 2, figsize=(14, 6))
    for axis, half_width in zip(axes, [None, 60.0]):
        axis.imshow(plate)
        draw_conic(axis, C, plate.shape, color="#e4572e", linewidth=2)
        axis.plot(RECORDED_RIM[:,0], RECORDED_RIM[:,1], 'o',
                  color="#2e86ab", markersize=7, markeredgecolor='k')
        axis.plot(tangent_point[0], tangent_point[1], '*',
                  color="#3fa34d", markersize=18, markeredgecolor='k')
        draw_line_across(axis, tangent, (-4000, plate.shape[1] + 4000),
                         color="#3fa34d", linewidth=2)
        if half_width is None:
            axis.set_xlim(0, plate.shape[1]);  axis.set_ylim(plate.shape[0], 0)
            axis.set_title("fitted conic, the eight points, and the tangent at p")
        else:
            axis.set_xlim(tangent_point[0] - half_width,
                          tangent_point[0] + half_width)
            axis.set_ylim(tangent_point[1] + half_width,
                          tangent_point[1] - half_width)
            axis.set_title("zoom on p: the line touches without crossing")
    figure.suptitle("Task 2(d): tangent l = C p at a recorded rim point")
    plt.tight_layout()
    show_or_save(figure, "task2_conic_and_tangent.png")


#______________________________  Bonus (optional):  Shooting Around Cover  _____________

##  The arena, in an ordinary x-y plane with y upward.  The player is at the
##  origin and alpha is measured counter-clockwise from the +x axis.

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
    '''(a) The aiming line through the origin at angle alpha, as [a, b, c]^T.

    It is the join of the origin (0,0) and the point one unit away in the
    direction alpha, which works out to [-sin a, cos a, 0]^T.  The angle sits
    in the first two entries only, and the third entry is zero because every
    line through the origin satisfies a*0 + b*0 + c = 0, forcing c = 0.

    Note what the sign of alpha does NOT do: alpha and alpha + 180 give the
    same line up to the scale factor -1, so the line has no direction at all.
    That is the fact the whole bonus is built on.
    '''
    alpha = np.radians(alpha_in_degrees)
    return join((0.0, 0.0), (np.cos(alpha), np.sin(alpha)))


def subtended_interval(segment):
    '''(a) The angular interval a segment subtends at the origin, in degrees.

    Returns the SMALLER of the two arcs bounded by the endpoint directions,
    as (start, end) with the interval swept counter-clockwise from start.  If
    the smaller arc straddles the zero direction the returned start is larger
    than the returned end, which is how the straddle is signalled.
    '''
    angles = [np.degrees(np.arctan2(point[1], point[0])) % 360.0
              for point in segment]
    low, high = min(angles), max(angles)
    if high - low <= 180.0:
        return (low, high)
    return (high, low)          # the smaller arc runs through zero


def angle_is_inside(alpha_in_degrees, interval):
    '''True if alpha lies in an interval returned by subtended_interval().'''
    alpha = alpha_in_degrees % 360.0
    start, end = interval
    if start <= end:
        return start <= alpha <= end
    return alpha >= start or alpha <= end     # the straddling case


def strikes_segment(segment, alpha_in_degrees, use_direction_test=True):
    '''(b) Does the shot at angle alpha strike this segment?

    The line through the segment's endpoints is met with the aiming line, and
    the meet must fall between the endpoints.  That much is the naive test.

    A line has no direction, so the naive test also counts meets that lie
    BEHIND the player.  The missing condition is a ray-direction test:
    with d = (cos a, sin a)^T and q the meet, the shot travels forwards only
    when d . q > 0.  The inequality is strict because d . q = 0 is the meet at
    the player's own position (or on the perpendicular through it), which is
    not a forward hit.

    Returns (hit, q) with q the meet in Cartesian coordinates, or (False, None)
    when the aiming line is parallel to the segment.
    '''
    segment_line = join(segment[0], segment[1])
    q = dehom(meet(segment_line, aiming_line(alpha_in_degrees)))
    if q is None:
        return False, None                    # parallel: they meet at infinity

    ##  Is the meet between the endpoints?  Project onto the segment.
    a, b = np.asarray(segment[0], float), np.asarray(segment[1], float)
    t = np.dot(q - a, b - a) / np.dot(b - a, b - a)
    between = -1e-9 <= t <= 1.0 + 1e-9

    if not use_direction_test:
        return between, q

    alpha = np.radians(alpha_in_degrees)
    direction = np.array([np.cos(alpha), np.sin(alpha)])
    return bool(between and np.dot(direction, q) > 0.0), q


def reflection_in_line(l):
    '''(c) The reflection matrix M = I - 2 * n_tilde * l^T for a line l.

    ax + by + c is the signed distance to the line when a^2 + b^2 = 1, and
    (a, b) is the unit normal, so subtracting twice that distance along the
    normal is exactly a reflection.  n_tilde = [a, b, 0]^T is that normal as an
    ideal point, which is what makes the same matrix reflect directions too.
    '''
    l = np.asarray(l, dtype=float)
    norm = np.hypot(l[0], l[1])
    if abs(norm - 1.0) > 1e-9:
        print("   [reflection_in_line: a^2 + b^2 = %.6f, not 1; normalizing]"
              % (norm ** 2))
        l = l / norm
    n_tilde = np.array([l[0], l[1], 0.0])
    return np.eye(3) - 2.0 * np.outer(n_tilde, l)


def bonus():
    print("\n" + "=" * 78)
    print("  Bonus: shooting around cover")
    print("=" * 78)

    ##  (a)  the aiming line, the two subtended intervals, and l_infinity.
    print("\n-- Bonus (a): the aiming line and the two intervals ---------------")
    for alpha in (0.0, 45.0, 90.0):
        print("   aiming line at alpha = %5.1f deg : [%9.6f, %9.6f, %9.6f]"
              % (alpha, *aiming_line(alpha)))
    print("   alpha appears in the first two entries only; the third is 0")
    print("   because every line through the origin has c = 0.")

    target_interval = subtended_interval(TARGET)
    armour_interval = subtended_interval(ARMOUR)
    print("\n   target subtends : [%.4f, %.4f] deg" % target_interval)
    print("   armour subtends : [%.4f, %.4f] deg" % armour_interval)

    ##  Every angle in the target's interval crosses y = 4 inside the armour.
    print("\n   for every angle in the target's interval, where does the ray")
    print("   cross y = 4?  (the armour spans x in [0.4, 5.0])")
    armour_line = join(ARMOUR[0], ARMOUR[1])
    crossings = []
    for alpha in np.linspace(target_interval[0], target_interval[1], 9):
        q = dehom(meet(armour_line, aiming_line(alpha)))
        crossings.append(q[0])
        print("      alpha = %8.4f deg  ->  crosses y = 4 at x = %8.4f" %
              (alpha, q[0]))
    print("   all crossings lie in [%.4f, %.4f], inside the armour, so the"
          % (min(crossings), max(crossings)))
    print("   armour is met FIRST and no direct shot exists.")

    ideal = meet(aiming_line(45.0), np.array([0.0, 0.0, 1.0]))
    print("\n   aiming line at 45 deg met with l_inf = [0,0,1]^T :")
    print("      [%9.6f, %9.6f, %9.6f]  -> dehom() gives %s"
          % (*ideal, dehom(ideal)))
    print("   an IDEAL point: the direction of the ray, [cos a, sin a, 0]^T")
    print("   up to scale.  A direction is a point at infinity.")

    ##  (b)  the naive test, then the corrected one.
    print("\n-- Bonus (b): the naive hit test at alpha = 250 deg ---------------")
    naive, q_naive = strikes_segment(TARGET, 250.0, use_direction_test=False)
    fixed, q_fixed = strikes_segment(TARGET, 250.0, use_direction_test=True)
    alpha = np.radians(250.0)
    direction = np.array([np.cos(alpha), np.sin(alpha)])
    print("   meet of the aiming line with the target's line : (%.4f, %.4f)"
          % tuple(q_naive))
    print("   naive test (between the endpoints only)  : %s" % naive)
    print("   d . q = %.4f  ->  the meet is BEHIND the player"
          % np.dot(direction, q_naive))
    print("   corrected test (adds d . q > 0)          : %s" % fixed)
    print("   250 deg points down and to the left; the naive test is fooled")
    print("   because a homogeneous line has no direction.")

    ##  (c)  the reflection in the wall x = 7.
    print("\n-- Bonus (c): the reflection in x = 7 -----------------------------")
    wall_line = join(WALL[0], WALL[1])
    wall_line = wall_line / np.hypot(wall_line[0], wall_line[1])
    print("   l_wall normalized to a^2 + b^2 = 1 : [%.6f, %.6f, %.6f]"
          % tuple(wall_line))
    M = reflection_in_line(wall_line)
    print("   M =")
    for row in M:
        print("      [%9.6f %9.6f %9.6f]" % tuple(row))
    print("   M @ M =")
    for row in M @ M:
        print("      [%9.6f %9.6f %9.6f]" % tuple(row))
    print("   ||M @ M - I||_F = %.2e" % np.linalg.norm(M @ M - np.eye(3)))
    print("   M^2 = I because reflecting twice in the same line returns every")
    print("   point to itself: a reflection is its own inverse.")

    ##  (d)  the bank shot.
    print("\n-- Bonus (d): the bank shot ---------------------------------------")
    target_centre = np.array([2.0, 8.0])
    mirror_centre = dehom(M @ hom(target_centre))
    print("   target centre                 : (%.4f, %.4f)" % tuple(target_centre))
    print("   its mirror image in the wall  : (%.4f, %.4f)" % tuple(mirror_centre))

    alpha_shot = np.degrees(np.arctan2(mirror_centre[1], mirror_centre[0])) % 360.0
    print("   aim at the mirror image: alpha = %.6f deg" % alpha_shot)

    ##  Leg 1: does it clear the armour?
    hits_armour, q_armour = strikes_segment(ARMOUR, alpha_shot)
    print("\n   leg 1, the armour:")
    print("      crosses y = 4 at x = %.4f; the armour spans [0.4, 5.0]"
          % q_armour[0])
    print("      strikes the armour? %s  -> the shot clears it" % hits_armour)

    ##  Leg 1: where does it strike the wall?
    hits_wall, q_wall = strikes_segment(WALL, alpha_shot)
    print("\n   leg 1, the wall:")
    print("      strikes the wall at (%.4f, %.4f); the wall spans y in [0, 6]"
          % tuple(q_wall))
    print("      strikes the wall? %s" % hits_wall)

    ##  Reflect the direction: apply M to the ideal point of the incoming ray.
    alpha = np.radians(alpha_shot)
    incoming_ideal = np.array([np.cos(alpha), np.sin(alpha), 0.0])
    reflected_ideal = M @ incoming_ideal
    print("\n   incoming direction as an ideal point  : [%.6f, %.6f, %.6f]"
          % tuple(incoming_ideal))
    print("   reflected by M                        : [%.6f, %.6f, %.6f]"
          % tuple(reflected_ideal))
    print("   the third entry stays 0, so M's translation column drops out and")
    print("   what comes back is a pure direction.")

    ##  Leg 2: from the wall strike, along the reflected direction, to the bar.
    return_direction = reflected_ideal[:2]
    return_line = join(q_wall, q_wall + return_direction)
    target_line = join(TARGET[0], TARGET[1])
    landing = dehom(meet(return_line, target_line))
    print("\n   leg 2, the return:")
    print("      lands on y = 8 at x = %.6f; the bar spans x in [1, 3]"
          % landing[0])
    print("      lands on the bar? %s" % bool(1.0 <= landing[0] <= 3.0))
    print("      distance from the bar centre = %.2e" % abs(landing[0] - 2.0))

    ##  Plot the two-leg path.
    figure, axis = plt.subplots(figsize=(9, 6.5))
    draw_arena(axis)
    path = np.array([[0.0, 0.0], q_wall, landing])
    axis.plot(path[:, 0], path[:, 1], 'k--', linewidth=1.8, label="bank shot")
    axis.plot(*mirror_centre, 'x', color="#2e86ab", markersize=11,
              label="mirror image of the bar centre")
    axis.plot([0, mirror_centre[0]], [0, mirror_centre[1]], ':',
              color="#2e86ab", linewidth=1.2, label="aim at the mirror image")
    axis.legend(loc="upper left", fontsize=8)
    axis.set_title("Bonus (d): the two-leg bank shot, alpha = %.3f deg" % alpha_shot)
    show_or_save(figure, "bonus_bank_shot.png")


#______________________________  main  _________________________________________________

if __name__ == '__main__':
    task_1()
    task_2()
    bonus()
