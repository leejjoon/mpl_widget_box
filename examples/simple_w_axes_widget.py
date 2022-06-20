import numpy as np

import matplotlib.pyplot as plt

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


def setup_axes_widgets(wbm, ax, artist=None):
    # from mpl_widget_box.axes_widget_manager2 import WidgetBoxManager
    from mpl_widget_box.axes_widget_base import AnnotationdGuiBoxSimple
    from mpl_widget_box.axes_widget_manager2 import (WidgetSet, Input, Button)
    # im = ax.imshow([[1, 2], [3, 4]], interpolation="none")

    fig = ax.figure

    box = AnnotationdGuiBoxSimple(fig, ax, width=80,
                                  artist=artist,
                                  xy=(1, 0),
                                  box_alignment=(0, 1))

    def on_change(w, kl, user_params):
        # vmax = float(user_params["vmax"])
        # im.set_clim(0, vmax)
        print(w, kl, user_params)

        fig.canvas.draw_idle()

    widgets = [
        Input("vmax", value="30", label="vmax",
              on_trigger=on_change),
        Input("vmin", value="-10", label="vmin",
              on_trigger=on_change),
        Button("Save & Quit", on_trigger=on_change)
    ]

    ws = WidgetSet(widgets)
    box.install(ws)

    # # ws.install_widgets(widgets)

    # def draw_animated_artist(*kl, **kwargs):
    #     ax.draw_artist(box)
    #     for _ax in box.gui.axlist:
    #         _ax.draw_artist(_ax)

    #     fig = ax.figure
    #     fig.canvas.blit()
    #     fig.canvas.draw_idle()
    #     # fig.canvas.flush_events()

    class Test():
        def __init__(self, box):
            self.box = box

        def purge_background(self):
            pass

        def draw(self, renderer):
            self.box.draw(renderer)
            for _ax in box.gui.axlist:
                _ax.draw_artist(_ax)
            # ax.draw_artist(renderer)

    # wbm._foreign_widgets.append(Test(box))
    wbm.add_foreign_widget(Test(box))
    # cid = fig.canvas.mpl_connect("draw_event", draw_animated_artist)


def test1():


    fig, ax = plt.subplots(num=2, clear=True)
    ax.set_aspect(1.)
    ax.plot(np.random.rand(10), np.random.rand(10))

    wbm = WidgetBoxManager(fig)

    btn = Button("btn1", "Click", centered=True, tooltip="Tooltip")
    widgets = [
        Title("title0", "My Widgets"),
        btn,
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

    setup_axes_widgets(wbm, ax, artist=btn.button_box.patch)

    plt.show()
    return wbm


if __name__ == "__main__":
    test1()
