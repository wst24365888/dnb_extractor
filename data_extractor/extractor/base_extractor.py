from __future__ import annotations
import abc
from typing import List, Set
from data_extractor.filter.base_filter import BaseFilter

class BaseExtractor:
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def extract(self) -> Set[str]:
        pass