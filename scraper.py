#!/bin/python

import io
import csv
import traceback
import lxml.etree
import requests
import requests.exceptions as reex
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from selenium.webdriver.firefox.options import Options
options = Options()
options.headless = True


def get_url(url:str, retries:int=3, timeout:tuple=(9.0, 21.0), headers:dict=None, cookies:dict=None):
    while retries:
        try:
            print(f'[*] Fetching url: {url}\n[*] Retries left: {retries}')
            response = requests.get(url, verify=False, headers=headers, cookies=cookies)
            response.raise_for_status()
            return response.content
        except (reex.Timeout, reex.HTTPError, reex.ConnectionError):
            retries -= 1
            traceback.print_exc(limit=1)
            sleep(5)

def parse_price(content:str) -> int:
    tree = lxml.etree.HTML(content)
    price_xpath = tree.xpath('//div[@class="sc-1xkgrh6-4 fkTMDj"]/text()')
    return int(''.join(number for number in price_xpath[0] if number.isdigit()))

def stream_data_from_csv(path:str) -> dict:
    with io.open(path, encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for i, item in enumerate(csv_reader):
            if i == 0:
                keys = item
                continue
            yield {k:v for k,v in zip(keys, item)}

def compare_prices(data_price: int, fetched_price: int) -> bool:
    if fetched_price < data_price:
        return True
    else:
        return False

def take_screeshot(url: str, driver: webdriver) -> str:
    driver.get(url)
    driver.save_screenshot("screenshot.png")
    driver.close()

def get_screenshot_filename(url: str) -> str:
    pass

def main():
    driver_path = '/Users/leovilhena/wakacje/'
    csv_path = '/Users/leovilhena/wakacje_scrape.csv'
    driver = webdriver.Firefox(driver_path, options=options)
    for data in stream_data_from_csv(csv_path):
        response = get_url(data['url_oferta'])
        parsed_price = parse_price(response)
        if compare_prices(int(data['cena']), parsed_price):
            take_screeshot(data['url_oferta'], driver)
        # TODO Write to csv file
        # TODO Post to blog and/or social media
        exit(0) # FIXME

if __name__ == '__main__':
    main()

