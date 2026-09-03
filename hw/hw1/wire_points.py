#!/usr/bin/env python
"""Wire recorded coordinates into hw1_ShrikrishnaRajule.py, and audit them.

pick_points.py writes one "x y" per line.  This reads those files, rewrites the
RECORDED_* literals in the submission file, and -- more usefully -- checks the
points before anything downstream depends on them:

  * every family's three lines must actually converge to a common point
  * a line whose pair of points is short is flagged, because a short baseline
    turns a one-pixel click error into a large direction error
  * a diagonal that was stepped with the wrong tile count shows up as one
    estimate disagreeing with the other two by orders of magnitude

    python wire_points.py
"""

import io
import os
import re
import sys

import numpy as np

TARGET = "hw1_ShrikrishnaRajule.py"


def read_points(path, expected):
    """Read an 'x y' per line file and return a list of (x, y) tuples."""
    if not os.path.isfile(path):
        return None
    points = []
    for line in io.open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            x, y = line.split()
            points.append((float(x), float(y)))
    if len(points) != expected:
        raise SystemExit("%s holds %d points, expected %d.  Re-run the picker."
                         % (path, len(points), expected))
    return points


def as_families(points, names):
    """Eighteen points in click order become three families of three lines."""
    families = {}
    for index, name in enumerate(names):
        block = points[index * 6:(index + 1) * 6]
        families[name] = [(block[0], block[1]), (block[2], block[3]),
                          (block[4], block[5])]
    return families


def audit(families, label):
    """Report, per family, whether the three lines really do converge."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hw1_ShrikrishnaRajule import join, meet, dehom, bounding_box_diagonal

    print("\n--- audit: %s ---" % label)
    ok = True
    for name, pairs in families.items():
        baselines = [np.hypot(b[0] - a[0], b[1] - a[1]) for a, b in pairs]
        lines = [join(a, b) for a, b in pairs]

        estimates = []
        for i in range(3):
            for j in range(i + 1, 3):
                point = dehom(meet(lines[i], lines[j]))
                estimates.append(point)

        if any(point is None for point in estimates):
            print("  %-20s TWO LINES CAME OUT EXACTLY PARALLEL" % name)
            ok = False
            continue

        estimates = np.array(estimates)
        spread = bounding_box_diagonal(estimates)
        centre = estimates.mean(axis=0)

        ##  A single pair disagreeing wildly with the other two is the
        ##  signature of a miscounted diagonal or a point on the wrong line.
        distances = np.hypot(*(estimates - centre).T)
        outlier = distances.max() / max(distances.min(), 1e-12)

        flags = []
        if min(baselines) < 100:
            flags.append("short baseline (%.0f px)" % min(baselines))
        if outlier > 50:
            flags.append("ONE PAIR DISAGREES x%.0f - check this family" % outlier)

        print("  %-20s baselines %5.0f %5.0f %5.0f px   spread %10.1f px  %s"
              % (name, *baselines, spread,
                 "  <-- " + "; ".join(flags) if flags else "ok"))
        if flags and "DISAGREES" in " ".join(flags):
            ok = False
    return ok


def literal_families(families, indent=4):
    """Render a families dict as the Python literal that goes in the file."""
    width = max(len(name) for name in families)
    lines = ["{"]
    for name, pairs in families.items():
        head = '%s"%s":%s [' % (" " * indent, name,
                                " " * (width - len(name) + 1))
        pad = " " * len(head)
        for k, (a, b) in enumerate(pairs):
            text = "((%.1f, %.1f), (%.1f, %.1f))" % (a[0], a[1], b[0], b[1])
            lines.append((head if k == 0 else pad) + text +
                         ("," if k < 2 else "],"))
    lines.append("}")
    return "\n".join(lines)


def literal_rim(points, indent=4):
    """Render the eight rim points as the np.array literal."""
    rows = ["[%.1f, %.1f]" % (x, y) for x, y in points]
    body = ",\n".join(" " * (indent + 21) + ", ".join(rows[k:k + 2])
                      for k in range(0, 8, 2))
    return "np.array([" + body.lstrip() + "], dtype=float)"


def replace_block(source, anchor, new_text):
    """Replace the literal that follows 'anchor = ' up to its closing brace."""
    start = source.index(anchor)
    open_at = source.index("{" if new_text.startswith("{") else "np.array(",
                           start)
    if new_text.startswith("{"):
        depth, end = 0, open_at
        while True:
            if source[end] == "{":
                depth += 1
            elif source[end] == "}":
                depth -= 1
                if depth == 0:
                    end += 1
                    break
            end += 1
    else:
        depth, end = 0, source.index("(", open_at)
        while True:
            if source[end] == "(":
                depth += 1
            elif source[end] == ")":
                depth -= 1
                if depth == 0:
                    end += 1
                    break
            end += 1
    return source[:open_at] + new_text + source[end:]


def main():
    source = io.open(TARGET, encoding="utf-8").read()

    tiles = read_points("tiles_points.txt", 18)
    if tiles:
        families = as_families(tiles, ["A  tile rows", "B  tile columns",
                                       "C  tile diagonals"])
        audit(families, "tiles.jpg")
        source = replace_block(source, "RECORDED_TILES = ",
                               literal_families(families))
        print("wired 18 tile points")

    rim = read_points("rim_points.txt", 8)
    if rim:
        source = replace_block(source, "RECORDED_RIM = ", literal_rim(rim))
        print("wired 8 rim points")

    photo = read_points("photo_points.txt", 18)
    if photo:
        families = as_families(photo, ["A  first family", "B  second family",
                                       "C  third family"])
        audit(families, "myphoto.jpg")
        source = replace_block(source, "RECORDED_MY_PHOTO = ",
                               literal_families(families))
        print("wired 18 photo points")

    io.open(TARGET, "w", encoding="utf-8").write(source)
    print("\n%s updated" % TARGET)


if __name__ == '__main__':
    main()
