"""Defines a set of widgets.

"""

__all__ = ["VPacker", "HPacker", "HWidgets", "VWidgets",
           "WidgetBoxEvent", "WidgetBoxGlobalEvent", "MouseOverEvent",
           "Label", "Title", "Button",
           "Radio", "CheckBox", "Sub", "Dropdown", "RadioButton"]

from itertools import zip_longest

import matplotlib.transforms as mtransforms
from matplotlib.offsetbox import bbox_artist

from matplotlib.offsetbox import (
    OffsetBox,
)

from matplotlib.offsetbox import VPacker as _VPacker, HPacker as _HPacker

# from pathlib import Path
# from matplotlib.font_manager import FontProperties

from .event_handler import WidgetBoxEventHandlerBase

from ._abc import PackedWidgetBase

from .fa_helper import FontAwesome

fa_icons = FontAwesome.icons
get_icon_fontprop = FontAwesome.get_fontprop

from .base_widget import BaseWidget, TextArea


class Centered(BaseWidget):
    def update_child_offsets(self, renderer, outer_bbox):

        w, h, xdescent, ydescent, offsets = self.get_extent_offsets(renderer)
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)
        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((px + (outer_bbox.width - w) * 0.5 + ox, py + oy))


class DrawWithDelayed:
    def draw(self, renderer):
        """
        Update the location of children if necessary and draw them
        to the given *renderer*.
        """
        # Modifie from OffsetBox.draw.
        my_bbox = self.get_extent_offsets(renderer)
        w, h, xdescent, ydescent, offsets = my_bbox
        px, py = self.get_offset(w, h, xdescent, ydescent, renderer)

        delayed_draws = []
        for c, (ox, oy) in zip(self.get_visible_children(), offsets):
            c.set_offset((px + ox, py + oy))
            if hasattr(c, "draw_with_outer_bbox"):
                # update the outer_bbox
                outer_bbox = self._get_outer_bbox(
                    px, py, my_bbox, c.get_window_extent(renderer)
                )
                dd = c.draw_with_outer_bbox(renderer, outer_bbox)
            else:
                dd = c.draw(renderer)

            delayed_draws.extend(dd or [])

        # not sure the role of this
        bbox_artist(self, renderer, fill=False, props=dict(pad=0.0))

        self.stale = False

        return delayed_draws


class VPacker(DrawWithDelayed, _VPacker):
    def get_event_area(self, renderer):
        return self.get_window_extent(renderer)

    def _get_outer_bbox(self, px, py, bbox, cb):
        # bbox : bbox of the self
        # cb : bbox of the child
        w, h, xdescent, ydescent, offsets = bbox
        left = px - xdescent

        outer_bbox = mtransforms.Bbox.from_bounds(left, cb.ymin, w, cb.height)

        return outer_bbox

    def handle_motion_notify(self, event, parent):
        pass


class HPacker(DrawWithDelayed, _HPacker):
    def get_event_area(self, renderer):
        return self.get_window_extent(renderer)

    def _get_outer_bbox(self, px, py, bbox, cb):
        # bbox : bbox of the self
        # cb : bbox of the child
        w, h, xdescent, ydescent, offsets = bbox
        bottom = py - ydescent

        outer_bbox = mtransforms.Bbox.from_bounds(cb.xmin, bottom, cb.width, h)

        return outer_bbox

    def handle_motion_notify(self, event, parent):
        pass


class HWidgets(PackedWidgetBase, HPacker):
    def __init__(self, children, *kl, **kw):
        pad = kw.pop("pad", 0)
        sep = kw.pop("sep", 3)
        super().__init__(*kl, children=children, pad=pad, sep=sep, **kw)

    def get_child_widgets(self):
        return self.get_children()


class VWidgets(PackedWidgetBase, VPacker):
    def __init__(self, children, *kl, **kw):
        pad = kw.pop("pad", 0)
        sep = kw.pop("sep", 3)
        super().__init__(*kl, children=children, pad=pad, sep=sep, **kw)

    def get_child_widgets(self):
        return self.get_children()


class WidgetBoxEventBase:
    """
    wid starts with @ are considered as global event and should not be used.
    """
    def __init__(self, wid):
        self.wid = wid

    def __repr__(self):
        return f"Event: {self.wid}"

class WidgetBoxGlobalEvent:
    """
    wid starts with @ are considered as global event and should not be used.
    """
    def __init__(self, wid):
        self.wid = wid

    def __repr__(self):
        return f"GlobarEvent: {self.wid}"

class WidgetBoxEvent(WidgetBoxEventBase):
    """
    wid starts with @ are considered as global event and should not be used.
    """
    def __init__(self, event, wid, auxinfo=None, callback_info=None):
        super().__init__(wid)
        self.event = event
        self.auxinfo = auxinfo if auxinfo is not None else {}
        self.callback_info = callback_info

        # the container that the event is triggered.
        self.container_info = {}

    def __repr__(self):
        return f"Event: {self.wid} {self.auxinfo} {self.container_info}"


class MouseOverEvent(WidgetBoxEvent):
    def __init__(self, event, wid, widget, auxinfo=None, callback_info=None):
        super().__init__(event, wid, auxinfo=auxinfo, callback_info=callback_info)
        self.widget = widget


class NamedWidget(BaseWidget):
    def __init__(self, wid, box, pad=None, draw_frame=True, auxinfo=None, **kwargs):
        self.wid = wid
        self.auxinfo = auxinfo if auxinfo is not None else {}
        super().__init__(box, pad=pad, draw_frame=draw_frame, **kwargs)


class LabelBase(NamedWidget):
    def __init__(
        self, wid, box, textbox=None, pad=None, draw_frame=True, auxinfo=None, **kwargs
    ):
        # self.label = label

        if pad is None:
            pad = 3

        super().__init__(
            wid, box, pad=pad, draw_frame=draw_frame, auxinfo=auxinfo, **kwargs
        )

        self.box = box
        self.textbox = textbox

        self._update_patch(self.patch)

    def get_label(self):
        """get the label string."""
        if self.textbox is not None:
            return self.textbox.get_text()
        else:
            raise RuntimeError("no textbox is defined")

    def set_label(self, l):
        """set the label string."""
        if self.textbox is not None:
            self.textbox.set_text(l)
        else:
            raise RuntimeError("no textbox is defined")

    def _get_default_textprops(self):
        return {}

    def set_textprops(self, **textprops):
        self.textbox.set_textprops(**textprops)

    def _update_patch(self, patch):
        patch.update(dict(ec="none"))

    def get_status(self):
        return {}

    def handle_button_press(self, event, parent=None):
        return WidgetBoxEvent(event, None, auxinfo=self.auxinfo)

    def handle_motion_notify(self, event, parent=None):
        auxinfo = {}
        if self._mouse_on == False:
            self._mouse_on = True
            auxinfo["mouse_entered"] = True

        return MouseOverEvent(event, self.wid, self, auxinfo=auxinfo)

    def set_mouse_leave(self):
        self._mouse_on = False


def _build_box_n_textbox(label, textprops, width=None):
    if isinstance(label, str):
        box = TextArea(label, textprops=textprops, fixed_width=width)
        textbox = box
    elif isinstance(label, OffsetBox):
        box = label
        textbox = None
    else:
        raise ValueError("incorrect label")

    return box, textbox


class Label(LabelBase):
    """A widget where you can place text or other box.

    Parameters
    ----------
    wid : str
       The widget ID.
    label : str or OffsetBox
       The label string or an instance of OffsetBox to be displayed
    fixed_width : float
       the width of the label. When None, the width will be calculated based on the rendered length of the string. Default is None.
    auxinfo : dict
       auxilary information to be returned with status. Default is empty dict.

    Examples
    --------

    >>> w1 = W.Button("btn", "Button")
    >>> install_widgets_simple(ax, [w1])
    """
    def __init__(
        self,
        wid,
        label,
        pad=None,
        draw_frame=True,
        auxinfo=None,
        fixed_width=None,
        textprops=None,
        **kwargs,
    ):

        _props = self._get_default_textprops()
        if textprops is not None:
            _props.update(textprops)

        box, textbox = _build_box_n_textbox(
            label, _props, width=fixed_width
        )
        LabelBase.__init__(
            self,
            wid,
            box,
            textbox=textbox,
            pad=pad,
            draw_frame=draw_frame,
            auxinfo=auxinfo,
            **kwargs,
        )

    def get_event_area(self, renderer):
        return self.patch.get_window_extent()

    def handle_button_press(self, event, parent=None):
        return WidgetBoxEvent(event, self.wid, auxinfo=self.auxinfo)


class Title(Label):
    def _get_default_textprops(self):
        return dict(weight="bold")

    # def _update_patch(self, patch):
    #     pass
    #     # patch.update(dict(ec="none", fc="0.9"))


class Button(LabelBase):
    default_contextual_themes = {
        "disabled": dict(fc="#cccccc", ec="#cccccc"),
        "disabled-hover": dict(fc="#cccccc", ec="#cccccc"),
        "default": dict(fc="#6200cc", ec="#6200ee"),
        "default-hover": dict(fc="#6200ee", ec="#6200ee"),
    }

    def _get_textprops(self):
        return dict(color="w")

    def set_context(self, c):
        self._context = c

    def get_event_area(self, renderer):
        return self.button_box.patch.get_window_extent()

    def _get_tooltip_anchor(self):
        return self.button_box.patch

    def __init__(
        self,
        wid,
        label,
        pad=3.0,
        mode=None,
        draw_frame=True,
        contextual_themes=None,
        **kwargs,
    ):

        self._context = ""
        themes = {} if contextual_themes is None else contextual_themes
        self.set_contextual_themes(themes)

        box, textbox = _build_box_n_textbox(label, self._get_textprops())

        if mode not in ["expand", "center", None]:
            raise ValueError(f"Unknown value of mode '{mode}'")

        expand = True if mode == "expand" else False
        centered = True if mode == "center" else False

        if centered:
            self.button_box = Centered(box, pad=pad, draw_frame=draw_frame)
        else:
            self.button_box = BaseWidget(
                box, pad=pad, draw_frame=draw_frame, expand=expand
            )

        super().__init__(
            wid,
            self.button_box,
            textbox=textbox,
            pad=3,
            draw_frame=False,
            # expand=expand,
            **kwargs,
        )

    def set_contextual_themes(self, themes):

        contextual_themes = self.default_contextual_themes.copy()
        contextual_themes.update(themes)
        self._contextual_themes = contextual_themes


    def _init_patch_n_context(self, patch):
        patch = self.button_box.patch

        patch.set_boxstyle("round,pad=0.3")
        patch.set_mutation_scale(8)


    def _make_shadow(self, patch):
        # patch.update(dict(fc="#6200ee", ec="#6200ee"))  # patch_attrs

        from matplotlib import patheffects

        offset = (2, -2)
        patch.set_path_effects(
            [  # patheffects.withSimplePatchShadow(),
                patheffects.SimpleLineShadow(
                    offset=offset, shadow_color="0.9", alpha=1.0, linewidth=3.0
                ),
                patheffects.SimpleLineShadow(
                    offset=offset, shadow_color="0.8", alpha=1.0, linewidth=1.5
                ),
                patheffects.SimplePatchShadow(
                    offset=offset, shadow_rgbFace="0.7", foreground="none", alpha=1.0
                ),
                patheffects.Normal(),
            ]
        )

    def handle_button_press(self, event, parent=None):
        return WidgetBoxEvent(event, self.wid, auxinfo=self.auxinfo)

    def _update_patch_with_context(self, renderer):
        patch = self.button_box.patch


        context = self._context if self._context else "default"

        if self._mouse_on:
            context += "-hover"

        default_dict = self._contextual_themes["default"]
        t = self._contextual_themes.get(context, default_dict)

        patch.update(t)

        if not context.startswith("disabled"):
            self._make_shadow(patch)
        else:
            patch.set_path_effects(None)


        # if self._contextual_themes:
        #     context = self._context

        #     if self._mouse_on:
        #         context += "-hover"

        #     t = self._contextual_themes.get(context, None)
        #     if t is None:
        #         t = self._contextual_themes["default"]
        #     patch.update(t)

        # else:
        #     if self._context == "disabled":
        #         patch.update(dict(fc="#cccccc", ec="#cccccc"))
        #     else:
        #         patch.update(dict(fc="#6200ee", ec="#6200ee"))  # patch_attrs
        #         if self._mouse_on:
        #             patch.update(dict(fc="#6200ee"))
        #         else:
        #             patch.update(dict(fc="#6200cc"))

        # patch = self.button_box.patch
        # self._make_shadow(patch)

    def _update_patch_for_mouse_over(self, renderer):
        patch = self.button_box.patch

        if self._mouse_on:
            patch.update(dict(fc="#6200ee"))
        else:
            patch.update(dict(fc="#6200cc"))

    def draw(self, renderer):

        self._update_patch_with_context(renderer)

        return super().draw(renderer)

    def draw_with_outer_bbox(self, renderer, outer_bbox):

        self._update_patch_with_context(renderer)

        return super().draw_with_outer_bbox(renderer, outer_bbox)


class Sub(LabelBase):
    def _get_tooltip_anchor(self):
        return self._button_label

    def build_label(self, button_label):

        fontprop_solid = get_icon_fontprop(family="solid", size=10)
        button = TextArea(
            fa_icons["plus"], textprops=dict(fontproperties=fontprop_solid, color="b")
        )

        label = HPacker(children=[button_label, button], pad=1, sep=2, align="baseline")
        return label

    def __init__(
        self, wid, label, widgets, pad=None, draw_frame=True, where="selected", **kwargs
    ):

        box, textbox = _build_box_n_textbox(label, self._get_default_textprops())
        self._button_label = box
        label_box = self.build_label(self._button_label)

        super().__init__(
            wid, label_box, textbox=textbox, pad=pad, draw_frame=draw_frame, **kwargs
        )
        self.patch.update(dict(ec="none", fc="#FFFFDD"))

        # self.set_popup_widgets(widgets)
        self.sub_widgets = widgets
        self.where = where

    def handle_button_press(self, event, parent=None):

        if self.where == "selected":
            a = self
        else:
            a = parent.get_box()

        callback_info = dict(command="add_sub", a=a, widgets=self.sub_widgets)

        return WidgetBoxEvent(event, self.wid, callback_info=callback_info)


class SelectableBase:
    def get_default_box(self, l, tooltip):
        if isinstance(l, str):
            box = TextArea(l)
            box.set_tooltip(tooltip)
        else:
            box = l

        return box

    def get_boxes(self, labels, tooltips=None):
        boxes = []
        if tooltips is None:
            tooltips = [None] * len(labels)

        if len(tooltips) != len(labels):
            raise ValueError("The length of tolltips should match labels")

        for l, t in zip(labels, tooltips):
            box = self.get_default_box(l, tooltip=t)
            boxes.append(box)
            # if isinstance(l, str):
            # else:
            #     boxes.append(l)

        return boxes


class Dropdown(Sub, SelectableBase):
    def build_label(self, button_label):
        # button_label.set_text(label)

        fontprop_solid = get_icon_fontprop(family="solid", size=10)
        # fontprop_regular = get_icon_fontprop(family="regular", size=10)
        button = TextArea(
            fa_icons["caret-down"],
            textprops=dict(fontproperties=fontprop_solid, color="red"),
        )

        label = HPacker(children=[button, button_label], pad=1, sep=2, align="baseline")
        return label

    def get_default_box(self, l):
        box = Label(l, l)
        return box

    def update_value(self, v):
        self._button_label.set_text(v)

    def get_boxes(self, widgets):
        self.menu = DropdownMenu(
            self.wid + ":select", widgets, update_func=self.update_value, pad=0
        )
        menu = [self.menu]
        return menu

    def __init__(
        self, wid, label, widgets, pad=None, draw_frame=True, where="selected", **kwargs
    ):

        super().__init__(
            wid, label, [], pad=pad, draw_frame=draw_frame, where=where, **kwargs
        )
        widgets = self.get_boxes(widgets)
        self.sub_widgets = widgets

        v = self.menu.get_status()["value"]
        self.update_value(v)

        self.patch.update(dict(ec="none", fc="#FFFFDD"))

    def handle_button_press(self, event, parent=None):

        if self.where == "selected":
            a = self
        else:
            a = parent.get_box()

        callback_info = dict(
            command="add_sub",
            a=a,
            widgets=self.sub_widgets,
            xy=(0, 0),
            xybox=(0, -5),
            sticky=False,
        )

        return WidgetBoxEvent(event, self.wid, callback_info=callback_info)

    def get_status(self):
        return dict(value=self._button_label.get_text())


class Radio(BaseWidget, WidgetBoxEventHandlerBase, SelectableBase):
    def _populate_buttons(self):
        SELECTED_ON = fa_icons["circle-dot"]
        SELECTED_OFF = fa_icons["circle"]
        color = "blue"

        fontprop_solid = get_icon_fontprop(family="solid", size=10)
        fontprop_regular = get_icon_fontprop(family="regular", size=10)
        self.button_on = TextArea(
            SELECTED_ON, textprops=dict(fontproperties=fontprop_solid, color=color)
        )
        self.button_off = TextArea(
            SELECTED_OFF, textprops=dict(fontproperties=fontprop_regular, color=color)
        )

    def _set_figure_extra(self, fig):
        self.button_on.set_figure(fig)
        self.button_off.set_figure(fig)

    def set_figure(self, fig):
        super().set_figure(fig)
        self._set_figure_extra(fig)

    def get_default_box(self, l, tooltip=None):
        if isinstance(l, str):
            t = Label("", l)
            t.set_tooltip(tooltip)
            box = HWidgets(
                children=[self.button_off, t], pad=1, sep=2, align="baseline"
            )
        else:
            box = HWidgets(
                children=[self.button_off, l], pad=1, sep=2, align="baseline"
            )

        return box

    def __init__(
        self,
        wid,
        labels,
        selected=None,
        values=None,
        title=None,
        tooltips=None,
        pad=3,
        direction="v",
    ):
        if tooltips is None:
            tooltips = [None] * len(labels)

        if len(tooltips) != len(labels):
            raise ValueError("The length of tolltips should match labels")

        self._populate_buttons()

        self.wid = wid

        # label_box = TextArea("Label:")
        if title is not None:
            label_box = HPacker(
                children=[TextArea(title)], pad=1, sep=2, align="baseline"
            )
            self.boxes = [label_box]
            self._title_offset = 1
        else:
            self.boxes = []
            self._title_offset = 0

        self.values = values if values is not None else labels

        self.boxes.extend(self.get_boxes(labels, tooltips=tooltips))

        kwargs = {}
        if direction == "h":
            box = HPacker(children=self.boxes, pad=0, sep=3, **kwargs)
        elif direction == "v":
            box = VPacker(children=self.boxes, pad=0, sep=3, **kwargs)
        else:
            raise ValueError("unknown dir value of '{dir'}")

        BaseWidget.__init__(self, box, pad=pad, draw_frame=True)
        WidgetBoxEventHandlerBase.__init__(self, box)

        self._update_patch(self.patch)

        self.initialize_selections(selected)

    def initialize_selections(self, selected):
        selected = 0 if selected is None else selected

        self.select(selected)

    def replace_labels(self, labels, values=None):
        new_labels = self.get_boxes(labels)
        for l in new_labels:
            l.set_figure(self.figure)
        self.boxes[self._title_offset :] = new_labels

        if values is None:
            values = labels

        self.values = values

    def _update_patch(self, patch):
        # patch.update(dict(ec="none"))
        self.patch.update(dict(ec="#AAEEEE", fc="#EEFFFF"))

    def select(self, i):
        """
        if i is larger than len(values) or smaller than 0, it will
        automatically wrapped around.
        """
        if i is None:
            i = 0

        i = i % len(self.values)

        o = self._title_offset

        for _i, b in enumerate(self.boxes[o:]):
            if _i == i:
                b.get_children()[0] = self.button_on
            else:
                b.get_children()[0] = self.button_off

        # self.selected[:] = [i]
        self.selected = i

        return i

    def handle_motion_notify(self, event, parent=None):
        _, b = self.get_responsible_child(event)
        if b is not None:
            children = b.get_visible_children()
            if len(children) > 1:
                b1 = b.get_visible_children()[1]
                return b1.handle_motion_notify(event, parent)

    def handle_button_press(self, event, parent=None):
        i, b = self.get_responsible_child(event)

        i -= self._title_offset

        if i >= 0:
            self.select(i)

        return WidgetBoxEvent(event, self.wid, dict(lid=i, widget=b))

    def get_status(self):
        return dict(selected=self.selected, value=self.values[self.selected])


class DropdownMenu(Radio):
    """
    The selection menu when dropdown button is pressed.
    """

    def __init__(
        self,
        wid,
        labels,
        selected=None,
        values=None,
        title=None,
        pad=0,
        update_func=None,
    ):
        super().__init__(
            wid, labels, selected=selected, values=values, title=title, pad=pad
        )
        self._update_func = update_func

    def _update_patch(self, patch):
        patch.update(dict(ec="none"))
        # pass
        # self.patch.update(dict(ec="#AAEEEE", fc="#EEFFFF"))

    def _populate_buttons(self):
        SELECTED_ON = fa_icons["angles-right"]
        color = "red"

        fontprop_solid = get_icon_fontprop(family="solid", size=10)
        fontprop_regular = get_icon_fontprop(family="regular", size=10)
        self.button_on = TextArea(
            SELECTED_ON, textprops=dict(fontproperties=fontprop_solid, color=color)
        )
        self.button_off = TextArea(
            SELECTED_ON, textprops=dict(fontproperties=fontprop_solid, color="w")
        )

    def handle_button_press(self, event, parent=None):
        i, b = self.get_responsible_child(event)

        i -= self._title_offset

        if i >= 0:
            self.select(i)

        if self._update_func is not None:
            callback_info = dict(
                command="update_widget",
                update_func=self._update_func,
                value=self.values[i],
            )
        else:
            callback_info = None

        return WidgetBoxEvent(event, self.wid, callback_info=callback_info)


class CheckBox(Radio):
    # button_on = TextArea(SELECTED_ON)
    # button_off = TextArea(SELECTED_OFF)
    # button_on = OffsetImage(ff[8]["check_button_on"])
    # button_off = OffsetImage(ff[8]["check_button_off"])

    def _populate_buttons(self):
        SELECTED_ON = fa_icons["square-check"]
        SELECTED_OFF = fa_icons["square"]
        color = "blue"

        fontprop_solid = get_icon_fontprop(family="solid", size=10)
        fontprop_regular = get_icon_fontprop(family="regular", size=10)
        self.button_on = TextArea(
            SELECTED_ON, textprops=dict(fontproperties=fontprop_solid, color=color)
        )
        self.button_off = TextArea(
            SELECTED_OFF, textprops=dict(fontproperties=fontprop_regular, color=color)
        )

    def initialize_selections(self, selected):
        self.selected = []
        if selected is None:
            return

        for i in selected:
            self.select(i)

    def select(self, i):
        if i is None:
            return

        o = self._title_offset

        b = self.boxes[o + i]
        if i in self.selected:
            self.selected.remove(i)
            b.get_children()[0] = self.button_off
        else:
            self.selected.append(i)
            b.get_children()[0] = self.button_on

    def get_status(self):
        return dict(
            selected=self.selected, values=[self.values[s] for s in self.selected]
        )


class RadioButton(Radio):
    def get_default_box(self, l, tooltip=None):

        contextual_themes = {
            "selected": dict(fc="#62eeee"),
            "selected-hover": dict(fc="#62cccc"),
            "default": dict(fc="w"),
        }

        if isinstance(l, str):
            box = Button(
                self.wid + ":" + l,
                TextArea(l),
                contextual_themes=contextual_themes,
                tooltip=tooltip,
            )
        else:
            box = Button(
                self.wid + ":" + str(l),
                l,
                contextual_themes=contextual_themes,
                tooltip=tooltip,
            )

        return box

    def get_boxes(self, labels, tooltips=None):
        boxes = []
        if tooltips is None:
            tooltips = []

        for l, t in zip_longest(labels, tooltips, fillvalue=None):
            box = self.get_default_box(l, t)
            boxes.append(box)
            # if isinstance(l, str):
            # else:
            #     boxes.append(l)

        return boxes

    def __init__(
        self, wid, labels, selected=None, values=None, tooltips=None, title=None, pad=3
    ):
        # self.selected = self.get_initial_selected(selected)

        self.wid = wid

        self.boxes = []
        self._title_offset = 0

        self.values = values if values is not None else labels

        self.boxes.extend(self.get_boxes(labels, tooltips))

        kwargs = {}
        box = HPacker(children=self.boxes, pad=0, sep=3, **kwargs)

        BaseWidget.__init__(self, box, pad=pad, draw_frame=True)
        WidgetBoxEventHandlerBase.__init__(self, box)

        self._update_patch(self.patch)

        self.initialize_selections(selected)

    def select(self, i):
        if i is None:
            i = 0

        o = self._title_offset

        for _i, b in enumerate(self.boxes[o:]):
            if _i == i:
                b.set_context("selected")
            else:
                b.set_context("")

        self.selected = i

    def _set_figure_extra(self, fig):
        pass

    def handle_motion_notify(self, event, parent=None):
        i, b = self.get_responsible_child(event)

        if b is not None:
            return b.handle_motion_notify(event, parent)
