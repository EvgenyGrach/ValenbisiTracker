
from pages.Valenbisi_Tracker import mapita
import streamlit as st
from pages.Buscador import show_secondary_page
from pages.FGV_Tracker import show_third_page

st.set_page_config(
    page_title="FGV/Valenbisi Tracker",
    page_icon="👋"
)
st.title("FGV/Valenbisi Fast Tracker")
f = f"""
    <span style="font-weight:bold;">Real Time information FGV and Valenbisi Stations</span>
    """

st.write(f, unsafe_allow_html=True)