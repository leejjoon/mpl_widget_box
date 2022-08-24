import numpy as np

from .. import widgets as W

from ..composite_widget import CompositeWidgetBase


# class OutOfRangeException(Exception):
#     pass


class Index:
    def __init__(self, initial=0, max=None, min=0):
        self.ind = initial
        if max is None:
            self.max = np.inf
        else:
            self.max = max
        self.min = min

    def _check_on_boundary(self):
        return (self.min < self.ind, self.ind < self.max)

    def inc(self, step=1):
        """
        RETURN:
        index
        tuple of boolean : (can decrease, can increase)
        """
        self.ind = np.clip(self.ind + step, self.min, self.max)
        return self.ind, self._check_on_boundary()

    def dec(self, step=1):
        return self.inc(-1 * step)
        # if self.ind > self.min:
        #     self.ind -= 1
        #     return self.ind, (self.ind > self.min, True)
        # else:
        #     raise OutOfRangeException()

    def current(self):
        return self.ind, self._check_on_boundary()


class NavButtons(CompositeWidgetBase):
    def __init__(self, wid, target_list, label_width=20,
                 label_format="{:d}"):
        self.wid = wid
        self.target_list = target_list
        self.ind = Index(max=len(target_list) - 1)
        self.label_width = label_width
        self.label_format = label_format

        self.btn_prev = W.Button(f"{self.wid}:btn-prev", "Prev")
        self.btn_next = W.Button(f"{self.wid}:btn-next", "Next")
        self.lbl = W.Label(f"{self.wid}:lbl", "", fixed_width=self.label_width,
                           draw_frame=True)
        # self._lbl.patch.set_edgecolor("0.5")

    def build_widgets(self):

        widgets = [
            W.HWidgets(
                [self.btn_prev,
                 self.lbl,
                 self.btn_next]
            )
        ]

        return widgets

    def post_install(self, wbm):
        pass

    def post_uninstall(self, wbm):
        pass

    def process_event(self, wbm, ev, status):


        i_old, boundary_check = self.ind.current()

        if ev.wid == f"@installed":
            i, i_old = i_old, None # we need to make i != i_old so that it does
                                   # not return None later.
        elif ev.wid == f"{self.wid}:btn-prev":
            i, boundary_check = self.ind.dec()
        elif ev.wid == f"{self.wid}:btn-next":
            i, boundary_check = self.ind.inc()
        else:
            return None

        if i == i_old:
            return None

        self.lbl.set_label(self.label_format.format(i))

        bp, bn = boundary_check
        self.btn_prev.set_context("default" if bp else "disabled")
        self.btn_next.set_context("default" if bn else "disabled")

        return i

