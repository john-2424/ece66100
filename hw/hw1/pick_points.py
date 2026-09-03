#!/usr/bin/env python
"""Interactive pixel-coordinate recorder for ECE661 HW1.

The handout permits any tool that reports the cursor position, and names
Matplotlib's interactive window as one of them.  This is that window with a
click handler bolted on, so the coordinates land in a file instead of being
copied by hand.

    python pick_points.py tiles.jpg 18 tiles_points.txt
    python pick_points.py plate.jpg  8 rim_points.txt

Left-click records a point.  Right-click (or backspace) undoes the last one.
Scroll to zoom about the cursor; the toolbar pan/zoom also work.  Close the
window when you are done and the coordinates are printed and written out.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


##  What each click is for, so the window states it rather than the operator
##  having to keep count.  Task 1 wants three lines per family and two points
##  per line; the diagonals are stepped across the grid by counting tiles.
TILE_PROMPTS = []
for _family, _n in [("A  tile ROWS", 3), ("B  tile COLUMNS", 3),
                    ("C  tile DIAGONALS", 3)]:
    for _line in range(1, _n + 1):
        if _family.startswith("C"):
            TILE_PROMPTS.append("%s - line %d: a corner where 4 tiles meet"
                                % (_family, _line))
            TILE_PROMPTS.append("%s - line %d: step n tiles DIAGONALLY, "
                                "same n across and up, click that corner"
                                % (_family, _line))
        else:
            TILE_PROMPTS.append("%s - line %d: FIRST point, near one end"
                                % (_family, _line))
            TILE_PROMPTS.append("%s - line %d: SECOND point, far from the first"
                                % (_family, _line))

RIM_PROMPTS = ["OUTER rim of the plate - point %d of 8 "
               "(spread them right around, not bunched)" % _i
               for _i in range(1, 9)]

PROMPTS = {18: TILE_PROMPTS, 8: RIM_PROMPTS}


def pick(image_path, n_expected, out_path):
    """Show the image, record clicked pixel coordinates, and write them out."""
    image = np.array(Image.open(image_path).convert("RGB"))
    recorded = []

    figure, axis = plt.subplots(figsize=(14, 10))
    axis.imshow(image)
    prompts = PROMPTS.get(n_expected, [])

    def next_prompt():
        if len(recorded) < len(prompts):
            return prompts[len(recorded)]
        return "done - close the window"

    axis.set_title("%d/%d   NEXT: %s" % (0, n_expected, next_prompt()),
                   fontsize=11, color="#b8331a")
    markers = []

    def redraw():
        axis.set_title("%d/%d   NEXT: %s"
                       % (len(recorded), n_expected, next_prompt()),
                       fontsize=11, color="#b8331a")
        figure.canvas.draw_idle()

    def on_click(event):
        if event.inaxes is not axis or event.xdata is None:
            return
        if event.button == 1:
            recorded.append((round(event.xdata, 1), round(event.ydata, 1)))
            markers.append(axis.plot(event.xdata, event.ydata, 'o',
                                     color="#e4572e", markersize=6,
                                     markeredgecolor='k')[0])
            markers.append(axis.annotate(str(len(recorded)),
                                         (event.xdata, event.ydata),
                                         color="#2e86ab", fontsize=9,
                                         xytext=(5, 5),
                                         textcoords="offset points"))
            print("%2d  (%.1f, %.1f)" % (len(recorded), *recorded[-1]))
        elif event.button == 3 and recorded:
            recorded.pop()
            markers.pop().remove()
            markers.pop().remove()
        redraw()

    def on_scroll(event):
        """Zoom about the cursor so points can be placed to sub-pixel accuracy."""
        if event.inaxes is not axis or event.xdata is None:
            return
        factor = 0.8 if event.button == 'up' else 1.25
        x0, x1 = axis.get_xlim()
        y0, y1 = axis.get_ylim()
        axis.set_xlim(event.xdata + (x0 - event.xdata) * factor,
                      event.xdata + (x1 - event.xdata) * factor)
        axis.set_ylim(event.ydata + (y0 - event.ydata) * factor,
                      event.ydata + (y1 - event.ydata) * factor)
        figure.canvas.draw_idle()

    figure.canvas.mpl_connect("button_press_event", on_click)
    figure.canvas.mpl_connect("scroll_event", on_scroll)
    plt.show()

    with open(out_path, "w") as handle:
        for x, y in recorded:
            handle.write("%.1f %.1f\n" % (x, y))
    print("\nwrote %d points to %s" % (len(recorded), out_path))
    print(recorded)


if __name__ == '__main__':
    pick(sys.argv[1], int(sys.argv[2]), sys.argv[3])
