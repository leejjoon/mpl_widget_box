import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            WidgetBoxManager,
                            install_widgets_simple)

from cbar_composite_widget import CbarSelectorWidget


if True:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(num=2, clear=True)

    arr = np.arange(100).reshape((10, 10))
    im = ax.imshow(arr)

    cbar_selector = CbarSelectorWidget("csw")
    widgets = [cbar_selector,
               W.Button("btn1", "Click", centered=True, tooltip="test")]


    def cb(wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status):

        if cbar_selector.process_event(wbm, ev, status, im):
            # process_event should return True if the event was processed by
            # the method.
            pass

        else:
            print(ev, status)

    wbm = install_widgets_simple(ax, widgets, cb)

    # We need to initailize the widget with the cmap name of the image. FIXME:
    # The norm also need to be initailized.
    cm_name = im.get_cmap().name
    cbar_selector.update_cbar_widget(wbm, cm_name)

    plt.show()
