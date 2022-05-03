"""
AnchoredGuiBox is the top level cobject.
It contains a list of widgets.
The 'install' method need to be called explicitly. It will add artists to the
axes and setup the event handling.
"""

import logging

import operator

from matplotlib.offsetbox import (OffsetBox,
                                  AnnotationBbox,
                                  DrawingArea, TextArea,
                                  OffsetImage)

from widgets import HPacker, VPacker

from widgets import (WidgetBoxEvent,
                     Title, Label, Button, CheckBox, Radio, Sub, Dropdown)

from event_handler import (WidgetBoxEventHandler,
                           EventHandlerBase, WidgetsEventHandler)


class WidgetBoxManager():
    def __init__(self, fig, callback=None, **kw):
        self._container_list = []
        # self._wb_list = []
        self.fig = fig

        self.useblit = kw.pop("useblit", True)
        self.background = None
        self._callback = callback

        self._cid_list = {}

        self._ephemeral_containers = {}

    def set_callback(self, callback):
        self._callback = callback

    def add_container(self, container, zorder=0):
        self._container_list.append((zorder, container))

    def remove_container(self, container):
        for z, c in self._container_list:
            if c is container:
                break
        else:
            raise RuntimeError("no container found")

        self._container_list.remove((z, c))

    def add_anchored_widget_box(self, widgets, ax,
                                xy=(0, 1), xybox=(10, -10),
                                # callback=None,
                                # install_args=None,
                                zorder=0):

        wc = AnchoredWidgetContainer(widgets, ax,
                                     xy=xy, xybox=xybox,
                                     #install_args=install_args
                                     )

        self.add_container(wc, zorder=zorder)

    def add_sub_widget_box(self, widgets, ax,
                           sticky=True, artist=None,
                           xy=(1, 1), xybox=(10, -10),
                           zorder=0):

        sub = SubGuiBox(widgets, ax,
                        artist=artist,
                        xy=xy, xybox=xybox,
                        )

        self.add_container(sub, zorder=zorder)

        sub.install()

        return sub

    def install_all(self):

        for zorder, wc in self._container_list:
            if not wc.installed():
                wc.install()

        cid = self.fig.canvas.mpl_connect('button_press_event',
                                          self.handle_event_n_draw)
        self._cid_list["button_press_event"] = cid

        cid = self.fig.canvas.mpl_connect('draw_event',
                                          self.save_n_draw)
        self._cid_list["draw_event"] = cid

    def handle_callback(self, event, e):
        wid = e.wid
        callback_info = e.callback_info
        if callback_info["command"] == "add_sub":
            a = callback_info["a"]
            ax = a.axes or event.inaxes

            if ax is None:
                # print("ax is None, skip.")
                return

            if wid in self._ephemeral_containers:
                c = self._ephemeral_containers[wid]
                self.remove_container(c)
                del self._ephemeral_containers[wid]
            else:

                widgets = callback_info["widgets"]
                c = self.add_sub_widget_box(widgets, ax,
                                            artist=a,
                                            sticky=True,
                                            xy=(1, 1), xybox=(10, -10),
                                            zorder=10)
                self._ephemeral_containers[wid] = c

    def handle_event_n_draw(self, event):
        for zorder, c in sorted(self._container_list,
                                key=operator.itemgetter(0), reverse=True):
            e = c.handle_event(event, parent=self)
            if e is not None:
                break
        else:
            e = None

        if e and e.callback_info:
            self.handle_callback(event, e)

        if e is not None and e.wid is not None:
            if self._callback is not None:
                status = self.get_status()
                # print(status)
                self._callback(self, e, status)

        self.draw_widgets(event)

    def savebg(self, event):
        canvas = self.fig.canvas
        if self.useblit:
            self.background = canvas.copy_from_bbox(self.fig.bbox)

    def save_n_draw(self, event):
        self.savebg(event)
        self.draw_child_containers(event)

    def draw_widgets(self, event):
        if self.useblit:
            if self.background is not None:
                self.fig.canvas.restore_region(self.background)
                self.draw_child_containers(event)
                self.fig.canvas.blit(self.fig.bbox)

    def draw_child_containers(self, event):
        for zorder, c in self._container_list:
            c.draw_widgets(event)

    def get_status(self):
        status = {}
        for zorder, c in self._container_list:
            status.update(c.get_status())

        return status

# containers can have multiple widget_boxes.

class WidgetBoxContainerBase():
    def __init__(self):
        # if wb_list is None:
        #     wb_list = []
        self._wb_list = []
        self._installed = False

    def append_widget_box(self, widget_box, zorder=0):
        self._wb_list.append((zorder, widget_box))

    def iter_wb_list(self, reverse=False):
        for zorder, wb in sorted(self._wb_list,
                                 key=operator.itemgetter(0), reverse=reverse):
            yield zorder, wb

    def handle_event(self, event, parent=None):
        for zorder, wb in sorted(self._wb_list,
                                key=operator.itemgetter(0), reverse=True):
            e = wb.handle_event(event, parent=parent)
            if e is not None:
                break
        else:
            e = None

        return e

    def get_draw_widget_method(self):
        pass

    def draw_widgets(self, event):
        if not self.installed:
            raise RuntimeError("need to be installed before drawing")

        self.draw_container(event)
        for zorder, wb in self.iter_wb_list(reverse=False):
            # self.draw_widget(w, event)
            wb.draw_widgets(event,
                            draw_method=self.get_draw_widget_method())

    def get_status(self):
        status = {}
        for zorder, wb in self.iter_wb_list(reverse=False):
            # self.draw_widget(w, event)
            s = wb.get_status()
            status.update(s)

        return status

    def draw_container(self, event):
        pass

    def install(self):
        self._installed = True

    def uninstall(self):
        self._installed = False

    def installed(self):
        return self._installed


class AxesWidgetBoxContainer(WidgetBoxContainerBase):
    # A simple axes-based container class which contains a single widget-box.

    def __init__(self, widget_box, ax):

        WidgetBoxContainerBase.__init__(self)

        self.ax = ax

        self.append_widget_box(widget_box)

        self.gui_visible = True

        self.sub = None
        self.sub_callback = None

        self._cached_widgets = None

    def get_draw_widget_method(self):
        return self.ax.draw_artist

    def install(self):

        for zorder, wb in self.iter_wb_list():
            self.ax.add_artist(wb.get_artist())

        super().install()

        return self

    def uninstall(self):
        super().uninstall()
        self.ax = None


class AnchoredWidgetContainer(AxesWidgetBoxContainer):
    def __init__(self, widgets, ax,
                 artist=None, xy=(0, 1), xybox=(0, 0)):

        widget_box = self._make_widget_box(widgets, ax,
                                           artist=artist, xy=xy, xybox=xybox)
        super().__init__(widget_box, ax)

    def _make_widget_box(self, widgets, ax,
                         artist=None, xy=(0, 1), xybox=(0, 0)):

        _widget_box = AnchoredWidgetBox(widgets, ax,
                                        artist=artist, xy=xy, xybox=xybox)

        return _widget_box


class SubGuiBox(AnchoredWidgetContainer):
    pass


# WidgetBox should contain a single box
class WidgetBoxBase():
    def __init__(self, widgets):

        self._widgets = widgets
        self._handler = WidgetsEventHandler(widgets)

        self.box = self.wrap(widgets)

    def get_artist(self):
        return self.box

    def wrap(self, widgets):
        _pack = VPacker(children=widgets,
                        pad=3, sep=3,
                        # **kwargs
                        )

        wrapped = HPacker(children=[_pack], pad=0, sep=0)

        return wrapped

    def get_widgets(self):
        return self._widgets

    def handle_event(self, event, parent=None):

        e = self._handler.handle_event(event, parent=parent)

        return e

    def get_status(self):

        status = dict((w.wid, dict(widget=w, status=w.get_status()))
                      for w in self.get_widgets() if hasattr(w, "wid"))

        return status

    def draw_widgets(self, event, draw_method):
        draw_method(self.box)


class AnchoredWidgetBox(WidgetBoxBase):
    def __init__(self, widgets, ax, artist=None, xy=(0, 1), xybox=(0, 0)):

        install_args = dict(artist=artist, xy=xy, xybox=xybox)

        self._install_args = install_args
        self.ax = ax

        super().__init__(widgets)

    def wrap(self, widgets):
        _pack = VPacker(children=widgets,
                        pad=3, sep=3,
                        )
        box = HPacker(children=[_pack], pad=0, sep=0)
        wrapped = self._make_wrapped_widget_box(self.ax, box,
                                                **self._install_args)
        return wrapped

    def _make_wrapped_widget_box(self, ax, box,
                                 artist=None, xy=(0, 1), xybox=(0, 0)):
        if artist is None:
            artist = ax

        wrapped_box = AnnotationBbox(box, xy=xy,
                                     xybox=xybox,
                                     xycoords=artist,
                                     boxcoords="offset points",
                                     box_alignment=(0, 1),
                                     pad=0.3,
                                     animated=True)
        return wrapped_box


def test1():
    import numpy as np

    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                      AnnotationBbox)

    # plt.rcParams["font.family"] = "sans-serif"
    # plt.rcParams["font.sans-serif"] = ["Source Code Pro"]

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot(np.random.rand(10))

    wbm = WidgetBoxManager(fig)

    sub_widgets = [Label("btn4", "-- Label --"),
                   Radio("radio2", ["Ag3", "Bc3"]),
                   ]

    widgets = [
        Title("title0", "My Widgets"),
        Sub("sub1", "Sub", sub_widgets),
        Dropdown("sub1", "Sub", sub_widgets),
        # Label("btn3", "-- Label --"),
        Radio("radio", ["Ag", "Bc"]),
        # Label("btn3", "-- Label --"),
        CheckBox("check", ["1", "2", "3"], title="Check"),
        Button("btn1", "   Click   "),
    ]

    wbm.add_anchored_widget_box(widgets, ax,
                                xy=(0, 1), xybox=(10, -10),
                                # callback=cb
                                )

    def cb(wb, event, status):
        pass
        # print(status)

    wbm.set_callback(cb)

    wbm.install_all()

    plt.show()
    return wbm


if __name__ == '__main__':
    test1()
