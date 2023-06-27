# %%

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import folium_static
from shapely.geometry import LineString
from streamlit_js_eval import get_geolocation
import requests
import json
import osmnx as ox
from folium.plugins import HeatMap, MeasureControl
import networkx as nx
import geocoder
from polyline import decode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import polyline
from bs4 import BeautifulSoup
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation



req = requests.get('https://valencia.opendatasoft.com/api/records/1.0/search/?dataset=fgv-bocas&q=&rows=187')


def emt_vlc(response):
    emt = []
    if response.status_code == 200:
        data = response.json()
        recs = data['records']
        for record in recs:
            fields = record['fields']
            id = fields['denominacion']
            geo_point = fields['geo_point_2d']
            prox = fields['proximas_llegadas']
            lineas = fields['lineas']
            geo_shape = fields['geo_shape']
            emt.append((id, geo_point, prox, lineas, geo_shape))

    df2 = pd.DataFrame(emt, columns = ('nombre', 'geo_point_2d', 'prox_llegadas', 'lineas', 'geo_shape'))
    df2[['Latitude', 'Longitude']] = df2['geo_point_2d'].apply(pd.Series)
    
    return df2

estaciones = emt_vlc(req)
print(estaciones)

@st.cache_data
def get_horarios(str):
    horario = requests.get(str)
    if horario.status_code == 200:
        data = horario.content
        soup = BeautifulSoup(data, 'html.parser')
        div_elements = soup.find_all('div', style=lambda value: value and 'border-bottom' in value)
        kl = []
        for div in div_elements:
            span_elements = div.find_all('span')
            b_elements = div.find_all('b')
            destination = span_elements[2].text.strip()
            destination_f = b_elements[0].text.strip()
            departure_time = span_elements[4].text.strip()
            kl.append((destination, destination_f, departure_time))
    return kl


def search_location(name):
    best_match = process.extractOne(name, estaciones['nombre'], scorer=fuzz.ratio)
    if best_match is not None:
        closest_name = best_match[0]
        closest_row = estaciones[estaciones['nombre'] == closest_name].iloc[0]
        name, lat, long, hora = closest_row['nombre'], closest_row['Latitude'], closest_row['Longitude'], closest_row['prox_llegadas']
        return name, lat, long, hora
    else: 
        return None

def show_third_page():
    st.title("Buscador de estaciones FGV")
    if st.checkbox("Check my location"):
        loc = get_geolocation()
        latc = loc['coords']['latitude']
        longc = loc['coord'['longitude']]
        st.write(f"Your coordinates are {latc, longc}")
    text = st.text_input("Busque una estacion :", key = 'user_input')
    if not text:
        map5 = folium.Map()
        for _, row in estaciones.iterrows():
            folium.Marker(
                location = [row['Latitude'], row['Longitude']],
                tooltip=row['nombre'],
                icon=folium.Icon(color = 'red')
            ).add_to(map5)

        folium_static(map5)
    else:
        map6 = folium.Map()
        plugins.LocateControl(strings={"title": "See your current location", "popup": "Your position"}).add_to(map6)
        if text:
            nam = search_location(text)
            nam = list(nam)
            z, g, h, horas = nam
            if g and h != None:
                horario = get_horarios(horas)
                for i in horario:
                    linea = i[0]
                    destino = i[1]
                    salida = i[2]

                st.success("Estacion encontrada!")
                st.write("Estacion: ", z)
                lati, longi = g, h
                tlp_txt = f"""
                <span style="font-weight:bold;">Estacion:</span> {z}<br>
                <span style="font-weight:bold;">Linea:</span> {linea}<br>
                <span style="font-weight:bold;">Destino:</span> {destino}<br>
                <span style="font-weight:bold;">H. Salida:</span> {salida}
                """
                folium.Marker(location= [lati, longi], tooltip = tlp_txt, icon = folium.Icon(color = "black")).add_to(map6)

    folium_static(map6)











show_third_page()
