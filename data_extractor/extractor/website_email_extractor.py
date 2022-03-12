from typing import Dict, List, Set
from data_extractor.filter.base_filter import BaseFilter
from data_extractor.filter.subpage_filter import SubpageFilter
from data_extractor.filter.email_filter import EmailFilter
from data_extractor.extractor.base_extractor import BaseExtractor
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebsiteEmailExtractor(BaseExtractor):
    def __init__(self, url: str, depth: int, all_emails: Dict[str, Set[str]]) -> None:
        self.url = url

        # www.example.com, etc.
        if not self.url.startswith("http"):
            self.url = f"https://{self.url}"

        self.depth = depth
        self.all_emails = all_emails

        print(f"{self.url}: depth={self.depth}")

        self.subpage_filter = SubpageFilter(url)
        self.email_filter = EmailFilter()

        # Set user agent
        options = Options()
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36')
        # Headless mode
        options.add_argument('--headless')
        # Disable logs
        options.add_argument('--log-level=3')

        # Create a new instance of the Edge driver
        self.driver = webdriver.Edge(options=options)

    def extract(self) -> Set[str]:
        self.find_emails()
        
        # combine all emails
        emails: Set[str] = set()
        for url, email_set in self.all_emails.items():
            emails.update(email_set)

        return emails

    def find_emails(self) -> Dict[str, Set[str]]:
        if self.depth == 0 or self.url in self.all_emails:
            self.driver.quit()
            return self.all_emails

        try:
            self.driver.implicitly_wait(100)
            self.driver.get(self.url)
        except Exception as e:
            print(f"{self.url}: {e}")
            self.driver.quit()
            return self.all_emails
        
        self.data = self.driver.page_source
        self.driver.quit()

        emails: Set[str] = self.email_filter.filter(self.data)
        self.all_emails[self.url] = emails
        
        if self.depth - 1 > 0:
            subpagaes: Set[str] = self.subpage_filter.filter(self.data)
            for subpage in subpagaes:
                extractor = WebsiteEmailExtractor(subpage, self.depth - 1, self.all_emails)
                try:
                    result = extractor.find_emails()
                except Exception as e:
                    print(f"{subpage}: {e}")
                    continue

                if not result:
                    continue

                for url, email_set in result.items():
                    if url in self.all_emails:
                        self.all_emails[url].update(email_set)
                    else:
                        self.all_emails[url] = email_set

        return self.all_emails