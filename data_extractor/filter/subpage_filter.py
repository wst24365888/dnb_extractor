from typing import Set
from urllib.parse import urlparse
from data_extractor.filter.base_filter import BaseFilter
import re

class SubpageFilter(BaseFilter):
    def __init__(self, url: str) -> None:
        self.url = url

    def filter(self, data: str) -> Set[str]:
        scheme, netloc = urlparse(self.url).scheme, urlparse(self.url).netloc

        results: Set[str] = set()

        # find all match in data
        
        # 1. sheme://netloc/new_path
        pattern = re.compile(f'(?<=href="{scheme}://{netloc}/)([a-zA-Z0-9\.\&\?\:@\-_=#][a-zA-Z0-9\.\&\/\?\:@\-_=#]*)(?=")')
        results.update([f"{scheme}://{netloc}/{m}" for m in pattern.findall(data)])

        # 2. netloc/new_path
        pattern = re.compile(f'(?<=href="{netloc}/)([a-zA-Z0-9\.\&\?\:@\-_=#][a-zA-Z0-9\.\&\/\?\:@\-_=#]*)(?=")')
        results.update([f"{scheme}://{netloc}/{m}" for m in pattern.findall(data)])

        # 3. href="/new_path"
        pattern = re.compile(f'(?<=href="/)([a-zA-Z0-9\.\&\?\:@\-_=#][a-zA-Z0-9\.\&\/\?\:@\-_=#]*)(?=")')
        results.update([f"{scheme}://{netloc}/{m}" for m in pattern.findall(data)])
        

        return results