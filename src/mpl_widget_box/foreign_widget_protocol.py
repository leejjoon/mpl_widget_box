from typing import Protocol


class ForeignWidgetProtocol(Protocol):
    def draw(self, renderer):
        ...

    def purge_background(self):
        ...

