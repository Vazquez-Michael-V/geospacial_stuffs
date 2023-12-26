# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 00:50:35 2023

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
import datetime
import pytz

import json


# Need a list of all 50 state names in USA, and District of Columbia.
wiki_list = pd.read_html("https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States")

# States table is the 1 indexed element in the list.
# len(wiki_list)
# wiki_list[1].shape
# wiki_list[1].head()
# for num, df in enumerate(wiki_list):
#     try:
#         if ("Flag") in wiki_list[num].columns.to_flat_index()[0][0]:
#             print(f'list index: {num}')
#             print(df.columns.to_flat_index())
#             time.sleep(5)
#         else:
#             pass
#     except IndexError:
#         pass


# District of Columbia is the 2 indexed element in the list.
# wiki_list[2].head()

### Obtain the states DataFrame. ###
df_states = wiki_list[1].copy()
df_states.columns = df_states.columns.to_flat_index()
states_og_cols = df_states.columns.to_list()
states_rename_cols = ['state_name', 'state_abbrev', 'capital', 'city_largest',
                      'admission', 'pop_2020', 'total_area_mi_sq', 'total_area_km_sq',
                      'land_area_mi_sq', 'land_area_km_sq', 'water_area_mi_sq', 'water_area_km_sq',
                      'num_reps']

states_dict = {k:v for k,v in zip(states_og_cols, states_rename_cols)}
df_states = df_states.rename(columns=states_dict)
df_states['state_name'] = df_states['state_name'].str.replace("[B]", "").str.strip()
print(f"{df_states['state_name'].nunique()} unique state names.")
print("df_states info:")
print(df_states.info())
print(f'df_states shape: {df_states.shape}')
###

### Obtain the DC DataFrame. ###
# Line up the DC columns with the states columns.
df_dc = wiki_list[2].copy()
df_dc.columns = df_dc.columns.to_flat_index()
df_dc.insert(2, "capital", np.nan)
df_dc.insert(3, "city_largest", np.nan)
dc_og_cols = df_dc.columns.to_list()
# len(dc_og_cols)
dc_rename_dict = {k:v for k,v in zip(dc_og_cols, states_rename_cols)}
df_dc = df_dc.rename(columns=dc_rename_dict)
df_dc['state_name'] = df_dc['state_name'].str.strip()
df_dc['admission'] = df_dc['admission'].str.replace("[13]", "").str.strip()
df_dc['num_reps'] = df_dc['num_reps'].str.replace("[C]", "").str.strip()
print(f"{df_dc['state_name'].nunique()} state in df_dc.")
print("df_dc info:")
print(df_dc.info())
print(f'df_dc shape: {df_dc.shape}')
###

### Concat states and DC. ###
df_states_dc = pd.concat([df_states, df_dc]) \
    .sort_values(by=['state_name']) \
    .reset_index(drop=True)

print(f"{df_states_dc['state_name'].nunique()} states in df_states_dc['state_name']")
print(f"{df_states_dc['state_abbrev'].nunique()} state abrreviations in df_states_dc['state_abbrev']")
print(f'df_states_dc shape: {df_states_dc.shape}')
print("df_states_dc info:")
print(df_states_dc.info())
# Send df_states_dc to csv for easy use later, if needed.
df_states_dc.to_csv(r'C:\Users\plott\OneDrive\Desktop\python_work\geo_projects\df_states_dc.csv', index=False)
###

# Obtain the states list, including DC.
states_list = list(df_states_dc['state_name'].unique())

# Webscrape the Whole Foods website for store locations in the United States.
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--incognito')

PATH = "C:\Program Files (x86)\chromedriver.exe" #Directory of the Chromedriver
serv = Service(PATH)
driver = webdriver.Chrome(service=serv, options=chrome_options)

WEBSITE = "https://www.wholefoodsmarket.com/stores"
driver.get(WEBSITE)
driver.maximize_window()
web_title = driver.title
print(WEBSITE)
print(web_title)

time.sleep(2)

timezone_est = pytz.timezone('US/Eastern')
scrape_timestamp_start = datetime.datetime.now(tz=timezone_est).strftime('%Y-%m-%d %I:%M:%S %p')
print(f'Starting web scrape {scrape_timestamp_start}')


stores_search_bar = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'store-finder-search-bar'))
    )

print(type(stores_search_bar))

dfs_stores = []
for state in states_list:
    ActionChains(driver) \
    .send_keys_to_element(stores_search_bar, state) \
    .send_keys_to_element(stores_search_bar, Keys.RETURN) \
    .perform()
    # 5 seconds to let the results load.
    time.sleep(5)
    store_finder = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'w-store-finder__store-list'))
        )
    # store_finder_ul = store_finder.find_elements(By.TAG_NAME, 'ul')
    # store_finder_ul = store_finder.find_elements(By.TAG_NAME, 'li')
    # store_finder_ul = store_finder.find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
    store_finder_li = store_finder.find_elements(By.TAG_NAME, 'li')
    # store_finder_ul.get_property('dataset')
    print(type(store_finder_li))
    for store_li in store_finder_li:
        type(store_li)
        if len(store_li.get_property('dataset')) > 0:
            # All of the non zero length dataset properties are formatted 'data-bu'.
            # print(store_li.get_property('dataset'))
            # print(type(store_li.get_property('dataset')))
            # print(store_li.get_property('innerText'))
            store_li_dict = store_li.get_property('dataset')
            print(store_li_dict)
            print(type(store_li_dict))
            store_finder_core_info = store_li.find_element(By.CLASS_NAME, 'w-store-finder-core-info')
            store_address = [s.text for s in store_finder_core_info.find_elements(By.CLASS_NAME, 'w-store-finder-mailing-address')]
            print(store_address)
            # TODO: Need the store lat and long.
            # store_coord = store_finder_core_info.find_element(By.PARTIAL_LINK_TEXT, "https://www.google.com/maps/dir/?api=")
            store_coord = \
                store_finder_core_info.find_element(By.ID, f"linksQuad{store_li_dict['bu']}") \
                .find_element(By.TAG_NAME, 'a') \
                .get_attribute('href')
            print("store_coord:")
            print(type(store_coord))
            print(store_coord)
            # https://www.google.com/maps/dir/?api=1&destination=39.908072,-74.937997
            df_store_temp = pd.DataFrame(data={'store_id': [int(store_li_dict['bu'])],
                                               'store_street': store_address[0],
                                               'store_city_state_zip': store_address[1],
                                               'store_coord_link': store_coord})
            print(df_store_temp.shape)
            dfs_stores.append(df_store_temp)

        else:
            pass
    
    # Clear the search bar using control a delete.
    ActionChains(driver) \
    .send_keys_to_element(stores_search_bar, Keys.CONTROL) \
    .send_keys_to_element(stores_search_bar, "a") \
    .send_keys_to_element(stores_search_bar, Keys.DELETE) \
    .perform()
    time.sleep(2)

# https://www.google.com/maps/dir/?api=1&destination=39.908072,-74.937997
# id linksQuad10526

# w-store-finder-core-info

df_stores = pd.concat(dfs_stores).reset_index(drop=True)
print(f'df_stores shape: {df_stores.shape}')

# df_stores['store_id'].nunique()
# df_stores['store_id'].value_counts().sort_values(ascending=False).head(20)
# Store id 10651 appears when DC, Florida, and Washington are searched.
# df_stores.loc[(df_stores['store_id'] == 10651), :]

df_stores = df_stores.drop_duplicates(subset=['store_id']).reset_index(drop=True)
print(f'df_stores shape: {df_stores.shape}')
# Clean up the state, city, and zip info.
df_stores['store_city_state_zip'] = df_stores['store_city_state_zip'].str.strip()
df_stores[['store_city', 'store_state_zip']] = df_stores['store_city_state_zip'].str.split(",", expand=True).apply(lambda x: x.str.strip())
df_stores[['store_state', 'store_zip']] = df_stores['store_state_zip'].str.split(" ", expand=True).apply(lambda x: x.str.strip())
df_stores = df_stores.drop(columns=['store_city_state_zip', 'store_state_zip'])
# Obtain the lat and long columns. Keep the google maps link, just in case.
df_stores[['store_lat', 'store_long']] = \
    df_stores['store_coord_link'].str.split("=", expand=True)[2] \
    .str.split(",", expand=True)

print(f'df_stores shape: {df_stores.shape}')


df_stores.to_csv(r'some_dir\wfm_stores_usa.csv')

