from matplotlib.offsetbox import (AnchoredOffsetbox as _AnchoredOffsetbox,
                                  PaddedBox as _PaddedBox)

class AnchoredOffsetbox(_AnchoredOffsetbox):
    pass

from matplotlib.offsetbox import OffsetBox, bbox_artist, Bbox

# This monkey-patches Matplotlib to supprt offsetox that expand to fill in the
# gap.

class _OffsetBoxPatch():
    def draw(self, renderer):
        """
        Update the location of children if necessary and draw them
        to the given *renderer*.
        """
        my_bbox = self.get_extent_offsets(renderer)
        w, h, xdescent, ydescent, offsets = my_bbox
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)
        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((px + ox, py + oy))
            c.draw_with_parent_bbox(renderer, my_bbox)
        bbox_artist(self, renderer, fill=False, props=dict(pad=0.))
        self.stale = False

    def draw_with_parent_bbox(self, renderer, parent_bbox=None):
        if parent_bbox is None:
            self.draw(renderer)
        else:
            self.draw(renderer)

OffsetBox.draw = _OffsetBoxPatch.draw
OffsetBox.draw_with_parent_bbox = _OffsetBoxPatch.draw_with_parent_bbox


class PaddedBox(_PaddedBox):
    def draw_with_parent_bbox(self, renderer, parent_bbox):
        # docstring inherited
        my_bbox = self.get_extent_offsets(renderer)
        w, h, xdescent, ydescent, offsets = my_bbox
        # print("xdescent", xdescent)
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)
        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((px + ox, py + oy))

        self.draw_frame_with_parent_bbox(renderer, parent_bbox)

        for c in self.get_visible_children():
            c.draw_with_parent_bbox(renderer, my_bbox)

        self.stale = False

    def draw_frame_with_parent_bbox(self, renderer, parent_bbox):
        # update the location and size of the legend
        bbox =self.get_window_extent(renderer)
        points = bbox.get_points()

        dpicor = renderer.points_to_pixels(1.)
        pad = self.pad * dpicor

        ## FIXME this only work for left-aligned bbox.
        bbox2 = Bbox(points + [[0, 0],
                               [parent_bbox[0] - bbox.width - 2*pad, 0]])

        self.update_frame(bbox2)
        self.patch.draw(renderer)

