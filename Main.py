
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
    <span style="font-weight:bold;">Real Time information on FGV and Valenbisi Stations</span>
    """

st.write(f, unsafe_allow_html=True)
st.write("__________________________________________________________________________________")
c1, c2 = st.columns(2)
f = f"""
    <span style="fomt-weight:bold;">Check info on FGV Stations at</span><br>
    <span> FGV Tracker</span>
    """
c = f"""
    <span style="fomt-weight:bold;">Check info on Valenbisi  at</span><br>
    <span> Valenbisi Tracker</span>
    """
f = st.write(f)
c1.text(f)
c = st.write(c)
c1.text(c)
