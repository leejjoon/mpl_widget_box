import logging


class EventHandlerBase:
    def get_child_widgets(self):
        return []

    def get_responsible_child(self, mpl_event):
        """
        returns a tuple of (index of the widget, and the widget itself)
        """
        renderer = mpl_event.canvas.get_renderer()

        for i, b in enumerate(self.get_child_widgets()):
            if not b.get_visible():
                # we skip invisible widgets
                continue
            if hasattr(b, "get_event_area"):
                w = b.get_event_area(renderer)
            else:
                w = b.get_window_extent(renderer)
            if w.contains(mpl_event.x, mpl_event.y):
                return i, b

        return -1, None

    def handle_event(self, event, parent=None):

        _, b = self.get_responsible_child(event)
        if hasattr(b, "handle_event"):
            e = b.handle_event(event, parent=parent)
        else:
            e = None
        return e

    def get_named_status(self):
        # raise ValueError()
        d = {}
        for w in self.get_child_widgets():
            d[w.wid] = w.get_status()

        return d

    def get_box(self):
        raise RuntimeError()


class WidgetsEventHandler(EventHandlerBase):
    def __init__(self, widgets):
        self._widgets = widgets

    def get_child_widgets(self):
        return self._widgets

    # def handle_event(self, event, parent=None):

    #     _, b = self.get_responsible_child(event)
    #     # print(b)
    #     if hasattr(b, "handle_event"):
    #         e = b.handle_event(event, parent=parent)
    #     else:
    #         # print(b)
    #         # print("No event handler defined")
    #         e = None
    #     return e

    def get_status(self):
        # raise ValueError()
        d = {}
        for w in self.get_child_widgets():
            d.update(w.get_status())

        return d

    def get_box(self):
        raise RuntimeError()


class WidgetBoxEventHandlerBase(EventHandlerBase):
    def __init__(self, box, debug=False):
        self.box = box

        self.logger = logging.getLogger()

    def get_child_widgets(self):
        return self.box.get_children()


# class WidgetBoxEventHandlerBase(EventHandlerBase):
#     def __init__(self, pack, children=None, debug=False):
#         self.pack = pack

#         if children is None:
#             children = pack.get_children()

#         self.children = children

#         self.logger = logging.getLogger()

#     def get_child_widgets(self):
#         return self.children


class WidgetBoxEventHandler(WidgetBoxEventHandlerBase):
    pass
