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

def test1():


    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot(np.random.rand(10))

    wbm = WidgetBoxManager(fig)

    sub_widgets = [
        Label("btn4", "-- Label --"),
        Radio("radio2", ["Ag3", "Bc3"]),
    ]

    widgets = [
        Title("title0", "My Widgets"),
        Sub("sub1", "Sub", sub_widgets, tooltip="Sub"),
        # Dropdown("dropdown", "Dropdown", ["123", "456"]),
        HWidgets(
            children=[
                Label("label2", "dropdow"),
                Dropdown("dropdown", "Dropdown", ["123", "456"]),
            ],
            align="baseline",
        ),
        # Label("btn3", "-- Label --"),
        Radio("radio", ["Ag", "Bc"]),
        # Label("btn3", "-- Label --"),
        CheckBox("check", ["1", "2", "3"], title="Check"),
        Button("btn1", "Click", centered=True, tooltip="Tooltip"),
        HWidgets(children=[Button("btn2", "A"), Button("btn3", "B")]),
    ]

    wbm.add_anchored_widget_box(
        widgets,
        ax,
        loc=2,
        # callback=cb
    )

    def cb(wb, ev, status):
        print(ev, status)

    wbm.set_callback(cb)

    wbm.install_all()

    plt.show()
    return wbm


if __name__ == "__main__":
    test1()
