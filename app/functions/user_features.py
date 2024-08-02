import streamlit as st
import geopandas as gpd
import pickle 
import pandas as pd
import sklearn

model = pickle.load(open('model.pkl', 'rb'))
def user_input_features():
    lokalizacja = st.sidebar.selectbox('Lokalizacja',[ ' Stare Miasto', ' Podgórze', ' Podgórze Duchackie', ' Bieńczyce',
       ' Prądnik Biały', ' Prądnik Czerwony', ' Krowodrza',
       ' Zwierzyniec', ' Dębniki', ' Łagiewniki-Borek Fałęcki',
       ' Bronowice', ' Osiedle Oficerskie', ' Czyżyny', ' ul. Wiślicka',
       ' ul. Lea', ' Mistrzejowice', ' Bieżanów-Prokocim', ' Rakowice',
       ' Grzegórzki', ' Wzgórza Krzesławickie', ' Wieliczka',
       ' Krowodrza Górka', ' Nowa Huta', ' Swoszowice',
       ' ul. Radzikowskiego'], key='localization')
    powierzchnia = st.sidebar.number_input('Powierzchnia', value=60)
    liczba_pokoi = st.sidebar.number_input('Liczba pokoi', value=2)
    status_mieszkania = st.sidebar.selectbox('Status mieszkania', ['do wykończenia', 'do zamieszkania', 'do remontu'], key='status')
    piętro = st.sidebar.number_input('Piętro', value=1)
    rodzaj_ogrzewania  = st.sidebar.selectbox('Rodzaj ogrzewania', ['miejskie', 'gazowe', 'elektryczne', 'inne', 'kotłownia'], key='heating_type')
    balkon = st.sidebar.selectbox('Balkon', ['tak', 'nie'], key='balkon')
    ogródek = st.sidebar.selectbox('Ogródek', ['tak', 'nie'], key='ogródek')
    taras = st.sidebar.selectbox('Taras', ['tak', 'nie'], key='taras')

    user_data = {'localization': lokalizacja,
            'rooms': liczba_pokoi,
            'area': powierzchnia,
            'status': status_mieszkania,
            'floor': piętro,
            'heating_type': rodzaj_ogrzewania,
            'balkon': balkon,
            'ogródek': ogródek,
            'taras': taras}
    user_input = pd.DataFrame(user_data, index=[0])
    user_input['balkon'] = user_input['balkon'].map({'tak': 1, 'nie': 0})
    user_input['ogródek'] = user_input['ogródek'].map({'tak': 1, 'nie': 0})
    user_input['taras'] = user_input['taras'].map({'tak': 1, 'nie': 0})
    user_input['floor']=user_input['floor'].astype(object)

    otodom_clean = pd.read_csv('cleaned_data.csv')
    otodom_pred= otodom_clean.drop(columns=['price'])
    otodom_pred = pd.concat([otodom_pred, user_input], axis=0)
    otodom_pred = pd.get_dummies(otodom_pred, drop_first=True)
   
    column_names = model.feature_names_in_
    features = otodom_pred[column_names]
    features = pd.DataFrame(features.iloc[-1]).T

    return   features, user_data, otodom_clean