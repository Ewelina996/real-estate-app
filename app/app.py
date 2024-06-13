import folium
import streamlit as st
import geopandas as gpd
import pickle 
import pandas as pd
from streamlit_folium import folium_static
from functions.maps import MapCreator
from functions.user_features import user_input_features

# Load the model
model = pickle.load(open('model.pkl', 'rb'))

st.write(""" 
# Prognozowanie ceny mieszkania w Krakowie
""")

st.sidebar.header('Wprowadź dane')
df, user_data, otodom = user_input_features()
df_pred = pd.DataFrame(df.iloc[-1]).T
prediction = model.predict(df_pred)
user_data = pd.DataFrame(user_data, index=[0])
st.table(user_data.assign(hack='').set_index('hack'))
st.subheader(f'Przewidywana cena twojego mieszkania: {prediction[0]:.0f} zł')
cena_lokalizacja = otodom.groupby('localization').price.mean().reset_index()
user_cena_lokalizacja = cena_lokalizacja[cena_lokalizacja['localization']==user_data['localization'][0]]
st.subheader(f'Średnia cena w tej lokalizacji to: {user_cena_lokalizacja["price"].values[0]:.0f} zł')

map = MapCreator(otodom, gpd.read_file('krakow-dzielnice.geojson'))
map.preprocess_data()
map.create_map()
m = map.display_map()
folium_static(m)