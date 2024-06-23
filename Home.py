import streamlit as st


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

f = f"""
    <span style="font-weight:bold;">Check info on FGV Stations at</span><br>
    <span> FGV Tracker</span>
    """

c = f"""
    <span style="font-weight:bold;">Check info on Valenbisi at</span><br>
    <span> Valenbisi Tracker</span>
    """
col1, col2 = st.columns(2)
with col1:
    st.write(f, unsafe_allow_html=True)

with col2:
    st.write(c, unsafe_allow_html=True)

g = f"""
    <span style="font-weight:bold;">You can also search for a station!</span><br>
    <span> Just select Finder</span>
    """
st.write(g, unsafe_allow_html=True)
st.write("____________________________________________________________________________________")


c1, c2 = st.columns(2)
evgeny = f"""
        <span style="font-weight:bold;"> Project by Evgeny Grachev</span><br>
        <span> Special thanks to Valencia Open Data Project</span>
        """
with c1:
    st.write(evgeny, unsafe_allow_html=True)

disclaimer = f"""
            <span style="font-weight:bold;"> Disclaimer!</span><br>
            <span> This app uses your geolocation data in order to provide personalized routes</span>
            """

with c2:
    st.write(disclaimer, unsafe_allow_html=True)

