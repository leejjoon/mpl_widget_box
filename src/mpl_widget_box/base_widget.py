import matplotlib.transforms as mtransforms
from matplotlib.offsetbox import PaddedBox
from matplotlib.offsetbox import (
    AnnotationBbox,
    TextArea as _TextArea,
)


# TextArea with optional fixed width
class TextArea(_TextArea):
    def __init__(self, s, textprops=None, multilinebaseline=False):
        super().__init__(s, textprops=textprops, multilinebaseline=multilinebaseline)

    def set_textprops(self, **textprops):
        t = self._text
        for k, v in textprops.items():
            if hasattr(t, f"set_{k}"):
                getattr(t, f"set_{k}")(v)
            else:
                raise KeyError(f"no set_f{k} method in {t}")


# Widgets are derived from PaddedBox, which is basically an offsetbox.

# For widgets, their `draw` method is modified to support delayed draws, i.e.,
# the need to retunr any delayed draws. You need to make sure that they are not
# lost in the middle which does not support `draw` with return vlaues.


class BaseWidget(PaddedBox):
    def __init__(
        self,
        child,
        pad=0.0,
        draw_frame=False,
        patch_attrs=None,
        tooltip=None,
        expand=True,
        fixed_width=None,
        align="",
    ):
        super().__init__(child, pad=pad, draw_frame=draw_frame, patch_attrs=patch_attrs)

        self.set_tooltip(tooltip)

        self._mouse_on = False
        self._expand = expand
        self._align = align
        self._fixed_width = fixed_width

    def set_fixed_width(self, width):
        self._fixed_width = width

    # we override get_window_extent and get_extent to support fixed width
    def get_window_extent(self, renderer):
        _ = super().get_window_extent(renderer)

        w = _.width
        if self._fixed_width is not None:
            w = renderer.points_to_pixels(self._fixed_width + 2 * self.pad)
            _ = _.from_bounds(_.x0, _.y0, w, _.height)
        return _

    def get_extent(self, renderer):
        w, h, xd, yd = super().get_extent(renderer)
        if self._fixed_width is not None:
            w = renderer.points_to_pixels(self._fixed_width + 2 * self.pad)

        return w, h, xd, yd

    def set_tooltip(self, tooltip):
        if tooltip is not None:
            self.tooltip = self.create_tooltip(tooltip)
        else:
            self.tooltip = None

    def get_tooltip_textarea(self):
        return self.tooltip.get_children()[0]

    def get_event_area(self, renderer):
        bb = self.patch.get_window_extent(renderer)

        return bb

    def draw_frame_with_outer_bbox(self, renderer, outer_bbox):
        if self._expand:

            frame_bbox = mtransforms.Bbox.from_bounds(
                outer_bbox.xmin, outer_bbox.ymin, outer_bbox.width, outer_bbox.height
            )

            self.update_frame(frame_bbox)
        else:

            frame_bbox = self.get_window_extent(renderer)
            if self._align == "right":
                # make offset for right align
                oa = outer_bbox.width - frame_bbox.width
            elif self._align == "center":
                # make offset for right align
                oa = .5 * (outer_bbox.width - frame_bbox.width)
            else:
                oa = 0

            if oa != 0:
                frame_bbox = mtransforms.Bbox.from_bounds(
                    frame_bbox.xmin + oa, frame_bbox.ymin, frame_bbox.width, frame_bbox.height
                )

            self.update_frame(frame_bbox)

        self.draw_frame_as_is(renderer)

    def draw_frame_as_is(self, renderer):
        # Note that this is different from self.draw_frame which resets the
        # bbox of the patch.
        self.patch.draw(renderer)

    def update_child_offsets(self, renderer, outer_bbox):
        w, h, xdescent, ydescent, offsets = self.get_extent_offsets(renderer)
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)

        # make offset for right align
        if self._align == "right":
            oa = outer_bbox.width - w
        elif self._align == "center":
            oa = .5 * (outer_bbox.width - w)
        else:
            oa = 0.

        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((oa + px + ox, py + oy))

    def draw(self, renderer):
        # FIXME: I don't think this method is called by others.
        super().draw(renderer)
        if self.tooltip is not None and self._mouse_on:
            # delayed draw method
            return [self.draw_tooltip]

    def draw_with_outer_bbox(self, renderer, outer_bbox):
        # a copy of PaddedBox.draw to use draw_frame_with_outer_bbox to draw frame

        # docstring inherited

        self.update_child_offsets(renderer, outer_bbox)

        self.draw_frame_with_outer_bbox(renderer, outer_bbox)

        delayed_draws = []
        for c in self.get_visible_children():
            if hasattr(c, "draw_with_outer_bbox"):
                dpicor = renderer.points_to_pixels(1.0)
                pad = self.pad * dpicor
                new_outer_bbox = mtransforms.Bbox.from_bounds(
                    outer_bbox.xmin + pad,
                    outer_bbox.ymin + pad,
                    outer_bbox.width - 2 * pad,
                    outer_bbox.height - 2 * pad,
                )

                _ = c.draw_with_outer_bbox(renderer, new_outer_bbox)
                delayed_draws.extend(_ or [])
            else:
                _ = c.draw(renderer)
                delayed_draws.extend(_ or [])

        self.stale = False

        if self.tooltip is not None and self._mouse_on:
            delayed_draws.append(self.draw_tooltip)

        return delayed_draws

    def handle_event(self, event, parent=None):
        if event.name == "motion_notify_event":
            return self.handle_motion_notify(event, parent)
        elif event.name == "button_press_event":
            return self.handle_button_press(event, parent)

    def handle_button_press(self, event, parent=None):
        return None

    def handle_motion_notify(self, event, parent=None):
        return None

    def _get_tooltip_anchor(self):
        return self.patch

    def create_tooltip(self, tooltip):
        box = TextArea(tooltip)
        xy = (0.5, 0)
        xybox = (0, -5)
        wrapped_box = AnnotationBbox(
            box,
            xy=xy,
            xybox=xybox,
            xycoords=self._get_tooltip_anchor(),
            boxcoords="offset points",
            box_alignment=(0.5, 1),
            pad=0.3,
            animated=True,
        )
        return wrapped_box

    def set_figure(self, fig):
        super().set_figure(fig)
        if self.tooltip is not None:
            self.tooltip.set_figure(fig)

    def draw_tooltip(self, renderer):
        # if self.tooltip is not None:
        self.tooltip.draw(renderer)
