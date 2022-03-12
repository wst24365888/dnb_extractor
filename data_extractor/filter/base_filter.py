
import abc
from typing import Set


class BaseFilter:
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def filter(self, data: str) -> Set[str]:
        pass