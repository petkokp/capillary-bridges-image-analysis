from abc import ABC, abstractmethod
from typing import Callable, Any

class Camera(ABC):
    @abstractmethod
    def record(self, process: Callable[[Any, Any], None]):
        pass
    
    @abstractmethod
    def release(self):
        pass