"""A simple gui widgets for matplotlib with a legend-like layout.

.. image:: https://user-images.githubusercontent.com/95962/180644553-9de7a6cf-8ad4-44fc-9aab-60138886ccd8.gif
           :align: right

mpl_widget_box is a gui-neutral widgets for matplotlib, that work for any of
the GUI backends. While Matplitlib does support gui-neutral widgets, it doesn't
try to be too smart with respect to layout. The mpl_widget_box try to be
smarter using the OffsetBox that powers Matplotlib's legends and annotations.

Features
--------

  * Gui-neutral widgets for Matplotlib
  * Layout behavior similar to legends.
  * Widgets are designed to minimize screen real estate when needed (e.g.,
    tooltips, dropdowns, popups, collapsable menu.).
  * Uses FontAwesome icons
  * Some of the Original Matplotlib's widgets are incorporated (e.g., Slider)
  * A single callback function that is called for any button-press events.

A Simple Example
----------------

`mpl_widget_box` defines its own set of widgets. To use those widgets, you
first define a list of widgets and create an instance of `WidgetBoxManger`
which will install the widgets to an axes and control them. For simplicity, we
provide a helper function of `install_widgets_simple` which, given a list of
widgets, creates a `WidgetBoxManger` instance under the hood and calls relevant
functions to install widgets to an axes. In most cases, a callback function
should be provided which will be triggered whenever an event occurs::

    import matplotlib.pyplot as plt
    from mpl_widget_box import (widgets as W,
                                install_widgets_simple)

    fig, ax = plt.subplots()
    ax.plot([0, 1])

    # Widgets to be added.
    widgets = [
        W.Button("btn", "Button"),
    ]

    # A callback function which will be bound to any button-press event.
    def cb(wbm, ev, status):
        if ev.wid == "btn":
            print("Button is pressed.")

    install_widgets_simple(ax, widgets, cb)

    plt.show()

.. image:: https://user-images.githubusercontent.com/95962/180644581-73167b90-fda4-412f-a5dc-920d59d18d5d.png


Install
-------

It is still in heavy development and is not available at pypi yet.
You may pip instal directly from the github repo,

"""

__version__ = "0.1.0"

from .widget_box import WidgetBoxManager, install_widgets_simple

__all__ = ["WidgetBoxManager", "install_widgets_simple"]
