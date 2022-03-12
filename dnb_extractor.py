from __future__ import annotations
from concurrent.futures import as_completed
from multiprocessing import Manager, cpu_count
import time
from typing import List, Optional, Tuple
from unittest import result
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data_extractor.extractor.website_email_extractor import WebsiteEmailExtractor
from concurrent.futures import ProcessPoolExecutor

class RestaurantInfo:
    def __init__(self, name: str, address: str, phone_number: str, url: str, emails: List[str]) -> None:
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.url = url
        self.emails = emails


def extract_emails(restaurant_link: str) -> Optional[RestaurantInfo]:
    # Set user agent
    options = Options()
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36')
    # Headless mode
    options.add_argument('--headless')
    # Disable logs
    options.add_argument('--log-level=3')
    
    # Create a new instance of the Edge driver
    d = webdriver.Edge(options=options)
    # Navigate to the restaurant page
    d.implicitly_wait(100)
    # Retry until it work
    while True:
        try:
            d.get(restaurant_link)
            # Get the restaurant name
            restaurant_name = d.find_element_by_css_selector('#content > div > div > div.company_profile_overview.basecomp.parbase.section > div > div.overview-container > div > div.company_profile_overview_body > div > div.col-md-6.company-profile-overview-starting-margin > div:nth-child(1) > span > span').text
            # Get the restaurant address
            restaurant_address = d.find_element_by_css_selector('#company_profile_snapshot > div:nth-child(2) > div.col-md-11 > span > span').text
            # Get the restaurant phone number
            restaurant_phone = d.find_element_by_css_selector('#company_profile_snapshot > div:nth-child(3) > div.col-md-11 > span > span').text
            
            break
        except Exception as e:
            time.sleep(10)

            continue


    try:
        # Get the restaurant website
        restaurant_website = d.find_element_by_css_selector('#hero-company-link').get_attribute('href')
        # Get the website email of the restaurant
        restaurant_email = WebsiteEmailExtractor(restaurant_website, 2, {}).extract()
        
        # Append the restaurant info to the list
        d.quit()
        return RestaurantInfo(restaurant_name, restaurant_address, restaurant_phone, restaurant_website, list(restaurant_email))
    except Exception as e:
        # Append the restaurant info to the list
        d.quit()
        return RestaurantInfo(restaurant_name, restaurant_address, restaurant_phone, '', [])

if __name__ == "__main__":
    all_restaurants: List[RestaurantInfo] = []

    for i in range(1, 21):
        # Set user agent
        options = Options()
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36')
        # Headless mode
        # options.add_argument('--headless')
        # Disable logs
        options.add_argument('--log-level=3')

        url = f'https://www.dnb.com/business-directory/company-information.restaurants_and_other_eating_places.us.washington.seattle.html?page={i}'

        # Create a new instance of the Edge driver
        driver = webdriver.Edge(options=options)

        # Navigate to the page you want to scrape
        driver.get(url)
        driver.implicitly_wait(10)

        # Get links to all restaurants
        restaurant_links_elems = driver.find_elements_by_css_selector('#companyResults > div > div.col-md-6 > a')
        restaurant_links = []

        # Loop through all restaurants
        for restaurant in restaurant_links_elems:
            # Get the link to the restaurant
            restaurant_links.append(restaurant.get_attribute('href'))
        
        with ProcessPoolExecutor(max_workers=cpu_count()-1) as executor:
            futures = []
            for restaurant_link in restaurant_links:
                futures.append(executor.submit(extract_emails, restaurant_link))

        for f in as_completed(futures):
            if f.result() is not None:
                all_restaurants.append(f.result())

        driver.quit()

    # Save the restaurant info to csv
    with open(f'restaurants.csv', 'w') as f:
        f.write('name,address,phone_number,url,emails\n')
        for restaurant in all_restaurants:
            f.write('"' + restaurant.name + '","' + restaurant.address + '","' + restaurant.phone_number + '","' + restaurant.url + '","' + ','.join(restaurant.emails) + '"\n')