from abc import ABC, abstractmethod
from typing import List

from .base_widget import BaseWidget


class PackedWidgetBase(ABC):
    @abstractmethod
    def get_child_widgets(self):
        return []


class CompositeWidgetBase(ABC):
    @abstractmethod
    def build_widgets(self) -> List[BaseWidget]:
        pass

    @abstractmethod
    def post_install(self, wbm):
        pass

    @abstractmethod
    def post_uninstall(self, wbm):
        pass
