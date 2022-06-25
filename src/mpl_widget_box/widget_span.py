from matplotlib.offsetbox import HPacker, TextArea
from matplotlib import rcParams
from matplotlib.widgets import SpanSelector as _SpanSelector

import fontawesome

from .widgets import get_icon_fontprop

from .widgets import (
    Radio,
    HWidgets,
    Button,
    CheckBox,
)

from .composite_widget import CompositeWidget


class SpanSelector(_SpanSelector):
    def purge_background(self):
        # we purge the background so that the span saves the current background
        # and use for blitting. Otherwise, the mpl_widget_box will be out of
        # date.
        self.background = None


class Span:
    def __init__(self, ax):

        self.span = None
        self._selected = None
        self.ax = ax

        self.span = SpanSelector(
            self.ax,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.2, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True,
        )

        self.span.set_active(False)

    def select(self):
        self.span.set_active(True)

    def onselect(self, wmin, wmax):
        self._selected = wmin, wmax

    def clear(self):
        self.span.set_active(False)
        self.span.clear()
        canvas = self.ax.figure.canvas
        canvas.draw_idle()

    def set_current_extents(self, extents):
        self.span.extents = extents
        self.span.set_visible(True)

    def get_current_extents(self):
        return self.span.extents

    def draw(self, renderer):
        if self.span is not None:
            artists = sorted(
                self.span.artists,
                # FIXME : check the implementation of matplotlib. Newer version needs _get_animated_artists.
                # + self.span._get_animated_artists()
                key=lambda a: a.get_zorder(),
            )
            for a in artists:
                a.draw(renderer)

    def purge_background(self):
        self.span.purge_background()


class SpanSelectors(Span, CompositeWidget):
    def __init__(self, ax, rootname, labels=[], values=None):
        Span.__init__(self, ax)
        self.rootname = rootname
        self.labels = labels
        self.values = values or labels

        self.extents_dict = {}

        self.markers_selected = None

        # FIXME: its length needs to be modified according to the label length
        self.marker_colors = rcParams["axes.prop_cycle"].by_key()["color"]

        self.marker_unset_color = "0.7"

        self.span_selection_bars = SpanSelectionBars(ax, self)

    def _make_hpacker(self, l):

        SELECTED_ON = fontawesome.icons["clipboard-check"]
        fontprop_solid = get_icon_fontprop(family="solid", size=10)

        button = TextArea(
            SELECTED_ON,
            textprops=dict(
                fontproperties=fontprop_solid, color=self.marker_unset_color
            ),
        )

        box = HPacker(children=[TextArea(l), button], pad=1, sep=4, align="baseline")

        return box, button

    # widget-related
    def build_widgets(self):
        label_widgets = []
        selection_markers = []

        for l in self.labels:
            box, button = self._make_hpacker(l)
            label_widgets.append(box)
            selection_markers.append(button)

        self.markers_selected = selection_markers

        self.selector = Radio(
            self._prefixed_name("sel"), label_widgets, values=self.values
        )

        widgets = [
            # CheckBox(self._prefixed_name("edit"),
            #          ["Show & Edit"], values=["edit"]),
            self.selector,
            HWidgets(
                children=[
                    Button(self._prefixed_name("store"), "Store"),
                    Button(self._prefixed_name("purge"), "Purge"),
                ]
            ),
        ]

        return widgets

    def post_install(self, wbm):
        wbm._foreign_widgets.append(self.span_selection_bars)
        wbm._foreign_widgets.append(self)
        self.initailize()

        for i, v in enumerate(self.values):
            x1, x2 = self.extents_dict.get(v, (None, None))
            self._update_selector_label(i, x1, x2)

    def post_uninstall(self, wbm):
        wbm._foreign_widgets.remove(self.span_selection_bars)
        wbm._foreign_widgets.remove(self)
        self.clear()

    def initailize(self):
        self.select()
        # sel = self._prefixed_name("sel")

        s = self.selector.get_status()

        saved_extent = self.extents_dict.get(s["value"], (0, 0))
        self.set_current_extents(saved_extent)

    def process_event(self, wb, ev, status):

        if ev.wid in [self._prefixed_name("sel")]:
            # if "edit" in status[self._prefixed_name("edit")]["values"]:
            self.initailize()

        elif ev.wid == self._prefixed_name("store"):
            sel = self._prefixed_name("sel")
            x1, x2 = self.get_current_extents()
            if (x1, x2) == (0, 0):
                return
            self.extents_dict[status[sel]["value"]] = x1, x2
            i = status[sel]["selected"][0]
            self._update_selector_label(i, x1, x2)

        elif ev.wid == self._prefixed_name("purge"):
            self.set_current_extents((0, 0))

            sel = self._prefixed_name("sel")
            i = status[sel]["selected"][0]
            self._update_selector_label(i, None, None)

            self.extents_dict[status[sel]["value"]] = (0, 0)

    def _update_selector_label(self, i, x1, x2):
        if (x1, x2) == (None, None):
            c = self.marker_unset_color
        else:
            c = self.marker_colors[i]
        self.markers_selected[i]._text.set_color(c)

    def _prefixed_name(self, n):
        return f"{self.rootname}:{n}"


class SpanSelectionBars:
    """
    This draws bars at the top of the axes showing the current
    span selections.
    """

    def __init__(self, ax, span):
        import matplotlib.lines as mlines
        import matplotlib.transforms as mtransforms

        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
        ann = mlines.Line2D([0, 0, 0, 0], [1.02, 1.04, 1.04, 1.02])
        ann.set_transform(trans)
        ax._set_artist_props(ann)

        self.span = span
        self.ann = ann

    def draw(self, renderer):
        for i, v in enumerate(self.span.values):
            if v in self.span.extents_dict:
                x1, x2 = self.span.extents_dict[v]
                c = self.span.marker_colors[i]
                self.ann.set_color(c)
                self.ann.set_xdata([x1, x1, x2, x2])
                self.ann.draw(renderer)

    def purge_background(self):
        pass
