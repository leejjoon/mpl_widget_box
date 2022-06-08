import numpy as np

import matplotlib.pyplot as plt
from mpl_widget_box.composite_widget import CompositeWidget

from mpl_widget_box.widget_box import WidgetBoxManager

from mpl_widget_box.widgets import (
    Sub,
    Title,
    Label,
    Radio,
    Dropdown,
    HWidgets,
    DropdownMenu,
    HPacker,
    Button,
    ButtonBar,
    CheckBox,
    HWidgets,
)


# def setup_axes_widgets(wbm, ax, artist=None):
#     # from mpl_widget_box.axes_widget_manager2 import WidgetBoxManager
#     from mpl_widget_box.axes_widget_base import AnnotationdGuiBoxSimple
#     from mpl_widget_box.axes_widget_manager2 import (WidgetSet, Input, Button)
#     # im = ax.imshow([[1, 2], [3, 4]], interpolation="none")

#     fig = ax.figure

#     box = AnnotationdGuiBoxSimple(fig, ax, width=80,
#                                   artist=artist,
#                                   xy=(1, 0),
#                                   box_alignment=(0, 1))

#     def on_change(w, kl, user_params):
#         # vmax = float(user_params["vmax"])
#         # im.set_clim(0, vmax)
#         print(w, kl, user_params)

#         fig.canvas.draw_idle()

#     widgets = [
#         Input("vmax", value="30", label="vmax",
#               on_trigger=on_change),
#         Input("vmin", value="-10", label="vmin",
#               on_trigger=on_change),
#         Button("Save & Quit", on_trigger=on_change)
#     ]

#     ws = WidgetSet(widgets)
#     box.install(ws)

#     # # ws.install_widgets(widgets)

#     # def draw_animated_artist(*kl, **kwargs):
#     #     ax.draw_artist(box)
#     #     for _ax in box.gui.axlist:
#     #         _ax.draw_artist(_ax)

#     #     fig = ax.figure
#     #     fig.canvas.blit()
#     #     fig.canvas.draw_idle()
#     #     # fig.canvas.flush_events()

#     class Test():
#         def __init__(self, box):
#             self.box = box

#         def purge_background(self):
#             pass

#         def draw(self, renderer):
#             self.box.draw(renderer)
#             for _ax in box.gui.axlist:
#                 _ax.draw_artist(_ax)
#             # ax.draw_artist(renderer)

#     # wbm._foreign_widgets.append(Test(box))
#     wbm.add_foreign_widget(Test(box))
#     # cid = fig.canvas.mpl_connect("draw_event", draw_animated_artist)

from mpl_widget_box.axes_widget import TextAreaWidget, SliderWidget

if True:

    fig, ax = plt.subplots(num=2, clear=True)
    ax.set_aspect(1.)
    ax.plot(np.random.rand(10), np.random.rand(10))

    wbm = WidgetBoxManager(fig)


    btn = Button("btn1", "Click", centered=True, tooltip="Tooltip")
    aw1 = TextAreaWidget("input_min",
                         60, 16,
                         "123", label="MIN")
    slider1 = SliderWidget("slider1",
                           60, 16,
                           label="Slide")
    # aw2 = CompositeAxesWidget("test2", "456")

    widgets = [
        Title("title0", "My Widgets"),
        aw1,
        slider1,
        btn,
        # aw2
        # HWidgets(children=[Label("test1", "Test1"), aw1], align="center"),
        # HWidgets(children=[Label("test2", "Test2"), aw2], align="center")
    ]

    wbm.add_anchored_widget_box(
        widgets,
        ax,
        loc=2,
        # callback=cb
    )

    def cb(wb, ev, status):
        if ev.wid == "btn1":
            print("clicked")
        print(ev.wid, status)

    wbm.set_callback(cb)

    wbm.install_all()

    # aw1.add_axes_box()
    # wbm.add_foreign_widget(aw1)
    # aw2.add_axes_box()
    # wbm.add_foreign_widget(aw2)

    plt.show()

# if False:

#     fig, ax = plt.subplots(num=2, clear=True)
#     ax.set_aspect(1.)
#     ax.plot(np.random.rand(10), np.random.rand(10))

#     wbm = WidgetBoxManager(fig)

#     btn = Button("btn1", "Click", centered=True, tooltip="Tooltip")
#     widgets = [
#         Title("title0", "My Widgets"),
#         btn,
#     ]

#     wbm.add_anchored_widget_box(
#         widgets,
#         ax,
#         loc=2,
#         # callback=cb
#     )

#     def cb(wb, ev, status):
#         if ev.wid == "btn1":
#             print("clicked")
#         print(ev.wid, status)

#     wbm.set_callback(cb)

#     wbm.install_all()

#     setup_axes_widgets(wbm, ax, artist=btn.button_box.patch)

#     plt.show()


