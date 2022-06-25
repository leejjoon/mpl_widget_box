from abc import ABC, abstractmethod
from typing import List

from .widgets import BaseWidget


class CompositeWidget(ABC):
    @abstractmethod
    def build_widgets(self) -> List[BaseWidget]:
        pass

    @abstractmethod
    def post_install(self, wbm):
        pass

    @abstractmethod
    def post_uninstall(self, wbm):
        pass
