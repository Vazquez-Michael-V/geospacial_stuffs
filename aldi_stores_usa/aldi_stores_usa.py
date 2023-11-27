# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 14:01:10 2023

@author: Michael Vazquez
"""

#Selenium imports for website navigation.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
import numpy as np

import time
from datetime import datetime
import pytz

import json


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--incognito')


PATH = "C:\Program Files (x86)\chromedriver.exe" #Directory of the Chromedriver
serv = Service(PATH)
driver = webdriver.Chrome(service=serv, options=chrome_options)

WEBSITE = "https://stores.aldi.us/"
driver.get(WEBSITE)
driver.maximize_window()
web_title = driver.title
print(WEBSITE)
print(web_title)

time.sleep(2)

timezone_est = pytz.timezone('US/Eastern')
scrape_timestamp_start = datetime.now(tz=timezone_est).strftime('%Y-%m-%d %I:%M:%S %p')
print(f'Starting web scrape {scrape_timestamp_start}')

aldi_stores = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, 'Directory-content'))
    )

aldi_stores_dict = {state: {'stores_link': link} for state, link in zip(
    [link.find_element(By.TAG_NAME, 'a').get_attribute('innerText') for link in aldi_stores.find_elements(By.TAG_NAME, 'li')],
    [link.find_element(By.TAG_NAME, 'a').get_attribute('href') for link in aldi_stores.find_elements(By.TAG_NAME, 'li')]   
    )}

# Can use this if need to webscrape only certain states.
# aldi_stores_dict = {k:v for k,v in aldi_stores_dict.items()
#                     if (k in ['Washington DC', 'West Virginia', 'Wisconsin'])}


for state in aldi_stores_dict:
    aldi_store_url = aldi_stores_dict[state]['stores_link']
    driver.get(aldi_store_url)
    time.sleep(5)
    try:
        aldi_state_stores = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'Directory-content'))
            )
    # This exception only occurs for states with 1 store. 'Washington DC' has only 1 store.
    except TimeoutException:
        state_stores_links_list = [aldi_store_url]
    else:
        state_stores_links_list = \
            [link.find_element(By.TAG_NAME, 'a').get_attribute('href') for link in aldi_state_stores.find_elements(By.TAG_NAME, 'li')]
        print(f'\n{len(state_stores_links_list)} store links found for {state}.\n')
        print(driver.title)
    for aldi_state_store_link in state_stores_links_list:
        time.sleep(2)
        # aldi_state_store.click()
        driver.get(aldi_state_store_link)
        print(driver.title)
        time.sleep(2)
        # TODO: Maybe put a WebDriverWait here. time.sleep(2) seems to work fine for now.
        store_list = driver.find_elements(By.TAG_NAME, 'meta')
        # Some not important keys will duplicate and thus overwrite.
        store_dict = {meta: content for meta, content in zip(
            [meta.get_attribute('itemprop') for meta in store_list],
            [content.get_attribute('content') for content in store_list]
            )}
        store_dict = {k:v for k,v in store_dict.items() if not (k in [None, 'position', 'logo'])}
        print(store_dict)
        # The website has a different layout if there is more than 1 store in a city.
        # --> TimeoutException if the city has more than 1 Aldi store.
        try:
            address_id = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'address'))
                )
        except TimeoutException:
            stores_row = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'Directory-content'))
                )
            stores_row_links = [s.get_attribute('href') for s in stores_row.find_elements(By.CLASS_NAME, 'Teaser-titleLink')]
            print(stores_row_links)
            for stores_row_link in stores_row_links:
                driver.get(stores_row_link)
                time.sleep(5)
                print(driver.title)
                store_list = driver.find_elements(By.TAG_NAME, 'meta')
                # Some not important keys will duplicate and thus overwrite.
                store_dict = {meta: content for meta, content in zip(
                    [meta.get_attribute('itemprop') for meta in store_list],
                    [content.get_attribute('content') for content in store_list]
                    )}
                store_dict = {k:v for k,v in store_dict.items() if not (k in [None, 'position', 'logo'])}
                print(store_dict)
                # Copy and paste the lines from below the else block. Not worth making a function for this.
                address_id = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'address'))
                    )
                address_lines = [address_line.get_attribute('innerText') for address_line in address_id.find_elements(By.CLASS_NAME, 'Address-line')]
                print(address_lines)
                store_street = address_lines[0].strip()
                store_dict['street'] = store_street
                store_city = address_lines[1].split(sep=",")[0].strip()
                store_dict['city'] = store_city
                store_state = address_lines[1].split(sep=",")[1].strip()
                store_dict['state'] = store_state
                store_dict['zip_code'] = address_lines[2].strip()
                store_dict['store_page_title'] = driver.title
                print(store_dict)
                print("\n")
                # Use the city and street to make the key unique. Avoids overwriting keys with same state and city.
                aldi_stores_dict[store_state][f'{store_city} {store_street}'] = store_dict
                # time.sleep(2)
                driver.back()
            driver.back()

        else:       
            # Address is formated 'street', 'city, state', 'zip code'.
            address_lines = [address_line.get_attribute('innerText') for address_line in address_id.find_elements(By.CLASS_NAME, 'Address-line')]
        
            print(address_lines)
            store_dict['street'] = address_lines[0].strip()
            store_city = address_lines[1].split(sep=",")[0].strip()
            store_dict['city'] = store_city
            store_state = address_lines[1].split(sep=",")[1].strip()
            store_dict['state'] = store_state
            store_dict['zip_code'] = address_lines[2].strip()
            store_dict['store_page_title'] = driver.title
            print(store_dict)
            print("\n")
            aldi_stores_dict[store_state][store_city] = store_dict
            time.sleep(2)
            driver.back()        

    driver.back()
    driver.refresh()


with open(r'some_directory\aldi_stores_usa.json', 'w') as j:
    json.dump(aldi_stores_dict, j, indent=4)

dfs_list = []
for state in list(aldi_stores_dict.keys()):
    for city, info in aldi_stores_dict[state].items():
        print(state)
        print(city, info)
        if city != 'stores_link':
            # print(city,info)
            df_temp = pd.json_normalize(aldi_stores_dict[state][city])
            print(df_temp.shape)
            dfs_list.append(df_temp)
            print("\n")
        else:
            pass

df = pd.concat(dfs_list).reset_index(drop=True)

print(df.info())
print(df.shape)

print(df['store_page_title'].nunique())
print(df['state'].nunique())
print(df['state'].value_counts().sort_index())

df.to_csv(r'some_directory\aldi_stores_usa.csv')





