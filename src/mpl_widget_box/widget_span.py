
from mpl_widget_box.widgets import (
    Radio,
    HWidgets,
    Button,
    CheckBox,
)

from matplotlib.widgets import SpanSelector as _SpanSelector


class SpanSelector(_SpanSelector):
    def purge_background(self):
        print("purging background")
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
            drag_from_anywhere=True
        )

        self.span.set_active(False)

    def select(self):
        self.span.set_active(True)

    def onselect(self, wmin, wmax):
        # print([wmin, wmax], wvl2x([wmin, wmax]))
        self._selected = wmin, wmax

    def clear(self):
        self.span.set_active(False)
        # self.span.extents = (0, 0)
        self.span.clear()
        canvas = self.ax.figure.canvas
        canvas.draw_idle()
        # if self.span is not None:
        #     canvas = self.span.ax.figure.canvas
        #     self.span.clear()
        #     self.span = None
        #     canvas.draw_idle()
        # canvas.draw()
        # canvas.flush_events()

    def set_current_extents(self, extents):
        self.span.extents = extents
        self.span.set_visible(True)

    def get_current_extents(self):
        return self.span.extents

    def draw(self, renderer):
        if self.span is not None:
            artists = sorted(self.span.artists,
                             # FIXME : check the implementation of matplotlib. Newer version needs _get_animated_artists.
                             #+ self.span._get_animated_artists()
                             key=lambda a: a.get_zorder())
            for a in artists:
                a.draw(renderer)

    def purge_background(self):
        self.span.purge_background()


class SpanSelectors(Span):
    def __init__(self, ax, rootname):
        Span.__init__(self, ax)
        self.rootname = rootname
        self.extents_dict = {}

    def _prefixed_name(self, n):
        return f"{self.rootname}:{n}"

    # widget-related
    def build_widgets(self):
        self.selector = Radio(self._prefixed_name("sel"),
                              ["Line 1:[0,0]", "Cont 1:[0,0]", "Cont 2:[0,0]"],
                              # values=[0, 1, 2]),
                              values=["line 1", "cont 1", "cont 2"])

        widgets = [
            CheckBox(self._prefixed_name("edit"),
                     ["Show & Edit"], values=["edit"]),
            self.selector,
            HWidgets(children=[Button(self._prefixed_name("store"),
                                      "Store"),
                               Button(self._prefixed_name("purge"),
                                      "Purge")]),
        ]

        return widgets

    def _update_selector_label(self, i, x1, x2):
        txt = self.selector.box.get_children()[i].get_children()[1]
        prefix = txt.get_text().split(":")[0]
        txt.set_text(f"{prefix}:[{x1:.1f}, {x2:.1f}]")

    def process(self, wb, ev, status):
        if ev.wid in [self._prefixed_name("edit"),
                      self._prefixed_name("sel")]:
            if "edit" in status[self._prefixed_name("edit")]["values"]:
                self.select()
                sel = self._prefixed_name("sel")
                saved_extent = self.extents_dict.get(status[sel]["value"], (0, 0))
                #if saved_extent is not None:
                print("saved", saved_extent)
                self.set_current_extents(saved_extent)
                # canvas = span.span.ax.figure.canvas
                # canvas.draw_idle()
            else:
                self.clear()
        # elif ev.wid == "sel":

        elif ev.wid == self._prefixed_name("store"):
            print("saving")
            sel = self._prefixed_name("sel")
            x1, x2 = self.get_current_extents()
            self.extents_dict[status[sel]["value"]] = x1, x2
            i = status[sel]["selected"][0]
            self._update_selector_label(i, x1, x2)

        elif ev.wid == self._prefixed_name("purge"):
            self.set_current_extents((0, 0))

            sel = self._prefixed_name("sel")
            i = status[sel]["selected"][0]
            self._update_selector_label(i, 0, 0)

            self.extents_dict[status[sel]["value"]] = (0, 0)

