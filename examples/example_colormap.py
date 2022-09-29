import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            WidgetBoxManager)

from mpl_widget_box.misc.cbar_composite_widget import CbarSelectorWidget


import matplotlib.pyplot as plt

fig, [ax1, ax2] = plt.subplots(1, 2, figsize=(12, 6))

arr = np.arange(100).reshape((10, 10))
im1 = ax1.imshow(arr)
im2 = ax2.imshow(arr)

cbar_selector1 = CbarSelectorWidget("csw1")  # cbar selector ax1
cbar_selector2 = CbarSelectorWidget("csw2", dir="h")  # for ax2

# for ax1
widgets1 = [cbar_selector1]

# for ax2
widgets2 = [cbar_selector2]

def cb(wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status):

    if cbar_selector1.process_event(wbm, ev, status, im1):
        # process_event should return True if the event was processed by
        # the method.
        pass
    elif cbar_selector2.process_event(wbm, ev, status, im2):
        pass

    else:
        print(ev, status)


wbm = WidgetBoxManager(fig)
wbm.add_anchored_widget_box(widgets1, ax1, loc=2)
wbm.add_anchored_widget_box(widgets2, ax2, loc=2, direction="h")
wbm.set_callback(cb)
wbm.install_all()

# We initailize the widget with the cmap name of the image. FIXME: The norm
# also need to be initailized.
cbar_selector1.update_cbar_widget(wbm, im1.get_cmap().name)
cbar_selector2.update_cbar_widget(wbm, im2.get_cmap().name)

plt.show()
