from abc import abstractmethod

from matplotlib.offsetbox import DrawingArea
from matplotlib.widgets import TextBox, Slider

from .widgets import (BaseWidget, Label, HWidgets)

from .composite_widget import CompositeWidget


class DrawingAreaBase(DrawingArea):
    def __init__(self, width, height, xdescent=0.,
                 ydescent=0., clip=False):
        """
        *width*, *height* : width and height of the container box.
        *xdescent*, *ydescent* : descent of the box in x- and y-direction.
        *clip* : Whether to clip the children
        """

        super().__init__(width, height, xdescent=xdescent, ydescent=ydescent,
                         clip=clip)

    def get_offset(self, width, height, xdescent, ydescent, renderer):
        """
        Get the offset

        accepts extent of the box
        """
        return (self._offset(width, height, xdescent, ydescent, renderer)
                if callable(self._offset)
                else self._offset)

    def draw(self, renderer):
        """
        Draw the children
        """

        pass


class AxesWidget(BaseWidget):
    def __init__(
            self,
            wid,
            width, height,
            pad=0.0,
            draw_frame=False,
            patch_attrs=None,
            tooltip=None,
            expand=True,
    ):
        self.wid = wid
        self.child_box = DrawingAreaBase(width=width, height=height)

        super().__init__(self.child_box, pad=pad,
                         draw_frame=draw_frame, patch_attrs=patch_attrs,
                         tooltip=tooltip, expand=expand)
        self.ax = None
        self._cb_get_status = None

    def add_axes_box(self):
        from mpl_widget_box.axes_widget_base import (OffsetBoxLocator,
                                                     Axes, TextBox)

        locator = OffsetBoxLocator(self.child_box)
        self.ax = Axes(self.figure, [0, 0, 1, 1], animated=True)
        self.figure.add_axes(self.ax)
        self.ax.set_axes_locator(locator)

        # self.ax.spines["left"].set_visible(False)

    # Below two methods is to use this as a foreing widget.
    def purge_background(self):
        pass

    def draw(self, renderer):
        # self.box.draw(renderer)
        self.ax.draw_artist(self.ax)
        # ax.draw_artist(renderer)

    def set_cb_get_status(self, cb):
        self._cb_get_status = cb

    def get_status(self):
        if self._cb_get_status is not None:
            return self._cb_get_status()
        else:
            return {}


class CompositeAxesWidgetBase(CompositeWidget):
    def __init__(self, wid, width, height,
                 label=None) -> None:
        self.axes_widget = AxesWidget(
            wid,
            width=width, height=height,
            pad=0.0,
            draw_frame=False,
            patch_attrs=None,
            tooltip=None,
            expand=True
        )
        self._label =label

    def build_widgets(self):
        if self._label is None:
            r = [self.axes_widget]
        else:
            r = [HWidgets(children=[Label("label", self._label), self.axes_widget],
                          align="center")]
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

    def post_uninstall(self, wbm):
        pass

    def get_status(self):
        return self._get_status(self._box)

    @abstractmethod
    def _make_box(self, ax):
        pass

    @abstractmethod
    def _get_status(self, box):
        pass


class TextAreaWidget(CompositeAxesWidgetBase):
    def __init__(self, wid, width, height, initial_text="",
                 label=None) -> None:
        super().__init__(wid, width, height, label=label)
        self._initial_text = initial_text

    def _make_box(self, ax):
        _box = TextBox(ax, "",
                       label_pad=0,
                       initial=self._initial_text)
        return _box

    def _get_status(self, box):
        return dict(text=box.text)


class SliderWidget(CompositeAxesWidgetBase):
    def __init__(self, wid, width, height, vmin=0, vmax=1,
                 label=None) -> None:
        super().__init__(wid, width, height, label=label)
        self._vmin = vmin
        self._vmax = vmax

    def _make_box(self, ax):
        _box = Slider(ax, "", self._vmin, self._vmax)
        _box.valtext.set_visible(False)
        return _box

    def _get_status(self, box):
        return dict(val=box.val)


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