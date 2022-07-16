from abc import abstractmethod

from matplotlib.axes import Axes
from matplotlib.text import Text
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
from matplotlib.offsetbox import DrawingArea
from matplotlib.transforms import Bbox, TransformedBbox

from matplotlib.widgets import TextBox, Slider, RangeSlider

from .widgets import (BaseWidget, Label, HWidgets, MouseOverEvent,
                      WidgetBoxEvent)

from .composite_widget import CompositeWidget


class OffsetBoxLocator:
    def __init__(self, offsetbox, prop=None):
        self._offsetbox = offsetbox

        if prop is None:
            self.prop = FontProperties(size=rcParams["legend.fontsize"])
        elif isinstance(prop, dict):
            self.prop = FontProperties(**prop)
            if "size" not in prop:
                self.prop.set_size(rcParams["legend.fontsize"])
        else:
            self.prop = prop

    # def draw(self, renderer):
    #     raise RuntimeError("No draw method should be called")

    def __call__(self, ax, renderer):
        self.axes = ax

        # fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())

        box = self._offsetbox
        # box._update_offset_func(renderer, fontsize)
        width, height, xdescent, ydescent = box.get_extent(renderer)

        px, py = box.get_offset(width, height, 0, 0, renderer)
        bbox_canvas = Bbox.from_bounds(px, py, width, height)
        tr = ax.figure.transFigure.inverted()
        bb = TransformedBbox(bbox_canvas, tr)

        return bb


class DrawingAreaBase(DrawingArea):
    def __init__(self, width, height, xdescent=0.0, ydescent=0.0, clip=False):
        """
        *width*, *height* : width and height of the container box.
        *xdescent*, *ydescent* : descent of the box in x- and y-direction.
        *clip* : Whether to clip the children
        """

        super().__init__(width, height, xdescent=xdescent, ydescent=ydescent, clip=clip)

    def get_offset(self, width, height, xdescent, ydescent, renderer):
        """
        Get the offset

        accepts extent of the box
        """
        return (
            self._offset(width, height, xdescent, ydescent, renderer)
            if callable(self._offset)
            else self._offset
        )

    def draw_delayed(self, renderer):
        super().draw(renderer)

    def draw(self, renderer):
        """
        Draw the children
        """

        # super().draw(renderer)


class AxesWidget(BaseWidget):
    def __init__(
        self,
        wid,
        width,
        height,
        pad=0.0,
        draw_frame=False,
        patch_attrs=None,
        tooltip=None,
        expand=True,
    ):
        self.wid = wid
        self.child_box = DrawingAreaBase(width=width, height=height)

        super().__init__(
            self.child_box,
            pad=pad,
            draw_frame=draw_frame,
            patch_attrs=patch_attrs,
            tooltip=tooltip,
            expand=expand,
        )
        self.ax = None
        self._cb_get_status = None

    def add_axes_box(self):

        locator = OffsetBoxLocator(self.child_box)
        self.ax = Axes(self.figure, [0, 0, 1, 1], animated=True)
        self.figure.add_axes(self.ax)
        self.ax.set_axes_locator(locator)

        # self.ax.spines["left"].set_visible(False)

    # Below two methods is to use this as a foreing widget.
    def purge_background(self):
        pass

    def handle_event(self, event, parent=None):
        if event.name == "motion_notify_event":
            return self.handle_motion_notify(event, parent)

    def handle_motion_notify(self, event, parent=None):
        auxinfo = {}
        if self._mouse_on == False:
            self._mouse_on = True
            auxinfo["mouse_entered"] = True

        return MouseOverEvent(event, self.wid, self, auxinfo=auxinfo)

    def set_mouse_leave(self):
        self._mouse_on = False

    def draw(self, renderer):
        # self.box.draw(renderer)

        self.ax.draw_artist(self.ax)
        if not self._mouse_on:
            self.child_box.draw_delayed(renderer)
            # delayed_artists.append(self.child_box.draw_delayed)

        # ax.draw_artist(renderer)

    def set_cb_get_status(self, cb):
        self._cb_get_status = cb

    def get_status(self):
        if self._cb_get_status is not None:
            return self._cb_get_status()
        else:
            return {}


class CompositeAxesWidgetBase(CompositeWidget):
    def __init__(self, wid, width, height, label=None, axes_tooltip=None) -> None:
        self.axes_widget = AxesWidget(
            wid,
            width=width,
            height=height,
            pad=0.0,
            draw_frame=False,
            patch_attrs=None,
            tooltip=axes_tooltip,
            expand=True,
        )
        self._label = label
        self._wbm = None

    def build_widgets(self):
        if self._label is None:
            r = [self.axes_widget]
        else:
            r = [
                HWidgets(
                    children=[Label("label", self._label), self.axes_widget],
                    align="center",
                )
            ]
        return r

    def post_install(self, wbm):
        # The 'add_axes_box' should be called after the figure is set. So, we
        # do thi in post_install phase.
        aw = self.axes_widget
        aw.set_figure(wbm.fig)
        aw.add_axes_box()
        self._box = self._make_box(aw.ax)
        wbm.add_foreign_widget(self.axes_widget)

        aw.set_cb_get_status(self.get_status)
        self._wbm = wbm

    def post_uninstall(self, wbm):
        self._wbm = None

    def get_status(self):
        return self._get_status(self._box)

    @abstractmethod
    def _make_box(self, ax):
        pass

    @abstractmethod
    def _get_status(self, box):
        pass


class TextAreaWidget(CompositeAxesWidgetBase):
    def __init__(self, wid, width, height, initial_text="", label=None) -> None:
        super().__init__(wid, width, height, label=label)
        self._initial_text = initial_text

    def _make_box(self, ax):
        _box = TextBox(ax, "", label_pad=0, initial=self._initial_text)
        return _box

    def _get_status(self, box):
        return dict(text=box.text)


class SliderWidget(CompositeAxesWidgetBase):
    def _get_default_fmt(self, vmin, vmax):
        # FIXME: there should be a better way. We may take a look at the
        # ScalarTickFormatter.
        dstep = abs(self._vmax - self._vmin) / 100.
        if dstep > 100:
            valfmt = "{:.2e}"
        elif dstep > 1.:
            valfmt = "{:.0f}"
        elif dstep > 0.05:
            valfmt = "{:.1f}"
        elif dstep > 0.005:
            valfmt = "{:.2f}"
        elif dstep > 0.0005:
            valfmt = "{:.3f}"
        else:
            valfmt = "{:e}"

        return valfmt

    def __init__(self, wid, width, height,
                 valmin=0, valmax=1, valinit=0.5, valfmt=None,
                 label=None, tooltip=None, label_width=None,
                 value_tooltip_on=True,
                 value_overlay_on=True,
                 value_label_on=False) -> None:

        axes_tooltip = "" if value_tooltip_on else None

        super().__init__(wid, width, height, label=label,
                         axes_tooltip=axes_tooltip)
        self._vmin = valmin
        self._vmax = valmax
        self._vinit = valinit
        if valfmt is None:
            valfmt = self._get_default_fmt(valmin, valmax)

        self._vfmt = "{}" if valfmt is None else valfmt

        self._label = label
        self._label_width = label_width

        self._value_label_on = value_label_on
        self._value_tooltip_on = value_tooltip_on
        self._value_overlay_on = value_overlay_on

        self._value_label = None
        self._value_overlay = None

        self._tooltip = tooltip

    def cb(self, value):
        # if self.axes_widget.tooltip is not None:
        #     self.axes_widget.get_tooltip_textarea().set_text(self._vfmt.format(value))
        #     # print(self.get_tooltip_textarea().get_text())

        # if self._value_label is not None:
        #     self._value_label.set_label(self._vfmt.format(value))

        self.update_value(value)

        status = self._wbm.get_named_status()
        e = WidgetBoxEvent(None, self.axes_widget.wid,
                           auxinfo=None, callback_info=None)

        self._wbm._callback(self._wbm, e, status)

    def build_widgets(self):

        if self._value_overlay_on:
            w = self.axes_widget.child_box

            from matplotlib.patches import Rectangle
            rect = Rectangle((0, 0), w.width, w.height, ec="none", fc="w",
                             alpha=0.4)
            w.add_artist(rect)

            self._value_overlay = Text(w.width*0.5, w.height*0.5, "",
                     ha="center", va="center")
            w.add_artist(self._value_overlay)

        if self._label is not None:
            _r = [Label(self.axes_widget.wid+":label", self._label,
                        tooltip=self._tooltip,
                        fixed_width=self._label_width)]
        else:
            _r = []

        _r.append(self.axes_widget)

        if self._value_label_on:
            self._value_label = Label(self.axes_widget.wid+"value", "")
            _r.append(self._value_label)

        r = [HWidgets(_r, align="center")]
        return r

    def update_value(self, v):
        s = self._vfmt.format(v)
        if self._value_label is not None:
            self._value_label.set_label(s)

        if self.axes_widget.tooltip is not None:
            self.axes_widget.get_tooltip_textarea().set_text(s)

        if self._value_overlay is not None:
            self._value_overlay.set_text(s)

    def _make_box(self, ax):

        _box = Slider(ax, "", self._vmin, self._vmax, valinit=self._vinit)
        _box.valtext.set_visible(False)
        _box.on_changed(self.cb)

        self.update_value(self._vinit)

        return _box

    def _get_status(self, box):
        return dict(val=box.val)


class RangeSliderWidget(SliderWidget):

    def _make_box(self, ax):
        _box = RangeSlider(ax, "", self._vmin, self._vmax, valinit=self._vinit)
        _box.valtext.set_visible(False)
        _box.on_changed(self.cb)

        return _box

    def update_value(self, v):
        s0 = self._vfmt.format(v[0])
        s1 = self._vfmt.format(v[1])
        s = f"{s0}, {s1}"

        if self._value_label is not None:
            self._value_label.set_label(s)

        if self.axes_widget.tooltip is not None:
            self.axes_widget.get_tooltip_textarea().set_text(s)

        if self._value_overlay is not None:
            self._value_overlay.set_text(s)


class CompositeAxesWidget(CompositeAxesWidgetBase):
    def __init__(self, wid, width, height, label=None) -> None:
        super().__init__(wid, width, height, label=label)
        self._status = {}

    def _make_box(self, ax):
        pass

    def _get_status(self, box):
        return self._status

    def get_axes_for_widget(self):
        return self.axes_widget.ax

    def update_status(self, **kw):
        self._status.update(**kw)
