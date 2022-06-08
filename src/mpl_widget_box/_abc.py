from abc import ABC, abstractmethod

class PackedWidgetBase(ABC):
    @abstractmethod
    def get_child_widgets(self):
        return []

