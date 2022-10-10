from abc import abstractmethod
from .widget_box import WidgetBoxManager
from . import widgets as W
from ._abc import CompositeWidgetBase

from .fa_icons import fa_icons

from .fa_helper import FontAwesome
from .base_widget import TextArea

get_icon_fontprop = FontAwesome.get_fontprop



class TitleCollapsableBase(CompositeWidgetBase):
    EXPAND = fa_icons["caret-down"]
    COLLAPSE = fa_icons["caret-up"]

    def __init__(self, wid, title):
        self.wid = wid
        self.title = title

        self._populate_buttons()
        self._button = None

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

    @abstractmethod
    def check_collapsed(self) -> bool:
        pass

    @abstractmethod
    def collapse_widgets(self, wbm, wc):
        pass

    @abstractmethod
    def expand_widgets(self, wbm, wc):
        pass

    def process_event(self, wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status: dict):
        if ev.wid == f"{self.wid}:btn":
            wc = ev.container_info["container"]

            if not self.check_collapsed():
                self.collapse_widgets(wbm, wc)
            else:
                self.expand_widgets(wbm, wc)

            return True


class TitleCollapsable(TitleCollapsableBase):

    def __init__(self, wid, title):
        super().__init__(wid, title)
        self._widgets_orig = []


    def check_collapsed(self):
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



class TitleCollapsableWithVisibility(TitleCollapsableBase):

    def __init__(self, wid, title, start_collapsed=False):
        super().__init__(wid, title)

        self._widgets_to_collapse = []
        self._is_collapsed = start_collapsed

    def check_collapsed(self):
        return self._is_collapsed

    def set_widgets_to_collapse(self, widgets_to_collapse):
        self._widgets_to_collapse = widgets_to_collapse

    def _update_button(self):
        if self.check_collapsed():
            self._button.box.set_text(self.EXPAND)
        else:
            self._button.box.set_text(self.COLLAPSE)

    def collapse_widgets(self, wbm, wc):

        for w in self._widgets_to_collapse:
            w.set_visible(False)

        self._is_collapsed = True

        self._update_button()

    def expand_widgets(self, wbm, wc):
        for w in self._widgets_to_collapse:
            w.set_visible(True)

        self._is_collapsed = False
        self._update_button()

    def process_event(self, wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status: dict):

        if ev.wid == "@installed":
            # The composite widget itself can not be searched with wbm.
            # Instead, we search for the button.
            wc, wb = wbm.get_parents_of_wid(self._button.wid)
            assert wb is not None

            self.set_widgets_to_collapse([w for w in wb.widgets_orig
                                          if w is not self])

            return True

        else:
            return super().process_event(wbm, ev, status)
