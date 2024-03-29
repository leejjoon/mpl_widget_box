"""
AnchoredGuiBox is the top level cobject.
It contains a list of widgets.
The 'install' method need to be called explicitly. It will add artists to the
axes and setup the event handling.
"""

import logging

import operator

from matplotlib.axes import Axes
from matplotlib.offsetbox import (
    OffsetBox,
    AnnotationBbox as _AnnotationBbox,
    DrawingArea,
    TextArea,
    OffsetImage,
)
import numpy as np

from .widgets import MouseOverEvent, WidgetBoxGlobalEvent
from .widgets import HPacker, VPacker
from .widgets_impl import PackedWidgetBase
from ._abc import CompositeWidgetBase

from .event_handler import WidgetsEventHandler

from typing import List
from .foreign_widget_protocol import ForeignWidgetProtocol


class AnnotationBbox(_AnnotationBbox):
    def draw(self, renderer):
        # docstring inherited
        if renderer is not None:
            self._renderer = renderer
        if not self.get_visible() or not self._check_xy(renderer):
            return
        self.update_positions(renderer)
        self.patch.draw(renderer)
        delayed_draws = self.offsetbox.draw(renderer)  # draw method will return
        # delayed draw methods.
        self.stale = False

        return delayed_draws

class SpaceBar():
    def __init__(self, fig, wbm, widgets=None):
        # self._timer = None
        self.fig = fig

        self._timer = self.fig.canvas.new_timer(interval=1000)
        self._timer.add_callback(self.on_tick)
        self._timer.single_shot = True
        self._timer_started = False

        if widgets is None:
            from . import widgets as W
            widgets = [W.Label("l1", "Space"), W.Label("l2", "Zoom")]

        # FIXME For now, we store wbm instance and trigger it to draw widgets
        # fro, the `on_tick` method. Not sure if this is a good idea.
        self._spacebar = wbm.add_widget_box(
            widgets,
            fig,
            xy=(0.5, 0.),
            xycoords=("figure fraction", "figure fraction"),
            xybox=(0, 10),
            box_alignment=(0.5, 0.),
            frameon=True,
            clip=False,
            direction="h",
        )

        self.wbm = wbm
        self._spacebar.set_visible(False)
        self.callback_customkey = None

    def set_customkey_callback(self, cb):
        """
            def cb_customkey(k):
                ....
                return True

        If the callback function returns True, wbm._callback will be triggered with GlobalEvent with "@key" id.
        """
        self.callback_customkey = cb

    def on_tick(self):
        self._timer_started = False
        self.hide_spacebar()
        from matplotlib.backend_bases import Event
        event = Event("Tick", self.fig.canvas)
        self.draw_widgets(event)

    def draw_widgets(self, event):
        self.wbm.draw_widgets(event)

    def on_key(self, event):

        r = None
        if event.key == " ":
            if self._timer_started:
                self._timer.stop()
                self._timer_started = False
                self.hide_spacebar()
            else:
                self._timer.start()
                self._timer_started = True
                self.show_spacebar()

            self.draw_widgets(event)
        else:
            if not self._timer_started:
                return
            self._timer.stop()
            self._timer_started = False
            self.hide_spacebar()

            if self.callback_customkey is not None:
                r = self.callback_customkey(event.key)

            # draw_widgets will be triggered by wbm._on_ky if its return value
            # is True. Still, we need to call self.draw_widgets to remove
            # spacebar widget.
            self.draw_widgets(event)

        return r

    def show_spacebar(self):
        self._spacebar.set_visible(True)

    def hide_spacebar(self):
        self._spacebar.set_visible(False)


class WidgetBoxManager:
    def __init__(self, fig, callback=None, **kw):
        self._container_list = []
        # self._wb_list = []
        self.fig = fig

        self.useblit = kw.pop("useblit", True)
        self.background = None
        self._background_filter = None

        self._callback = callback

        self._cid_list = {}

        self._ephemeral_containers = {}

        self._mouse_owner = None
        self._foreign_widgets: List[ForeignWidgetProtocol] = []

        self._stealed_lock = None

        self._last_callback_return_value = None

        self._spacebar = SpaceBar(fig, self, None)

    def get_last_callback_return_value(self):
        return self._last_callback_return_value 

    def add_foreign_widget(self, w: ForeignWidgetProtocol):
        self._foreign_widgets.append(w)

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

        # we first try to remove any ephemeral containers of child widgets.
        for zorder, wb in c.iter_wb_list():
            flattened_widgets = wb._get_flattened_widgets(wb._widgets)
            for w in flattened_widgets:
                wid = w.wid
                if wid in self._ephemeral_containers:
                    c1 = self._ephemeral_containers[wid]
                    self.remove_container(c1)
                    del self._ephemeral_containers[wid]

        self._container_list.remove((z, c))

    def add_widget_box(
            self,
            widgets,
            ax,
            xy,
            xycoords="data",
            xybox=(0, 0),
            boxcoords="offset points",
            direction="v",
            zorder=0,
            box_alignment=(0.5, 0.5),
            pad=10,
            frameon=True,
            clip=None,
    ):

        from collections.abc import Sequence

        _padx, _pady = pad if isinstance(pad, Sequence) else (pad, pad)

        wc = WidgetContainer(
            widgets,
            ax,
            xy=xy,
            xycoords=xycoords,
            xybox=xybox,
            boxcoords=boxcoords,
            box_alignment=box_alignment,
            direction=direction,
            frameon=frameon,
            clip=clip,
        )

        self.add_container(wc, zorder=zorder)
        return wc

    def add_anchored_widget_box(
        self,
        widgets,
        ax,
        loc=2,
        direction="v",
        zorder=0,
        box_alignment=None,
        bbox_to_anchor=None,
        xybox=None,
        pad=10,
        frameon=True,
    ):

        # xy, box_alignment, pad
        coefs = {
            "center": (0.5, 0.5),
            "lower left": (0, 0),
            "lower center": (0.5, 0),
            "lower right": (1.0, 0),
            "center right": (1.0, 0.5),
            "upper right": (1.0, 1.0),
            "upper center": (0.5, 1.0),
            "upper left": (0, 1.0),
            "center right": (0, 0.5),
        }

        loc_code = {
            1: "upper right",
            2: "upper left",
            3: "lower left",
            4: "lower right",
            5: "right",
            6: "center left",
            7: "center right",
            8: "lower center",
            9: "upper center",
            10: "center",
        }

        # change integer loc to string.
        loc = loc_code.get(loc, loc)
        xy = coefs.get(loc)
        box_alignment = xy if box_alignment is None else box_alignment
        from collections.abc import Sequence

        _padx, _pady = pad if isinstance(pad, Sequence) else (pad, pad)

        # loc = 5 and 7 have a same effects. See the matplotlib.legend manual.

        # We interpret xybox with a unit of padx and pady.
        # Thus the default is 1, 1. FIXME The API need ot be revisited.

        if xybox is None:
            xybox = (1, 1)

        # FIXME padx and pady means the padding from the inner edge of
        # bbox_to_anchor to the outer edge of the widget, *excluding the
        # frame*. This is not ideal for anchoring.

        padx = np.sign(0.5 - xy[0]) * _padx * xybox[0]
        pady = np.sign(0.5 - xy[1]) * _pady * xybox[1]
        xybox = padx, pady

        wc = AnchoredWidgetContainer(
            widgets,
            ax,
            xy=xy,
            xybox=xybox,
            box_alignment=box_alignment,
            # install_args=install_args
            direction=direction,
            bbox_to_anchor=bbox_to_anchor,
            frameon=frameon,
        )

        self.add_container(wc, zorder=zorder)
        return wc

    def add_sub_widget_box(
        self,
        widgets,
        ax,
        sticky=True,
        bbox_to_anchor=None,
        xy=(1, 1),
        xybox=(10, -10),
        parent=None,
        zorder=0,
    ):

        sub = SubGuiBox(
            widgets,
            ax,
            bbox_to_anchor=bbox_to_anchor,
            xy=xy,
            xybox=xybox,
            sticky=sticky,
            parent=parent,
        )

        self.add_container(sub, zorder=zorder)

        sub.install(self)

        return sub

    def install_all(self):

        for zorder, wc in self._container_list:
            if not wc.installed():
                wc.install(self)

        cid = self.fig.canvas.mpl_connect(
            "button_press_event", self.handle_event_n_draw
        )
        self._cid_list["button_press_event"] = cid

        cid = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.handle_event_n_draw
        )
        self._cid_list["motion_notify_event"] = cid

        cid = self.fig.canvas.mpl_connect("draw_event", self.save_n_draw)
        self._cid_list["draw_event"] = cid

        if self._spacebar is not None:
            cid = self.fig.canvas.mpl_connect('key_press_event',
                                              self.on_key)
            self._cid_list["key_press_event"] = cid

        # trigger installed event.
        e = WidgetBoxGlobalEvent("@installed")
        self._trigger_callback(e)

        self.fig.canvas.draw_idle()

    def uninstall_all(self):

        for zorder, wc in self._container_list:
            if wc.installed():
                wc.uninstall(self)

        for cid in self._cid_list.values():
            self.fig.canvas.mpl_disconnect(cid)

        self.fig.canvas.draw_idle()

    def handle_callback(self, event, e):
        wid = e.wid
        callback_info = e.callback_info
        if callback_info["command"] == "add_sub":
            a = callback_info["a"]
            ax = a.axes or event.inaxes

            xy = callback_info.get("xy", (1, 1))
            xybox = callback_info.get("xybox", (10, -10))
            sticky = callback_info.get("sticky", True)

            if ax is None:
                return

            if wid in self._ephemeral_containers:
                c = self._ephemeral_containers[wid]
                self.remove_container(c)
                del self._ephemeral_containers[wid]
            else:

                widgets = callback_info["widgets"]
                c = self.add_sub_widget_box(
                    widgets,
                    ax,
                    bbox_to_anchor=a,
                    sticky=sticky,
                    # xy=(1, 1), xybox=(10, -10),
                    xy=xy,
                    xybox=xybox,
                    parent=e.container_info["container"],
                    zorder=10,
                )
                self._ephemeral_containers[wid] = c

        elif callback_info["command"] == "update_widget":
            update_func = callback_info["update_func"]
            update_func(callback_info["value"])
            self.purge_ephemeral_containers(e)

    def purge_ephemeral_containers(self, event):
        event_container = event.container_info.get("container", None) if event else None
        to_be_deleted = [
            (wid, c)
            for (wid, c) in self._ephemeral_containers.items()
            if (not c.sticky) or not c.is_ancestor_of(event_container)
        ]

        for wid, c in to_be_deleted:
            self.remove_container(c)
            del self._ephemeral_containers[wid]

    def steal_event_lock(self):
        lock = self.fig.canvas.widgetlock

        # do nothing if self is the owner of the lock.
        if lock.isowner(self):
            return

        # if self._stealed_lock is not None:
        #     return

        # now we steal the lock
        if lock.isowner(None):
            lock(self)
            self._stealed_lock = None
        else:
            self._stealed_lock = lock._owner
            lock._owner = None
            lock(self)

    def restore_event_lock(self):
        lock = self.fig.canvas.widgetlock

        if lock.isowner(self):
            lock.release(self)

        if self._stealed_lock is not None:
            # lock._owner = None
            lock(self._stealed_lock)
            self._stealed_lock = None

    def check_event_area(self, event):
        "check if event is located inside the containers"
        for zorder, c in reversed(
            sorted(self._container_list, key=operator.itemgetter(0))
        ):
            b = c.check_event_area(event)
            if b:
                self.steal_event_lock()
                return True
        else:
            self.restore_event_lock()

    def _trigger_callback(self, e):
        if self._callback is not None:
            status = self.get_named_status()
            return self._callback(self, e, status)

    def handle_event_n_draw(self, event):
        event_inside = self.check_event_area(event)

        if not event_inside:
            # we need remove the tooltips and redraw if they are still on.
            if self._mouse_owner is not None:
                self._mouse_owner.set_mouse_leave()
                self._mouse_owner = None
                self.draw_widgets(event)

            return

        # we iter through containers to find out any of the widget in the
        # container can catch the event and convert it to WidgetBox' own event
        # instance.
        for zorder, c in reversed(
            sorted(self._container_list, key=operator.itemgetter(0))
        ):
            e = c.handle_event(event, parent=self)
            if e is not None:
                break
        else:
            e = None

        need_redraw = False

        if event.name == "motion_notify_event":
            if isinstance(e, MouseOverEvent):
                if self._mouse_owner != e.widget:
                    if self._mouse_owner is not None:
                        self._mouse_owner.set_mouse_leave()
                        need_redraw = True
                    self._mouse_owner = e.widget
                    need_redraw = True
            else:
                if self._mouse_owner is not None:
                    self._mouse_owner.set_mouse_leave()
                    self._mouse_owner = None
                    need_redraw = True

            # self._mouse_owner = e.wid

        if event.name in ["button_press_event"]:
            if e and e.callback_info:
                # note that some of the callback need to call `purge_emphemeral`.
                self.handle_callback(event, e)
            else:
                self.purge_ephemeral_containers(e)

            if e is not None and e.wid is not None:
                self._last_callback_return_value = self._trigger_callback(e)

        # if drawing is needed.
        if event.name in ["button_press_event"] or need_redraw:
            self.draw_widgets(event)

    def savebg(self, event):
        canvas = self.fig.canvas
        if self.useblit:
            self.background = self._get_background(event)

    def set_background_filter(self, bg_filter):
        """
        Modifies the background that is being saved.

            bg_filter(canvas, fig, background) -> background
        """
        self._background_filter = bg_filter

    def get_background_filter(self):
        return self._background_filter

    def _get_background(self, event):

        canvas = event.canvas
        background = canvas.copy_from_bbox(self.fig.bbox)

        if self.get_background_filter() is not None:
            background = self._background_filter(canvas, self.fig, background)

        return background

        # renderer = canvas.get_renderer()
        # bg_rgba = np.array(background)
        # rgb = bg_rgba[:, :, :-1]

        # gray = np.sum(rgb * [0.299, 0.587, 0.114], axis=-1).astype(rgb.dtype)

        # gray = 255 - ((255 - gray) >> 2)

        # bg_rgba[:, :, :-1] = gray[:, :, np.newaxis]

        # gc = renderer.new_gc()
        # renderer.draw_image(
        #     gc, 0, 0, bg_rgba[::-1])

        # return canvas.copy_from_bbox(fig.bbox)


    def save_n_draw(self, event):
        self.savebg(event)

        # self.draw_child_containers(event, draw_foreign_widgets=False)
        self.draw_child_containers(event, draw_foreign_widgets=True)

    def on_key(self, event):
        t = self._spacebar.on_key(event)
        if t:
            e = WidgetBoxGlobalEvent("@key")
            self._trigger_callback(e)

    def draw_widgets(self, event):
        if self.useblit:
            if self.background is not None:
                self.fig.canvas.restore_region(self.background)

                self.draw_child_containers(event)
                self.fig.canvas.blit(self.fig.bbox)

    def draw_child_containers(self, event, draw_foreign_widgets=True):
        delayed_draws = []
        to_be_removed = []
        for zorder, c in self._container_list:
            # check if c.ax is still in the figure and uninstall if not.
            if (isinstance(c, AxesWidgetBoxContainer) and
                  isinstance(c.ax, Axes) and
                  c.ax not in self.fig.axes):
                c.uninstall(self)
                to_be_removed.append((zorder, c))
                continue

            _ = c.draw_widgets(event)
            delayed_draws.extend(_ or [])

        for zc in to_be_removed:
            self._container_list.remove(zc)

        renderer = event.canvas.get_renderer()

        # foreign widgets may need to be an attribute of axes.
        if draw_foreign_widgets:
            for a in self._foreign_widgets:
                a.purge_background()
                a.draw(renderer)

        for draw in delayed_draws:
            draw(renderer)

    def get_named_status(self):
        status = {}
        for zorder, c in self._container_list:
            status.update(c.get_named_status())

        return status

    def draw_idle(self):
        self.fig.canvas.draw_idle()

    def get_widget_by_id(self, wid):
        for zorder, c in self._container_list:
            w = c.get_widget_by_id(wid)
            if w is not None:
                return w

    def get_parents_of_wid(self, wid):
        for zorder, c in self._container_list:
            wb = c.get_widgetbox_of_wid(wid)
            if wb is not None:
                return c, wb
        return None, None

    def wait_for_button(self):
        """Returns the last return value from the callback function or True if the
        figure is destroyed.
        """
        from matplotlib.pyplot import fignum_exists
        if fignum_exists(self.fig.number):
            self.fig.waitforbuttonpress()
            return self.get_last_callback_return_value()
        else:
            # return True if fig does not exists anymore.
            return True

    # This is a hack for the widgets to get removed when the figure is cleared
    # (clf), We will add the manager as a subfigure of the figure. When the
    # figure is cleared, the clear method of the subfigures are also called. On
    # the other hand, we also need to define the draw and get_children method
    # which does nothing.

    def draw(self, renderer):
        pass

    def get_children(self):
        return []

    def pick(self, mouseevent):
        pass

    def clear(self, keep_observers=None):
        self.uninstall_all()

    def _append_to_subfigs(self, fig):
        # This is a hack to add wbm as an artist of the fig so that it can be
        # unmounted when the figure got cleared.
        fig.subfigs.append(self)

    # containers can have multiple widget_boxes.


class WidgetBoxContainerBase:
    def __init__(self):
        # if wb_list is None:
        #     wb_list = []
        self._wb_list = []
        self._installed = False
        self._visible = True

    def set_visible(self, v):
        self._visible = v

    def get_visible(self):
        return self._visible

    def append_widget_box(self, widget_box, zorder=0):
        self._wb_list.append((zorder, widget_box))

    def iter_wb_list(self, reverse=False):
        for zorder, wb in sorted(
            self._wb_list, key=operator.itemgetter(0), reverse=reverse
        ):
            yield zorder, wb

    def get_widget_by_id(self, wid):
        for zorder, wb in self.iter_wb_list():
            w = wb.get_widget_by_id(wid)
            if w is not None:
                return w

    def get_widgetbox_of_wid(self, wid):
        for zorder, wb in self.iter_wb_list():
            w = wb.get_widget_by_id(wid)
            if w is not None:
                return wb

    def check_event_area(self, event):
        for zorder, wb in self.iter_wb_list():
            b = wb.check_event_area(event)
            if b:
                return True

    def handle_event(self, event, parent=None):
        if not self.get_visible:
            return None

        for zorder, wb in sorted(
            self._wb_list, key=operator.itemgetter(0), reverse=True
        ):
            e = wb.handle_event(event, parent=parent)
            if e is not None:
                break
        else:
            e = None

        if e is not None:
            e.container_info["container"] = self

        return e

    def get_draw_widget_method(self):
        pass

    def draw_widgets(self, event):
        if not self.get_visible():
            return []

        if not self.installed:
            raise RuntimeError("need to be installed before drawing")

        # delayed_draws = self.draw_container(event) or []
        delayed_draws = []

        for zorder, wb in self.iter_wb_list(reverse=False):
            # self.draw_widget(w, event)
            dd = wb.draw_widgets(event, draw_method=self.get_draw_widget_method())
            delayed_draws.extend(dd or [])

        return delayed_draws

    def get_named_status(self):
        status = {}
        for zorder, wb in self.iter_wb_list(reverse=False):
            # self.draw_widget(w, event)
            s = wb.get_named_status()
            status.update(s)

        return status

    def draw_container(self, event):
        pass

    def install(self, wbm):
        for zorder, wb in self.iter_wb_list():
            wb.init_widgets()
            wb.trigger_post_install_hooks(wbm)

        self._installed = True

    def uninstall(self, wbm):
        for zorder, wb in self.iter_wb_list():
            wb.trigger_post_uninstall_hooks(wbm)

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

    def get_widget_box(self):
        return self._wb_list[0][-1]

    def get_draw_widget_method(self):
        return self.ax.draw_artist

    def install(self, wbm):

        super().install(wbm)

        for zorder, wb in self.iter_wb_list():
            self.ax.add_artist(wb.get_artist())

        return self

    def uninstall(self, wbm):
        super().uninstall(wbm)

    def reinit_widget_box(self, wbm, widgets):
        wb = self.get_widget_box()
        # assert wb in [_wb for _, _wb in self._wb_list]

        wb.trigger_post_uninstall_hooks(wbm)
        wb.get_artist().remove()
        wb.init_widgets(widgets)
        self.ax.add_artist(wb.get_artist())
        wb.trigger_post_install_hooks(wbm)


class WidgetContainer(AxesWidgetBoxContainer):
    def __init__(
        self,
        widgets,
        ax,
        xy=(0, 1),
        xycoords="data",
        xybox=(0, 0),
        boxcoords="offset points",
        box_alignment=(0, 1),
        frameon=True,
        clip=None,
        direction="v",
    ):

        widget_box = self._make_widget_box(
            widgets,
            ax,
            xy=xy,
            xycoords=xycoords,
            xybox=xybox,
            boxcoords=boxcoords,
            box_alignment=box_alignment,
            direction=direction,
            frameon=frameon,
            clip=clip,
        )
        super().__init__(widget_box, ax)

    def _make_widget_box(
        self,
        widgets,
        ax,
        xy=(0, 1),
        xycoords="data",
        xybox=(0, 0),
        boxcoords="offset points",
        box_alignment=(0, 1),
        frameon=True,
        clip=None,
        direction="v",
    ):

        _widget_box = WidgetBox(
            widgets,
            ax,
            xy=xy,
            xycoords=xycoords,
            xybox=xybox,
            boxcoords=boxcoords,
            box_alignment=box_alignment,
            direction=direction,
            clip=clip,
            frameon=frameon,
        )

        return _widget_box

class AnchoredWidgetContainer(AxesWidgetBoxContainer):
    def __init__(
        self,
        widgets,
        ax,
        bbox_to_anchor=None,
        xy=(0, 1),
        xybox=(0, 0),
        box_alignment=(0, 1),
        frameon=True,
        direction="v",
    ):

        widget_box = self._make_widget_box(
            widgets,
            ax,
            bbox_to_anchor=bbox_to_anchor,
            xy=xy,
            xybox=xybox,
            box_alignment=box_alignment,
            direction=direction,
            frameon=frameon,
        )
        super().__init__(widget_box, ax)

    def _make_widget_box(
        self,
        widgets,
        ax,
        bbox_to_anchor=None,
        xy=(0, 1),
        xybox=(0, 0),
        box_alignment=(0, 1),
        frameon=True,
        direction="v",
    ):

        _widget_box = AnchoredWidgetBox(
            widgets,
            ax,
            bbox_to_anchor=bbox_to_anchor,
            xy=xy,
            xybox=xybox,
            box_alignment=box_alignment,
            direction=direction,
            frameon=frameon,
        )

        return _widget_box


class SubGuiBox(AnchoredWidgetContainer):
    def __init__(
        self,
        widgets,
        ax,
        bbox_to_anchor=None,
        xy=(0, 1),
        xybox=(0, 0),
        parent=None,
        sticky=True,
    ):
        super().__init__(widgets, ax, bbox_to_anchor=bbox_to_anchor, xy=xy, xybox=xybox)

        # sticky for only for event from the same container.
        self.sticky = sticky
        self.parent = parent

    def get_ancestors(self):
        if hasattr(self.parent, "get_ancestors"):
            return list(self.parent.get_ancestors()) + [self.parent]
        else:
            return [self.parent]

    def is_ancestor_of(self, c):
        my_ancestors = self.get_ancestors()
        n = len(my_ancestors)
        if c is not None and hasattr(c, "get_ancestors"):
            ancestors = c.get_ancestors()
            return my_ancestors == ancestors[:n]


# WidgetBox should contain a single box
class WidgetBoxBase:
    @classmethod
    def _get_flattened_widgets(cls, widgets):
        flattened_widgets = []
        for w in widgets:
            if isinstance(w, PackedWidgetBase):
                child_widgets = w.get_child_widgets()
                new_widgets = cls._get_flattened_widgets(child_widgets)
                flattened_widgets.extend(new_widgets)
            else:
                flattened_widgets.append(w)

        return flattened_widgets

    def __init__(self, widgets, direction="v"):

        self.widgets_orig = widgets

        self._post_install_hook = []
        self._post_uninstall_hook = []

        self.direction = direction

        # init_widgets method will be called later during install phase.
        # self.init_widgets()

    def init_widgets(self, widgets=None):

        widgets = widgets or self.widgets_orig

        _widgets = []
        for w in widgets:
            if isinstance(w, CompositeWidgetBase):
                _widgets.extend(w.build_widgets())
                self._post_install_hook.append(w.post_install)
                self._post_uninstall_hook.append(w.post_uninstall)
            else:
                _widgets.append(w)

        self._widgets = _widgets

        flattened_widgets = self._get_flattened_widgets(self._widgets)
        self._handler = WidgetsEventHandler(flattened_widgets)

        self.box = self.wrap(_widgets, direction=self.direction)

    def get_artist(self):
        return self.box

    def check_event_area(self, event):
        bbox = self.box.patch.get_extents()
        return bbox.contains(event.x, event.y)

    def wrap(self, widgets, direction="v"):
        if direction == "h":
            _pack = HPacker(
                children=widgets,
                pad=3,
                sep=3,
                # **kwargs
                mode="expand",
            )

            wrapped = VPacker(children=[_pack], pad=0, sep=0, mode="expand")
        else:
            _pack = VPacker(
                children=widgets,
                pad=3,
                sep=3,
                # **kwargs
                mode="expand",
            )
            wrapped = HPacker(children=[_pack], pad=0, sep=0, mode="expand")

        return wrapped

    def get_widgets(self):
        return self._widgets

    def get_box(self):
        return self.box

    def _check_xy(self, renderer):
        return True

    def handle_event(self, event, parent=None):

        renderer = event.canvas.get_renderer()
        if not self._check_xy(renderer):
            return None
        parent = self
        e = self._handler.handle_event(event, parent=parent)

        return e

    def get_named_status(self):
        status = self._handler.get_named_status()

        return status

    def draw_widgets(self, event, draw_method):
        renderer = event.canvas.get_renderer()
        return self.box.draw(renderer)

    def trigger_post_install_hooks(self, wbm):
        while self._post_install_hook:
            cb = self._post_install_hook.pop()
            cb(wbm)
        # for cb in self._post_install_hook:
        #     cb(wbm)

    def trigger_post_uninstall_hooks(self, wbm):
        while self._post_uninstall_hook:
            cb = self._post_uninstall_hook.pop()
            cb(wbm)
        # for cb in self._post_uninstall_hook:
        #     cb(wbm)

    def get_widget_by_id(self, wid):
        for w in self._handler.get_child_widgets():
            if w.wid == wid:
                return w


class WidgetBox(WidgetBoxBase):
    def __init__(
        self,
        widgets,
        ax,
        xy=(0, 1),
        xycoords="data",
        xybox=(0, 0),
        boxcoords="offset points",
        box_alignment=(0, 1),
        frameon=True,
        clip=None,
        direction="v",
    ):

        install_args = dict(
            xy=xy,
            xycoords=xycoords,
            xybox=xybox,
            boxcoords=boxcoords,
            box_alignment=box_alignment,
            frameon=frameon,
            clip=clip,
        )

        self._install_args = install_args
        self.ax = ax

        super().__init__(widgets, direction=direction)

    def _check_xy(self, renderer):
        return self.box._check_xy(renderer)

    def wrap(self, widgets, direction="v"):
        if direction == "h":
            _pack = HPacker(children=widgets, pad=1, sep=2, align="bottom")
            box = VPacker(children=[_pack], pad=0, sep=0)
        else:
            _pack = VPacker(
                children=widgets,
                pad=1,
                sep=2,
                align="left",  # the default is baseline which depends on
                # xdescent. While this is okay in general, this
                # may introduce offset shift when collapsed.
            )
            box = HPacker(children=[_pack], pad=0, sep=0)

        wrapped = self._make_wrapped_widget_box(self.ax, box, **self._install_args)
        return wrapped

    def _make_wrapped_widget_box(
        self,
        ax,
        box,
        xy=(0, 1),
        xycoords="data",
        xybox=(0, 0),
        boxcoords="offset points",
        box_alignment=(0, 1),
        frameon=True,
        clip=None,
    ):
        wrapped_box = AnnotationBbox(
            box,
            xy=xy,
            xybox=xybox,
            xycoords=xycoords,
            boxcoords=boxcoords,
            box_alignment=box_alignment,
            pad=0.3,
            animated=True,
            frameon=frameon,
            annotation_clip=clip,
        )
        return wrapped_box


class AnchoredWidgetBox(WidgetBoxBase):
    def __init__(
        self,
        widgets,
        ax,
        bbox_to_anchor=None,
        xy=(0, 1),
        xybox=(0, 0),
        box_alignment=(0, 1),
        frameon=True,
        direction="v",
    ):

        install_args = dict(
            bbox_to_anchor=bbox_to_anchor,
            xy=xy,
            xybox=xybox,
            box_alignment=box_alignment,
            frameon=frameon,
        )

        self._install_args = install_args
        self.ax = ax

        super().__init__(widgets, direction=direction)

    def wrap(self, widgets, direction="v"):
        if direction == "h":
            _pack = HPacker(children=widgets, pad=1, sep=2, align="bottom")
            box = VPacker(children=[_pack], pad=0, sep=0)
        else:
            _pack = VPacker(
                children=widgets,
                pad=1,
                sep=2,
                align="left",  # the default is baseline which depends on
                # xdescent. While this is okay in general, this
                # may introduce offset shift when collapsed.
            )
            box = HPacker(children=[_pack], pad=0, sep=0)

        wrapped = self._make_wrapped_widget_box(self.ax, box, **self._install_args)
        return wrapped

    def _make_wrapped_widget_box(
        self,
        ax,
        box,
        bbox_to_anchor=None,
        xy=(0, 1),
        xybox=(0, 0),
        box_alignment=(0, 1),
        frameon=True,
    ):
        if bbox_to_anchor is None:
            bbox_to_anchor = ax

        wrapped_box = AnnotationBbox(
            box,
            xy=xy,
            xybox=xybox,
            xycoords=bbox_to_anchor,
            boxcoords="offset points",
            box_alignment=box_alignment,
            pad=0.3,
            animated=True,
            frameon=frameon,
        )
        return wrapped_box


def install_widgets_simple(ax, widgets, cb=None, loc=2, add_to_subfigs=True):

    wbm = WidgetBoxManager(ax.figure)

    wbm.add_anchored_widget_box(
        widgets,
        ax,
        loc=loc,
    )

    if cb is not None:
        wbm.set_callback(cb)

    wbm.install_all()

    if add_to_subfigs:
        wbm._append_to_subfigs(ax.figure)

    wbm.draw_idle()

    return wbm
