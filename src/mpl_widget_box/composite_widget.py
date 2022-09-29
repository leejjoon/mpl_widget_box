from .widget_box import WidgetBoxManager
from . import widgets as W
from ._abc import CompositeWidgetBase

from .fa_icons import fa_icons

from .fa_helper import FontAwesome
from .base_widget import TextArea

get_icon_fontprop = FontAwesome.get_fontprop


class TitleCollapsable(CompositeWidgetBase):
    EXPAND = fa_icons["caret-down"]
    COLLAPSE = fa_icons["caret-up"]

    def _populate_buttons(self):
        color = "red"

        fontprop_solid = get_icon_fontprop(family="solid", size=10)
        self.button_expand = TextArea(
            self.EXPAND, textprops=dict(fontproperties=fontprop_solid,
                                        color=color)
        )
        self.button_collapse = TextArea(
            self.COLLAPSE, textprops=dict(fontproperties=fontprop_solid,
                                          color=color)
        )

    def __init__(self, wid, title):
        self.wid = wid
        self.title = title
        self._widgets_orig = []

        self._populate_buttons()
        self._button = None

    def build_widgets(self):

        self._button = W.Label(f"{self.wid}:btn", self.button_collapse)
        r = [
            W.HWidgets(
                [
                    W.Title(f"{self.wid}:title", self.title),
                    self._button,
                ],
                align="baseline",
            ),
        ]
        return r

    def post_install(self, wbm):
        pass

    def post_uninstall(self, wbm):
        pass

    def is_collapsed(self):
        return len(self._widgets_orig)

    def collapse_widgets(self, wbm, wc):
        widgets = [
            self,
        ]

        wb = wc.get_widget_box()
        self._widgets_orig = wb.widgets_orig

        self._button.get_children()[0] = self.button_expand

        self._button.box.set_text(self.EXPAND)
        wc.reinit_widget_box(wbm, widgets)

    def expand_widgets(self, wbm, wc):
        widgets = self._widgets_orig
        self._widgets_orig = []

        self._button.box.set_text(self.COLLAPSE)
        wc.reinit_widget_box(wbm, widgets)

    def process_event(self, wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status: dict):
        if ev.wid == f"{self.wid}:btn":
            wc = ev.container_info["container"]

            if not self.is_collapsed():
                self.collapse_widgets(wbm, wc)
            else:
                self.expand_widgets(wbm, wc)

            return True
