# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 19:39:12 2023

@author: Michael Vazquez
"""


import pandas as pd
import numpy as np
import plotly


def great_circle_distance(lambda_1, phi_1, lambda_2, phi_2, r):
    """Compute the great circle distance with radius r and lat long coordinates.
    lambda <--> longitude
    phi <--> latitude
    https://en.wikipedia.org/wiki/Haversine_formula"""
    
    # print(f'lambda_1 = {lambda_1}')
    # print(f'phi_1 = {phi_1}')
    # print(f'lambda_2 = {lambda_2}')
    # print(f'phi_2 = {phi_2}')
    lambda_1, phi_1, lambda_2, phi_2 = [np.radians(deg) for deg in [lambda_1, phi_1, lambda_2, phi_2]]

    d = 2 * r * np.arcsin(
        np.sqrt(
            (((np.sin((phi_2 - phi_1)/2))**2) + ((np.cos(phi_1) * np.cos(phi_2)) * (np.sin((lambda_2 - lambda_1)/2)**2)))
            )
        )
    
    theta = d/r
    haversine = (np.sin((theta/2))**2)
    
    return {'d': d, 'theta': theta, 'haversine': haversine}


# Will webscrape for college locations and obtain a csv. Got a some random colleges from google maps for now.
df_colleges = pd.DataFrame(data={'name': ['Rutgers University New Brunsiwck', 'University of Florida',
                                          'Texas A&M University', 'Columbia University',
                                          'University of California, Berkeley', 'University of Kentucky',
                                          'Montana State University', 'University of South Alabama'],
                                 'longitude': [-74.40407738483181, -82.35327295998434,
                                               -96.33654060598519, -73.96257270366836,
                                               -122.25905292983549, -84.503197227578,
                                               -111.05399883088783, -88.18381757950283],
                                 'latitude': [40.51941445048781, 29.64675723519598,
                                              30.61890216588467, 40.80773036918585,
                                              37.870328756578374, 38.030777835366905,
                                              45.667517317094934, 30.69620811669505]})

df_colleges = df_colleges.add_prefix('college_')
print(df_colleges.info())


# Aldi stores in USA, obtaianed via webscraping.
df_aldi = pd.read_csv(r'some_dir\aldi_stores_usa.csv',
                      dtype={'zip_code': str})
# Forgot the as_index=False when I created the csv.
df_aldi = df_aldi.drop(columns=['Unnamed: 0'])
df_aldi = df_aldi.add_prefix('aldi_')
print(df_aldi.info())
print(df_aldi.shape)

# Earth radius in miles and km.
r_mi = 3958.8
r_km = 6371

df_aldi_colleges = pd.merge(df_aldi, df_colleges, how="cross")

# Aldi store distance to each college.
df_aldi_colleges['dist_mi'] = df_aldi_colleges[['aldi_longitude', 'aldi_latitude', 'college_longitude', 'college_latitude']]\
    .apply(lambda row: great_circle_distance(row['aldi_longitude'], row['aldi_latitude'],
                                             row['college_longitude'], row['college_latitude'],
                                             r_mi)['d'], axis=1)

print(df_aldi_colleges.info())
print(df_aldi_colleges.shape)
print("df_aldi_colleges['dist_mi'] describe:")
print(df_aldi_colleges['dist_mi'].describe())
