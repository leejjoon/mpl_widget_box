__version__ = "0.1.0"

from .widget_box import WidgetBoxManager

__all__ = ["install_widgets", "WidgetBoxManager"]


def install_widgets_simple(ax, widgets, cb=None, loc=2):

    wbm = WidgetBoxManager(ax.figure)

    wbm.add_anchored_widget_box(
        widgets,
        ax,
        loc=loc,
    )

    if cb is not None:
        wbm.set_callback(cb)

    wbm.install_all()
    wbm.draw_idle()

    return wbm
