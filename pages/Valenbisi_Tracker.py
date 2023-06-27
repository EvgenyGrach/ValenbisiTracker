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
from pages.Finder import show_secondary_page



place_name = "Valencia, Spain"


@st.cache_resource
def get_graph():
    graph = ox.graph_from_place(place_name, network_type="drive", simplify=True)
    street_geometries = ox.graph_to_gdfs(graph, nodes=False, edges=True)['geometry']
    return graph, street_geometries


request = requests.get('https://valencia.opendatasoft.com/api/records/1.0/search/?dataset=valenbisi-disponibilitat-valenbisi-dsiponibilidad&q=&rows=276')


def df_respuesta(response):
    p = []
    if response.status_code == 200:
        data = response.json()
        records = data['records']
        for record in records:
            record_id = record['recordid']
            fields = record['fields']
            geometry = record['geometry']
            ticket = fields['ticket']
            geo_point_2d = fields['geo_point_2d']
            open = fields['open']
            total = fields['total']
            number = fields['number']
            free = fields['free']
            available = fields['available']
            address = fields['address']
            geo_shape = fields['geo_shape']
            p.append((record_id, geometry, ticket, geo_point_2d, open, total, number, free, available, address, geo_shape))

        df = pd.DataFrame(p, columns = ('rocrd_id', 'geometry', 'ticket', 'geo_point_2d', 'open', 'total', 'number', 'free', 'available' , 'address', 'geo_shape'))
        df[['Latitude', 'Longitude']] = df['geo_point_2d'].apply(pd.Series)

    

        return df
    

def get_icon_color(value):
    if value < 5:
        return 'red'
    elif value > 15:
        return 'blue'
    else:
        return 'green'

    
bicis = df_respuesta(request)
oeste = bicis[['Latitude', 'Longitude']].min().values.tolist()
este = bicis[['Latitude', 'Longitude']].max().values.tolist()


def get_user_location():
    g = geocoder.ip('me')
    if g.latlng:
        latitude, longitude = g.latlng
        return latitude, longitude
    else:
        return None, None
    

def reverse_geocode(latitude, longitude):
    g = geocoder.osm([latitude, longitude], method='reverse')
    if g.ok:
        return g.address
    else:
        return None

def get_route_geometry(st_lat, st_lng, dest_lat, dest_lng):
    url = f"http://router.project-osrm.org/route/v1/walking/{st_lng},{st_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
    response = requests.get(url)
    data = response.json()
    if data["code"] == "Ok":
        geometry = data["routes"][0]["geometry"]
        decoded_points = decode(geometry)
        return decoded_points
    else:
        return []

def search_location(name):
    best_match = process.extractOne(name, bicis['address'], scorer=fuzz.ratio)
    if best_match is not None:
        closest_name = best_match[0]
        closest_row = bicis[bicis['address'] == closest_name].iloc[0]
        name, lat, long = closest_row['address'], closest_row['Latitude'], closest_row['Longitude']
        return name, lat, long
    else: 
        return None




def mapita():
    st.title("Valenbisi Fast tracker")
    bicis_full = bicis.loc[(bicis['available'] >= 15), ('address', 'open', 'ticket', 'total', 'available', 'Latitude', 'Longitude')]
    bicis_full = bicis_full.sort_values('available', ascending = False).reset_index(drop = True)
    permit = st.checkbox("Check to display selector")
    if permit:
        selected_location = st.selectbox('Select a station', bicis_full['address'])
    show_map = True
    f = st.checkbox("Find me")
    if f and show_map:
        loc = get_geolocation()
        latc = loc['coords']['latitude']
        longc = loc['coords']['longitude']
        m = reverse_geocode(latc, longc)
        st.write(f"Your location is: {m}")
        x, y = get_graph()
        map = folium.Map()
        plugins.LocateControl(strings={"title": "See your current location", "popup": "Your position"}).add_to(map)

        folium.GeoJson(y).add_to(map)

        for _, row in bicis.iterrows():
            tooltip_txt = f"""
            <span style="font-weight:bold;">Dirección:</span> {row['address']}<br>
            <span style="font-weight:bold;">Total:</span> {row['total']}<br>
            <span style="font-weight:bold;">Disponibles:</span> {row['available']}
            """
            icon_color = get_icon_color(row['available'])
            if row['available'] > 0:
               folium.Marker(
                   location=[row['Latitude'], row['Longitude']],
                   tooltip=tooltip_txt,
                   fill_color = "red",
                   icon=folium.Icon(color=icon_color, icon_color='#FFFF00')
               ).add_to(map)
            map.fit_bounds([oeste, este])

        if selected_location:
            map3 = folium.Map()
            selected_lat = bicis_full.loc[bicis_full['address'] == selected_location, 'Latitude']
            selected_long = bicis.loc[bicis['address'] == selected_location, 'Longitude']
            localizacion = bicis_full.loc[bicis_full['address'] == selected_location, ('address', 'open', 'total', 'available')].reset_index(drop = True)
            st.subheader("Estacion")
            st.dataframe(localizacion)
            icon_color = get_icon_color(localizacion['available'].item())
            folium.Marker(
                location=[selected_lat, selected_long],
                popup=selected_location,
                icon=folium.Icon(color=icon_color)
                ).add_to(map3)
            map3.fit_bounds([oeste, este])

            
        if f:
            folium.Marker(
                location = [latc, longc],
                tooltip = "There's you!",
                icon = folium.Icon(color = "black", icon_color = '#FFFFFF')
            ).add_to(map)
        if f and selected_location:
            folium.Marker(
                location = [latc, longc],
                tooltip = "There's you!",
                icon = folium.Icon(color = "black", icon_color = '#FFFFFF')
            ).add_to(map3)
            route_geometry = get_route_geometry(latc, longc, selected_lat, selected_long)
            gh = []
            for i,n in route_geometry:
                gh.append([n,i])
            linea = folium.PolyLine([gh], color = 'blue', weight = 3)
            linea.add_to(map3)

    if selected_location and f:
        folium_static(map3)
    else:
        folium_static(map)


        

        


        
        
        
       
        

    

mapita()





