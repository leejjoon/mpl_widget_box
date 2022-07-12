try:
    from typing import Protocol
except ImportError:
    # Protocol is available from python 3.8
    Protocol = object

class ForeignWidgetProtocol(Protocol):
    def draw(self, renderer):
        ...

    def purge_background(self):
        ...
