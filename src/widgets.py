from matplotlib.offsetbox import PaddedBox

from matplotlib.offsetbox import (OffsetBox,
                                  AnnotationBbox,
                                  DrawingArea, TextArea,
                                  OffsetImage,
                                  HPacker, VPacker)

from matplotlib.offsetbox import (VPacker as _VPacker,
                                  HPacker as _HPacker)

from event_handler import WidgetBoxEventHandlerBase

from icon_helper import load_from_json
icons = load_from_json("icons.json")

# Widgets are derived from PaddedBox, which is basically an offsetbox.

class BaseWidget(PaddedBox):
    def get_event_area(self, renderer):
        return self.patch.get_window_extent(renderer)

    def draw_frame_with_outer_bbox(self, renderer, outer_bbox):

        dpicor = renderer.points_to_pixels(1.)
        pad = self.pad * dpicor
        ypad = 0.

        frame_bbox = mtransforms.Bbox.from_bounds(outer_bbox.xmin + pad,
                                                  outer_bbox.ymin + ypad,
                                                  outer_bbox.width - 2*pad,
                                                  outer_bbox.height - 2*ypad)

        self.update_frame(frame_bbox)
        self.patch.draw(renderer)

        # self.draw_frame(renderer)

    def update_child_offsets(self, renderer, outer_bbox):
        w, h, xdescent, ydescent, offsets = self.get_extent_offsets(renderer)
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)
        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((px + ox, py + oy))

    def draw_with_outer_bbox(self, renderer, outer_bbox):
        # a copy of PaddedBox.draw.
        # The only change is to us draw_frame_with_outer_bbox to draw frame

        # docstring inherited
        self.update_child_offsets(renderer, outer_bbox)

        self.draw_frame_with_outer_bbox(renderer, outer_bbox)

        for c in self.get_visible_children():
            if hasattr(c, "draw_with_outer_bbox"):
                dpicor = renderer.points_to_pixels(1.)
                pad = self.pad * dpicor
                new_outer_bbox = mtransforms.Bbox.from_bounds(outer_bbox.xmin + pad,
                                                              outer_bbox.ymin + pad,
                                                              outer_bbox.width - 2*pad,
                                                              outer_bbox.height - 2*pad)

                c.draw_with_outer_bbox(renderer, new_outer_bbox)
            else:
                c.draw(renderer)

        self.stale = False


class Centered(BaseWidget):
    def update_child_offsets(self, renderer, outer_bbox):
        w, h, xdescent, ydescent, offsets = self.get_extent_offsets(renderer)
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)
        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((px + (outer_bbox.width-w) * 0.5 + ox, py + oy))


import matplotlib.transforms as mtransforms
from matplotlib.offsetbox import bbox_artist

class VPacker(_VPacker):
    def get_event_area(self, renderer):
        return self.get_window_extent(renderer)

    def draw(self, renderer):
        """
        Update the location of children if necessary and draw them
        to the given *renderer*.
        """
        my_bbox = self.get_extent_offsets(renderer)
        w, h, xdescent, ydescent, offsets = my_bbox
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)

        left = px - xdescent

        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((px + ox, py + oy))
            if hasattr(c, "draw_with_outer_bbox"):
                cb = c.get_window_extent(renderer)
                outer_bbox = mtransforms.Bbox.from_bounds(left, cb.ymin, w, cb.height)
                c.draw_with_outer_bbox(renderer, outer_bbox)
            else:
                c.draw(renderer)

        # not sure the role of this
        bbox_artist(self, renderer, fill=False, props=dict(pad=0.))

        self.stale = False


class HPacker(_HPacker):
    def get_event_area(self, renderer):
        return self.get_window_extent(renderer)

    # def draw_with_outer_bbox(self, renderer, outer_bbox):
    #     self.draw(renderer)


class HWidgets(HPacker):
    def __init__(self, *kl, **kw):
        pad = kw.pop("pad", 0)
        sep = kw.pop("sep", 3)
        super().__init__(*kl, pad=pad, sep=sep, **kw)

    def get_child_widgets(self):
        return self.get_children()

    # def handle_event(self, event, parent=None):
    #     print("OOO")

class WidgetBoxEvent():
    def __init__(self, event, wid,
                 auxinfo=None,
                 callback_info=None):
        self.event = event
        self.wid = wid
        self.auxinfo = auxinfo if auxinfo is not None else {}
        self.callback_info = callback_info

        # the container that the event is triggered.
        self.container_info = {}

    def __repr__(self):
        return f"Event: {self.wid} {self.auxinfo}"


class Label(BaseWidget):
    def set_label(self, l):
        self.box.set_text(l)

    def _get_textprops(self):
        return {}

    def _update_patch(self, patch):
        patch.update(dict(ec="none"))

    def __init__(self, wid, label, pad=None, draw_frame=True,
                 auxinfo=None):
        self.wid = wid
        self.label = label
        self.auxinfo = auxinfo if auxinfo is not None else {}

        if pad is None:
            pad = 3
        if isinstance(label, str):
            box = TextArea(label, textprops=self._get_textprops())
        elif isinstance(label, OffsetBox):
            box = label
        else:
            raise ValueError("incorrect label")
        self.box = box

        super().__init__(box, pad=pad, draw_frame=draw_frame)
        # self.patch.update(dict(ec="none", fc="#DDDDDD"))
        self._update_patch(self.patch)

    def get_status(self):
        return {}

    def handle_event(self, event, parent=None):
        # print("pressed", self.label)
        return WidgetBoxEvent(event, None, auxinfo=self.auxinfo)

class Title(Label):
    def _get_textprops(self):
        return dict(weight="bold")

    # def _update_patch(self, patch):
    #     pass
    #     # patch.update(dict(ec="none", fc="0.9"))

class Button(Label):
    def _get_textprops(self):
        return dict(color="w")

    def __init__(self, wid, label, pad=None, draw_frame=True,
                 centered=False,
                 **kwargs):

        if isinstance(label, str):
            box = TextArea(label, textprops=self._get_textprops())
        elif isinstance(label, OffsetBox):
            box = label
        else:
            raise ValueError("incorrect label")
        self.box = box

        if centered:
            self.button_box = Centered(box, pad=3,
                                       draw_frame=draw_frame)
        else:
            self.button_box = BaseWidget(box, pad=3,
                                         draw_frame=draw_frame)


        super().__init__(wid, self.button_box, pad=pad, draw_frame=False)
        # self.patch.update(dict(ec="none", fc="#DDDDDD"))
        self._update_patch(self.patch)

        # super().__init__(wid, label, pad=pad, draw_frame=draw_frame,
        #                  **kwargs)
        # print(self.patch)
        patch = self.button_box.patch
        patch.update(dict(fc="#6200ee", ec="#6200ee")) # patch_attrs
        patch.set_boxstyle("round,pad=0.3")
        patch.set_mutation_scale(8)

        from matplotlib import patheffects

        offset=(2, -2)
        patch.set_path_effects([# patheffects.withSimplePatchShadow(),
            patheffects.SimpleLineShadow(
                offset=offset,
                shadow_color="0.9",
                alpha=1.,
                linewidth=3.),
            patheffects.SimpleLineShadow(
                offset=offset,
                shadow_color="0.8",
                alpha=1.,
                linewidth=1.5),
            patheffects.SimplePatchShadow(offset=offset, shadow_rgbFace="0.7",
                                          foreground="none",
                                          alpha=1.),
            patheffects.Normal()
        ])

    def handle_event(self, event, parent=None):
        return WidgetBoxEvent(event, self.wid, auxinfo=self.auxinfo)


class Sub(Label):
    def build_label(self, label, button_label):
        # button_label.set_text(label)
        button = OffsetImage(icons[10]["popup_button"])
        label = HPacker(children=[button_label,
                                  button
                                  ],
                        pad=1, sep=2,
                        align="baseline")
        return label

    def __init__(self, wid, label, widgets, pad=None, draw_frame=True,
                 where="selected", **kwargs):

        if isinstance(label, str):
            self._button_label = TextArea("")
        else:
            self._button_label = label
        label_box = self.build_label(label, self._button_label)
        super().__init__(wid, label_box, pad=pad, draw_frame=draw_frame,
                         **kwargs)
        self.patch.update(dict(ec="none", fc="#FFFFDD"))

        # self.set_popup_widgets(widgets)
        self.sub_widgets = widgets
        self.where = where

    def handle_event(self, event, parent=None):

        if self.where == "selected":
            a = self
        else:
            a = parent.get_box()

        callback_info = dict(command="add_sub",
                             a=a,
                             widgets=self.sub_widgets)

        return WidgetBoxEvent(event, self.wid,
                              callback_info=callback_info)


class SelectableBase():
    def get_default_box(self, l):
        box = TextArea(l)
        return box

    def get_boxes(self, labels):
        boxes = []
        for l in labels:
            box = self.get_default_box(l)
            boxes.append(box)
            # if isinstance(l, str):
            # else:
            #     boxes.append(l)

        return boxes


class Dropdown(Sub, SelectableBase):
    def build_label(self, label, button_label):
        # button_label.set_text(label)
        button = OffsetImage(icons[8]["dropdown_button"])
        label = HPacker(children=[button,
                                  button_label
                                  ],
                        pad=1, sep=2,
                        align="baseline")
        return label

    def get_default_box(self, l):
        box = Label(l, l)
        return box

    def update_value(self, v):
        self._button_label.set_text(v)

    def get_boxes(self, widgets):
        self.menu = DropdownMenu(self.wid+":menu", widgets,
                                 update_func=self.update_value, pad=0)
        menu = [self.menu]
        return menu

    def __init__(self, wid, label, widgets, pad=None, draw_frame=True,
                 where="selected", **kwargs):

        super().__init__(wid, label, [], pad=pad, draw_frame=draw_frame,
                         where=where, **kwargs)
        widgets = self.get_boxes(widgets)
        self.sub_widgets = widgets

        v = self.menu.get_status()["value"]
        self.update_value(v)

        self.patch.update(dict(ec="none", fc="#FFFFDD"))

    def handle_event(self, event, parent=None):

        if self.where == "selected":
            a = self
        else:
            a = parent.get_box()

        callback_info = dict(command="add_sub",
                             a=a,
                             widgets=self.sub_widgets,
                             xy=(0, 0), xybox=(0, -5), sticky=False)

        return WidgetBoxEvent(event, self.wid,
                              callback_info=callback_info)

    # def sub_selected(self, event, parent):
    #     self.set_label(event.wid)
    #     event.auxinfo.update(self.auxinfo)

    # def _add_sub(self, parent):
    #     if self.where == "selected":
    #         a = self
    #     else:
    #         a = parent.box.offsetbox

    #     print("ppp", parent)
    #     parent.add_sub(a, self.widgets,
    #                    self.sub_selected, sticky=False,
    #                    xy=(0, 0), xybox=(0, 0))


class Radio(BaseWidget, WidgetBoxEventHandlerBase, SelectableBase):

    def _populate_buttons(self):
        SELECTED_ON = "(O)"
        SELECTED_OFF = "( )"
        # self.button_on = TextArea(SELECTED_ON)
        # self.button_off = TextArea(SELECTED_OFF)
        self.button_on = OffsetImage(icons[8]["radio_button_on"])
        self.button_off = OffsetImage(icons[8]["radio_button_off"])

    def set_figure(self, fig):
        super().set_figure(fig)
        self.button_on.set_figure(fig)
        self.button_off.set_figure(fig)

    def get_default_box(self, l):
        if isinstance(l, str):
            box = HPacker(children=[self.button_off,
                                    TextArea(l)],
                          pad=1, sep=2,
                          align="baseline")
        else:
            box = HPacker(children=[self.button_off,
                                    l],
                          pad=1, sep=2,
                          align="baseline")

        return box

    def get_initial_selected(self, selected):
        selected = [0] if selected is None else [selected]
        return selected

    def __init__(self, wid, labels, selected=None,
                 values=None, title=None, pad=3):
        self.selected = self.get_initial_selected(selected)
        self._populate_buttons()

        self.wid = wid

        # label_box = TextArea("Label:")
        if title is not None:
            label_box = HPacker(children=[TextArea(title)],
                                pad=1, sep=2,
                                align="baseline")
            self.boxes = [label_box]
            self._title_offset = 1
        else:
            self.boxes = []
            self._title_offset = 0
        # box = HPacker(children=[self.button_off,
        #                         TextArea(l)],
        #               pad=1, sep=2,
        #               align="baseline")

        self.values = values if values is not None else labels

        self.boxes.extend(self.get_boxes(labels))

        kwargs = {}
        box = VPacker(children=self.boxes,
                      pad=0, sep=3,
                      **kwargs)

        BaseWidget.__init__(self, box, pad=pad,
                           draw_frame=True)
        WidgetBoxEventHandlerBase.__init__(self, box)

        self._update_patch(self.patch)
        self.select(selected)

    def _update_patch(self, patch):
        # patch.update(dict(ec="none"))
        self.patch.update(dict(ec="#AAEEEE", fc="#EEFFFF"))

    def select(self, i):
        if i is None:
            i = 0

        o = self._title_offset

        for _i, b in enumerate(self.boxes[o:]):
            if _i == i:
                b.get_children()[0] = self.button_on
            else:
                b.get_children()[0] = self.button_off

        self.selected[:] = [i]

    def handle_event(self, event, parent=None):
        i, b = self.get_responsible_child(event)

        i -= self._title_offset

        if i >= 0:
            self.select(i)

        return WidgetBoxEvent(event, self.wid, dict(lid=i, widget=b))

    def get_status(self):
        return dict(selected=self.selected,
                    value=self.values[self.selected[0]])


class DropdownMenu(Radio):
    """
    The selection menu when dropdown button is pressed.
    """
    def __init__(self, wid, labels, selected=None,
                 values=None, title=None, pad=0, update_func=None):
        super().__init__(wid, labels, selected=selected,
                         values=values, title=title, pad=pad)
        self._update_func = update_func

    def _update_patch(self, patch):
        patch.update(dict(ec="none"))
        # pass
        # self.patch.update(dict(ec="#AAEEEE", fc="#EEFFFF"))

    def _populate_buttons(self):
        SELECTED_ON = "(O)"
        SELECTED_OFF = "( )"
        # self.button_on = TextArea(SELECTED_ON)
        # self.button_off = TextArea(SELECTED_OFF)
        self.button_on = OffsetImage(icons[8]["check_mark"])
        self.button_off = OffsetImage(icons[8]["empty"])


    def handle_event(self, event, parent=None):
        i, b = self.get_responsible_child(event)

        i -= self._title_offset

        if i >= 0:
            self.select(i)

        if self._update_func is not None:
            callback_info = dict(command="update_widget",
                                 update_func=self._update_func,
                                 value=self.values[i])
        else:
            callback_info = None

        return WidgetBoxEvent(event, self.wid,
                              callback_info=callback_info)


class CheckBox(Radio):
    # button_on = TextArea(SELECTED_ON)
    # button_off = TextArea(SELECTED_OFF)
    # button_on = OffsetImage(ff[8]["check_button_on"])
    # button_off = OffsetImage(ff[8]["check_button_off"])

    def _populate_buttons(self):
        SELECTED_ON = "[v]"
        SELECTED_OFF = "[ ]"
        # self.button_on = TextArea(SELECTED_ON)
        # self.button_off = TextArea(SELECTED_OFF)
        self.button_on = OffsetImage(icons[8]["check_button_on"])
        self.button_off = OffsetImage(icons[8]["check_button_off"])

    def get_initial_selected(self, selected):
        selected = [] if selected is None else selected
        return selected

    def select(self, i):
        if i is None:
            return

        o = self._title_offset

        b = self.boxes[o+i]
        if i in self.selected:
            self.selected.remove(i)
            b.get_children()[0] = self.button_off
        else:
            self.selected.append(i)
            b.get_children()[0] = self.button_on

    def get_status(self):
        return dict(selected=self.selected,
                    values=[self.values[s] for s in self.selected])
