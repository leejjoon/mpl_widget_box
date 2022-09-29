import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            WidgetBoxManager,
                            install_widgets_simple)

from mpl_widget_box.fa_helper import get_fa_textarea, FontAwesome

# fontawesome icons can be used as a label
_icons = dict(angle_left='\uf104',
              angles_left='\uf100',
              angle_right='\uf105',
              angles_right='\uf101')

from mpl_widget_box.misc.nav_buttons import (Index, CompositeWidgetBase)

class NavButtons(CompositeWidgetBase):
    def __init__(self, wid, target_list, label_width=20,
                 label_format="{cur}/{total}",
                 bigstep=10):
        self.wid = wid
        self.target_list = target_list
        self.ind = Index(max=len(target_list) - 1)
        self.label_width = label_width
        self.label_format = label_format

        self.lbl = W.Label(self._cwid("lbl"), "", fixed_width=self.label_width,
                           align="right")
        self.lbl.patch.set_edgecolor("0.8")

        self.btn_prev = W.Button(self._cwid("btn-prev"),
                                 get_fa_textarea(_icons["angle_left"], "w"),
                                 tooltip="Go to prev.")
        self.btn_backward = W.Button(self._cwid("btn-backward"),
                                     get_fa_textarea(_icons["angles_left"], "w"),
                                     tooltip="Go backward")
        self.btn_forward = W.Button(self._cwid("btn-forward"),
                                    get_fa_textarea(_icons["angles_right"], "w"),
                                    tooltip="Go forward")
        self.btn_next = W.Button(self._cwid("btn-next"),
                                 get_fa_textarea(_icons["angle_right"], "w"),
                                 tooltip="Go to next")

        self.bigstep = bigstep

    def _cwid(self, n):
        "get wid of the child widget"
        return f"{self.wid}:{n}"

    def build_widgets(self):

        widgets = [
            W.HWidgets(
                [self.btn_prev,
                 self.btn_backward,
                 self.lbl,
                 self.btn_forward,
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
        elif ev.wid == f"{self.wid}:btn-backward":
            i, boundary_check = self.ind.dec(self.bigstep)
        elif ev.wid == f"{self.wid}:btn-forward":
            i, boundary_check = self.ind.inc(self.bigstep)
        elif ev.wid == f"{self.wid}:btn-next":
            i, boundary_check = self.ind.inc()
        else:
            return None

        if i == i_old:
            return None

        v = self.target_list[i]
        self.lbl.set_label(self.label_format.
                           format(cur=v, total=len(self.target_list)))

        # we update status to reflect the change.
        status.update({self.lbl.wid: self.lbl.get_status(),
                       self._cwid("ind"): {"index": i, "value": v}})

        bp, bn = boundary_check
        self.btn_prev.set_context("default" if bp else "disabled")
        self.btn_backward.set_context("default" if bp else "disabled")
        self.btn_next.set_context("default" if bn else "disabled")
        self.btn_forward.set_context("default" if bn else "disabled")

        return v


freqs = np.arange(2, 20, 3)
t = np.arange(0.0, 1.0, 0.001)
s = np.sin(2*np.pi*freqs[0]*t)

fig, ax = plt.subplots(num=2, clear=True)
l, = plt.plot(t, s, lw=2)

buttons = [W.Button(f"btn{i:03d}", f"{i:03d}", expand=True, align="center",
                    auxinfo="paged")
           for i in range(100)]
n_per_page = 5
total_pages = (len(buttons) - 1) // n_per_page + 1

widgets = [
    nav_button := NavButtons("nav", range(total_pages), bigstep=5,
                             label_width=30),
    *buttons
]
# W.Button("btn1", "1", expand=True, align="center"),
# W.Button("btn2", "2", expand=True, align="center"),

def cb(wbm, ev: W.WidgetBoxEvent, status):
    # w = wbm.get_widget_by_id("nav")
    v = nav_button.process_event(wbm, ev, status)
    if v is not None:
        for i, btn in enumerate(buttons):
            if v*n_per_page <= i < (v+1)*n_per_page:
                btn.set_visible(True)
            else:
                btn.set_visible(False)

        # l1.set_data(x, np.power(x, v))
        # wbm.draw_idle()

    if ev.auxinfo == "paged":
        print("from paged buttons", ev.wid)

wbm = install_widgets_simple(ax, widgets, cb)

plt.show()
