from typing import Set
from urllib.parse import urlparse
from data_extractor.filter.base_filter import BaseFilter
import re

class EmailFilter(BaseFilter):
    def __init__(self) -> None:
        pass

    def filter(self, data: str) -> Set[str]:
        results: Set[str] = set()

        pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

        for m in pattern.findall(data):
            if m.split('.')[-1] in ['png', 'jpg']:
                continue

            results.add(m)

        return results