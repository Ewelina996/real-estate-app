import folium
import streamlit as st
import geopandas as gpd
import pickle 
import pandas as pd
from streamlit_folium import folium_static
from functions.maps import MapCreator
from functions.user_features import user_input_features
import plotly.express as px

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

map = MapCreator(otodom, gpd.read_file('app/krakow-dzielnice.geojson'))
map.preprocess_data()
map.create_map()
m = map.display_map()
data = pd.read_csv('app/cleaned_data.csv')
df_average_area = data.groupby('localization')['area'].mean().sort_values(ascending=False)

df_average_area = df_average_area.reset_index()
df_average_area['area'] = df_average_area['area'].round(0)
#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 1.5), gap='small')

with col[0]:
    st.markdown('#### Coś')
    st.dataframe(df_average_area,
                 column_order=("localization", "area"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "localization": st.column_config.TextColumn(
                        "Localization",
                    ),
                    "area": st.column_config.ProgressColumn(
                        "Average area [m2]",
                        format="%f",
                        min_value=0,
                        max_value=max(df_average_area['area']),
                     )}
                 )
    
    

with col[1]:
    st.markdown('#### Średnia cena mieszkania w poszczególnych lokalizacjach (Niebeski najdroższy, pomarańczowy najtańszy)')
    folium_static(m)

with col[2]:
    st.markdown('#### Średnia powierzchnia mieszkania w poszczególnych lokalizacjach w metrach kwadratowych')

    

    st.dataframe(df_average_area,
                 column_order=("localization", "area"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "localization": st.column_config.TextColumn(
                        "Localization",
                    ),
                    "area": st.column_config.ProgressColumn(
                        "Average area [m2]",
                        format="%f",
                        min_value=0,
                        max_value=max(df_average_area['area']),
                     )}
                 )
size_counts = data.groupby('localization')['size'].value_counts(normalize=True).unstack().fillna(0)
size_counts = size_counts.reset_index().melt(id_vars='localization', value_name='Percentage')

fig = px.bar(size_counts, x='localization', y='Percentage', color='size', title='Udział poszczególnych koszyków wielkościowych w dzielnicach', color_continuous_scale='seismic')
fig.update_layout(xaxis_tickangle=-90)  # Rotate the x-axis labels for better readability
st.plotly_chart(fig, use_container_width=True)