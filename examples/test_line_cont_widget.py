import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box.widget_box import WidgetBoxManager

import mpl_widget_box.widgets as w

from mpl_widget_box.widget_span import Span, SpanSelectors
# from mpl_widget_span import Span

fig, ax = plt.subplots(1, 1, num=1, clear=True)
x = np.linspace(1., 2.5, 100)
y = np.zeros_like(x)
y[len(y)//2] = 1

ax.plot(x, y)


span = SpanSelectors(ax, "line",
                     labels=["line 1", "cont 1", "cont 2"])

subwidgets1 = [
    w.Label("", "My Label"),
    span,
    w.HWidgets(children=[w.Button("zoom", "Zoom into"),
                         w.Button("plot", "Plot")])
]

subwidgets2 = [
    w.Label("", "My Label II"),
    w.HWidgets(children=[w.Button("zoom", "Zoom KK"),
                         w.Button("plot", "KKK")])
]

menu_widget = w.HWidgets(
    children=[
        w.Label("menu", "Menu"),
        w.Dropdown("menu-kind", "", ["----", "menu 1", "menu 2"]),
    ]
)

widgets = [
    menu_widget,
]

wbm = WidgetBoxManager(fig)

wc = wbm.add_anchored_widget_box(
    widgets,
    ax,
    loc=2,
    # callback=cb
)

def cb(wb, ev, status):
    span.process_event(wb, ev, status)

    print(ev)

    if ev.wid == "zoom":
        # fig.canvas.toolbar.push_current()

        toolbar = fig.canvas.toolbar
        # we need this in case the zoom button is pressed before the home is
        # set.
        if toolbar._nav_stack() is None:
            toolbar.push_current()

        x1, x2 = span.get_current_extents()
        dx = x2 - x1
        ax.set_xlim(x1 - dx, x2 + dx)

        fig.canvas.draw_idle()
        # FIXME : If the button is prssed while in the pan mode, the current
        # position pushed twice. This won't work if the button is outside the
        # axes. We need better solution
        if toolbar.mode._navigate_mode != "PAN":
            toolbar.push_current()

    elif ev.wid == "menu-kind:select":
        wb = wc.get_widget_box()
        if status["menu-kind"]["value"] == "menu 1":
            subwidgets = subwidgets1
        elif status["menu-kind"]["value"] == "menu 2":
            subwidgets = subwidgets2
        else:
            subwidgets = []

        widgets = [
            menu_widget,
            *subwidgets
        ]
        wc.reinit_widget_box(wbm, wb, widgets)

    # print(ev, status)

wbm.set_callback(cb)

wbm.install_all()

plt.show()

# ax.annotate("", (1.7, 1.02), xytext=(1.8, 1.02),
#             xycoords=("data", "axes fraction"),
#             textcoords=("data", "axes fraction"),
#             arrowprops=dict(arrowstyle="-",
#                             connectionstyle="bar"),
#             annotation_clip=False
#             )
