import streamlit as st
import pickle
import pandas as pd


# Load the model
model = pickle.load(open('model.pkl', 'rb'))

st.write(""" 
# Prognozowanie ceny mieszkania w Krakowie
""")

st.sidebar.header('Wprowadź dane')

def user_input_features():
    lokalizacja = st.sidebar.selectbox('Lokalizacja', [' Krowodrza', ' Prądnik Biały', ' Łagiewniki-Borek Fałęcki',
       ' Podgórze Duchackie', ' Stare Miasto', ' Bieżanów-Prokocim',
       ' Podgórze', ' Prądnik Czerwony', ' Dębniki', ' Nowa Huta',
       ' Zwierzyniec', ' Bieńczyce', ' Bronowice', ' Osiedle Oficerskie',
       ' Czyżyny', ' ul. Wiślicka', ' Grzegórzki', ' ul. Lea',
       ' Mistrzejowice', ' Rakowice', ' Wzgórza Krzesławickie',
       ' Wieliczka', ' Krowodrza Górka', ' Zielonki',
       ' ul. Radzikowskiego', ' Swoszowice'], key='localization')
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

    otodom_clean = pd.read_csv('otodom_data_cleaned.csv')
    otodom_clean = otodom_clean.drop(columns=['price'])
    otodom_clean = pd.concat([otodom_clean, user_input], axis=0)
    otodom_clean = pd.get_dummies(otodom_clean, drop_first=True)

    column_names = model.feature_names_in_
    features = otodom_clean[column_names]
    features = pd.DataFrame(features.iloc[-1]).T
    
    return  features
df = user_input_features()
df = pd.DataFrame(df.iloc[-1]).T
st.write(df)
prediction = model.predict(df)
st.write(f'Prognozowana cena mieszkania: {prediction[0]:.0f} zł')

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 5), gap='medium')

with col[0]:
    st.markdown('#### Coś')

with col[1]:
    st.markdown('#### Mapka')

with col[2]:
    st.markdown('#### Dzielnice/Średnia powierzchnia mieszkań w m2')

    data = pd.read_csv('cleaned_data.csv')
    df_average_area = data.groupby('localization')['area'].mean().sort_values(ascending=False)

    df_average_area = df_average_area.reset_index()
    df_average_area['area'] = df_average_area['area'].round(0)

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
    