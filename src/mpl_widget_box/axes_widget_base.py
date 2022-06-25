from matplotlib.axes import Axes

from matplotlib.font_manager import FontProperties
from matplotlib import rcParams

from matplotlib.transforms import Bbox, TransformedBbox

from matplotlib.offsetbox import (
    AnchoredOffsetbox,
    DrawingArea,
    TextArea,
    HPacker,
    VPacker,
)
from matplotlib.offsetbox import AnnotationBbox

from matplotlib.widgets import (
    AxesWidget,
    Button,
    RadioButtons as _RadioButtons,
    CheckButtons,
    TextBox,
)

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.text import Text
import matplotlib.patheffects as path_effects

from matplotlib.tight_layout import get_renderer


def ignore(self, event):
    """Return True if event should be ignored.

    This method (or a version of it) should be called at the beginning
    of any event callback.
    """
    return (not self.active) or (not self.ax.get_visible())


AxesWidget.ignore = ignore


class RadioButtons(_RadioButtons):
    def __init__(self, ax, labels, active=0, values=None):
        """
        active : active index
        """
        self._values = values
        self._labels = labels

        _RadioButtons.__init__(self, ax, labels, active=active)

    def get_selected_value(self):
        label1 = self.value_selected
        if self._values is not None:
            i = self._labels.index(label1)
            return self._values[i]
        else:
            return label1


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

    def draw(self, renderer):
        """
        Draw the children
        """

        pass


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


def make_axes_box(fig, box):
    bbox = [0, 0, 1, 1]

    ax = Axes(fig, bbox, animated=False)
    fig.add_axes(ax)
    locator = OffsetBoxLocator(box)
    ax.set_axes_locator(locator)

    return ax


class DrawingAreaGrid:
    @staticmethod
    def make_drawing_area_grid(nrow, ncol, px, py):
        """
        px, py : size of the drawing aread
        """
        boxes = []
        for irow in range(nrow):
            _boxes = [DrawingAreaBase(px, py, 0, 0) for icol in range(ncol)]
            boxes.append(_boxes)

        _packed = [HPacker(children=_b, align="center", pad=0, sep=5) for _b in boxes]

        packed = VPacker(children=_packed, align="center", pad=0, sep=5)

        return boxes, packed

    def __init__(self, nrow, ncol, px, py):
        boxes, packed = self.make_drawing_area_grid(nrow, ncol, px, py)
        self.boxes = boxes
        self.packed = packed

    def get_box_list(self):
        return [b for bl in self.boxes for b in bl]


class GuiBox:
    def __init__(self, fig, ax, width, line_height=20, **kwargs):
        self._fig = fig
        self._ax = ax
        # self._agg_renderer = get_agg_renderer(fig)

        self._width = width
        self._line_height = line_height

        pad = kwargs.pop("pad", 0)
        sep = kwargs.pop("sep", 0)

        self._widgets = []
        self._gui_elements = []
        self.pack = VPacker(children=self._gui_elements, pad=pad, sep=sep, **kwargs)

        self.axlist = []

    def set_axlist_visibility(self, v):
        for ax in self.axlist:
            ax.set_visible(v)

    def _add_axes_box(self, box):
        locator = OffsetBoxLocator(box)
        ax = Axes(self._fig, [0, 0, 1, 1], animated=True)
        self._fig.add_axes(ax)
        ax.set_axes_locator(locator)

        self.axlist.append(ax)

        return ax

    def _append_box(self, height):
        box = DrawingAreaBase(self._width, height, 0, 0)
        self._gui_elements.append(box)
        return box

    def append_label(self, label):

        t = TextArea(label)
        t.set_figure(self._fig)

        self._gui_elements.append(t)

        return t

    def append_labeled_textbox(self, label, width, height, initial_text="TEXT"):
        """
        with & height for the label.
        """
        # We use DrawingArea, instead of TextArea, to have a fixed width.
        labelbox = DrawingArea(width, height, 0, 0)
        labelbox.set_figure(self._fig)
        # For now, we use va=center. ba=baseline does not work okay as is
        # and need to be improved.
        p = Text(width, height / 2.0, label, va="center", ha="right")
        labelbox.add_artist(p)

        # pe = [path_effects.Stroke(linewidth=3, foreground='0.9'),
        #       path_effects.Normal()]
        # p.set_path_effects(pe)

        box = DrawingAreaBase(self._width - width - 5, height, 0, 0)
        ax = self._add_axes_box(box)
        text_box = TextBox(ax, "", initial=initial_text)

        b = [labelbox, box]
        packed = HPacker(children=b, align="center", pad=0, sep=5)
        self._gui_elements.append(packed)
        self._widgets.append(text_box)

        return text_box

    def _append_labeld_box_d(self, label, height, initial_text="TEXT"):

        t = TextArea(label)

        t.set_figure(self._fig)
        renderer = get_renderer(self._fig)
        w_ = t.get_window_extent(renderer).width
        w = w_ / renderer.points_to_pixels(1.0)

        # text_box.on_submit(submit)

        box = DrawingAreaBase(self._width - w - 5, height, 0, 0)
        ax = self._add_axes_box(box)
        text_box = TextBox(ax, "", initial=initial_text)

        b = [t, box]
        packed = HPacker(children=b, align="center", pad=0, sep=5)
        self._gui_elements.append(packed)

        return text_box

    def append_radio_buttons(self, labels, active, values=None):
        box = self._append_box(self._line_height * len(labels))
        ax = self._add_axes_box(box)

        radioButtons = RadioButtons(ax, labels, active=active, values=values)
        self._widgets.append(radioButtons)

        return radioButtons

    def append_check_buttons(self, labels, values):
        box = self._append_box(self._line_height * len(labels))
        ax = self._add_axes_box(box)

        checkButtons = CheckButtons(ax, labels, values)
        self._widgets.append(checkButtons)

        return checkButtons

    def append_button(self, label):
        box = self._append_box(self._line_height)
        ax = self._add_axes_box(box)

        btn = Button(ax, label)
        self._widgets.append(btn)

        return btn

    def append_text_box(self, label, initial_text):
        box = self._append_box(self._line_height)
        ax = self._add_axes_box(box)

        text_box = TextBox(ax, "Evaluate", initial=initial_text)
        self._widgets.append(text_box)

        return text_box


class AnnotationdGuiBoxSimple(AnnotationBbox):
    def __init__(
        self,
        fig,
        ax,
        artist=None,
        xy=(0.5, 0.5),
        xybox=(0, 0),
        box_alignment=(0.5, 0.5),
        *kl,
        **kw
    ):

        self.gui = GuiBox(fig, ax, *kl, **kw)
        self.gui_visible = True

        if artist is None:
            artist = ax

        AnnotationBbox.__init__(
            self,
            self.gui.pack,
            xy=xy,
            xybox=xybox,
            xycoords=artist,
            boxcoords="offset points",
            box_alignment=box_alignment,
            pad=0.3,
        )
        self.set_animated(True)
        self.set_figure(fig)

    def _trigger_redraw(self):
        self.figure.canvas.draw()

    def set_figure(self, fig):
        self.figure = fig

    def install(self, widget_set):
        widget_set.install_widgets(self.gui)
