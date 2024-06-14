import pandas as pd
import geopandas as gpd
import numpy as np
import folium

class MapCreator:
    def __init__(self, data, geodata):
        self.data = data
        self.geodata = geodata
        self.data_final = None
        self.m = None

    def preprocess_data(self):
        self.geodata['name'] = self.geodata['name'].apply(lambda x: ' '.join(x.split()[2:]))
        self.data['localization'] = self.data['localization'].apply(lambda x: x.strip())
        self.geodata['name'] = self.geodata['name'].apply(lambda x: x.strip())
        self.data_final = pd.merge(self.data, self.geodata, left_on='localization', right_on='name', how='left')
        self.data_final = gpd.GeoDataFrame(self.data_final)
        numeric_cols = self.data_final.select_dtypes(include=[np.number])
        data_final_numeric = numeric_cols.groupby('cartodb_id')
        mean_price = data_final_numeric['price'].mean().reset_index()
        self.data_final = pd.merge(self.data_final, mean_price, on='cartodb_id', how='left')
        self.data_final = self.data_final.rename(columns={'price_x': 'price', 'price_y': 'mean_price'})
        self.data_final['price'].dropna(inplace=True)

    def color_producer(self, value):
        if value < 500000:
            return 'green'
        elif 500000 <= value < 750000:
            return 'orange'
        elif 750000 <= value < 1000000:
            return 'red'
        else:
            return 'blue'

    def create_map(self):
        self.data_final = self.data_final.dropna(subset=['mean_price'])
        self.m = folium.Map(location=[self.data_final.geometry.centroid.y.mean(), self.data_final.geometry.centroid.x.mean()], zoom_start=11, height='100%', zoom_control=False)
        folium.GeoJson(
            self.data_final,
            style_function=lambda feature: {
                'fillColor': self.color_producer(feature['properties']['mean_price']),  # Change color based on price
                'color': 'black',
                'weight': 2,
                'dashArray': '5, 5'
        }
    ).add_to(self.m)

    def display_map(self):
        return self.m