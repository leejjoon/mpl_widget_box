from . import widgets as W
from ._abc import CompositeWidgetBase



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
