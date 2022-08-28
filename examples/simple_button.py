import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)


def main():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot([0, 1])

    widgets = [
        W.Title("title1", "Buttons"),
        W.Button("btn1", "A"),
        W.Button("btn2", "B", align="right"),
        W.Button("btn3", "C", expand=True, align="center"),
        W.Button("btn4", "D", expand=True, tooltip="Tooltip"),
    ]

    def cb(wb, ev, status):
        print(ev, status)

    install_widgets_simple(ax, widgets, cb=cb, loc=2)

    plt.show()


if __name__ == "__main__":
    main()
