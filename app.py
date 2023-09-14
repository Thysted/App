# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import altair as alt
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns
import numpy as np
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2


#Load data
@st.cache_data
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/Thysted/App/main/global_sustainable_energy.csv') 
    return df
df = load_data()

df_2020 = df[df['Year'] == 2020]

st.title("Sustainability across the world")
st.sidebar.header("Specifications")

# Introduction
st.markdown(""" This dashboard tries to show a few key factors related sustainability across different countries.
The reasoning behind this overview is the UN World Goals focus on sustainability. By collecting these different variabels in one simple dashboard its posible to directly focus on different factors to improve towards a greener lifestyle.
""")

#The elements
st.markdown("""In this folder is an overview over the different posibilities on this dashboard.
""")
with st.expander("Elements guide"):
    st.markdown("""
On the left side is a sidebar which creates the posibility to select different countries and a year interval.
After this you can choose different points of interest which is as follow:
- Economic activity
- Distribution of energisources
- Access to electricity
""")

#Trying GeoDataFrame    
gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df['Longitude'], df['Latitude']))
gdf.crs = "EPSG:4326"

gdf = gdf[gdf['Year'] == 2020]
#Removing NAs
gdf = gdf.dropna(subset=['Latitude', 'Longitude'])

m = folium.Map(location = [57.046707, 9.935932], zoom_start=1, tiles = "CartoDB positron")

#Create cluster
marker_cluster = MarkerCluster().add_to(m)

#Text over data
for _, row in gdf.iterrows():
    popup_content = f"""
    Country: {row['Entity']}<br>
    GDP per Capita: {row['gdp_per_capita']}<br>
    GDP growth: {row['gdp_growth']}<br>
    Land Area : {row['Land Area(Km2)']}<br>
    Latitude  : {row['Latitude']}<br>
    Longitude  : {row['Longitude']}<br>
    """
    popup = folium.Popup(popup_content, max_width=300)
        
    folium.Circle(
        location=[row['Latitude'], row['Longitude']],
        radius=15,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.4,
        popup=popup
    ).add_to(marker_cluster)

#Map    
st_folium(m)

#Sidebar select
#Select countries
# Creating new column "continents"

continents = {
    'NA': 'North America',
    'SA': 'South America', 
    'AS': 'Asia',
    'OC': 'Australia',
    'AF': 'Africa',
    'EU': 'Europe'
}

con2 = { 'NA': 'North America',
    'SA': 'South America', 
    'AS': 'Asia',
    'OC': 'Australia',
    'AF': 'Africa',
    'EU': 'Europe', 
    'AL': 'All'}

countries = df['Entity']

df['Continent'] = [continents[country_alpha2_to_continent_code(country_name_to_country_alpha2(country))] for country in countries]

# Select continent and country
# selectbox = list and choose one, multiselect = choose many


con2 = st.sidebar.selectbox('Select Continent', options=['select']+list(df['Continent'].unique())+['All'])


if con2 == 'select':
    st.warning('You need to select a Continent')
    st.stop()

elif con2 == 'All':
    #chosen_country_AL = df['Entity']
    chosen_country = st.sidebar.multiselect('Select Country ', options=df['Entity'].unique())     

elif con2 == 'Africa':
    chosen_country_AF = df[df['Continent'] == 'Africa']
    chosen_country = st.sidebar.multiselect('Select Country ', options=chosen_country_AF.Entity.unique())
    
elif con2 == 'Asia':
    chosen_country_AS = df[df['Continent'] == 'Asia']
    chosen_country = st.sidebar.multiselect('Select Country ', options=chosen_country_AS.Entity.unique())
     
elif con2 == 'Australia':
    chosen_country_AU = df[df['Continent'] == 'Australia']
    chosen_country = st.sidebar.multiselect('Select Country ', options=chosen_country_AU.Entity.unique())

elif con2 == 'Europe':
    chosen_country_EU = df[df['Continent'] == 'Europe']
    chosen_country = st.sidebar.multiselect('Select Country ', options=chosen_country_EU.Entity.unique())

elif con2 == 'North America':
    chosen_country_NA = df[df['Continent'] == 'North America']
    chosen_country= st.sidebar.multiselect('Select Country ', options=chosen_country_NA.Entity.unique().tolist())

elif con2 == 'South America':
    chosen_country_SA = df[df['Continent'] == 'South America']
    chosen_country = st.sidebar.multiselect('Select Country ', options=chosen_country_SA.Entity.unique())



filtered_df = df[df['Entity'].isin(chosen_country)]


#Select years
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
year_range = st.sidebar.slider('Select the years', min_year, max_year, (min_year, max_year))
filtered_df = filtered_df[(filtered_df['Year'] >= year_range[0]) & (filtered_df['Year'] <= year_range[1])]
filtered_df_2020 = filtered_df[filtered_df['Year'] == 2020]

#Dropdown, used to select diffent chart categories
visualization_option = st.selectbox(
    "Select subject for charts",
    ["Economic activity",
     "Distribution of energisources",
     "Access to electricity"]
)

# Visual coding for selected categories

if visualization_option == "Economic activity":
    st.markdown("""
    This folder is showning the economic activity for the selected country/countries in the selected timeperiod.
    By implementing the two line charts the values are easy to compare 
    """)
    chart = alt.Chart(filtered_df).mark_line().encode(
        x = 'Year',
        y = alt.Y('gdp_growth', title = "GDP growth"),
        color = 'Entity:N'
    ).properties(
        title = 'GDP growth for slected countries'
    )
    st.altair_chart(chart, use_container_width = True)
    
    chart = alt.Chart(filtered_df).mark_line().encode(
        x = 'Year',
        y = alt.Y('gdp_per_capita', title = "GDP per capita (USD)"),
        color = 'Entity:N',
        tooltip = [
            alt.Tooltip('Year:T', title="Year")
        ]
    ).properties(
        title = 'GDP per capita for selected countries'
    )
    st.altair_chart(chart, use_container_width = True)
    
elif visualization_option == "Distribution of energisources":
    st.markdown(""" 
    On this page is illustrated different graph which indicate the distribution of energisorces for the selectec country/countries.
    The first three charts shows the development of energisources over time over time, while below is added a pie chart which shows the percentwise distribution. 
    """)
    chart = alt.Chart(filtered_df).mark_line().encode(
        x = 'Year',
        y = 'Electricity from fossil fuels (TWh)',
        color = 'Entity:N'
    ).properties(
        title = 'Electricity from fossil fuels (TWh)'
    )
    st.altair_chart(chart, use_container_width = True)
    
    chart = alt.Chart(filtered_df).mark_line().encode(
        x = 'Year',
        y = 'Electricity from nuclear (TWh)',
        color = 'Entity:N'
    ).properties(
        title = 'Electricity from nuclear (TWh)'
    )
    st.altair_chart(chart, use_container_width = True)

    chart = alt.Chart(filtered_df).mark_line().encode(
        x = 'Year',
        y = 'Electricity from renewables (TWh)',
        color = 'Entity:N'
    ).properties(
        title = 'Electricity from renewables (TWh)'
    )
    st.altair_chart(chart, use_container_width = True)
    st.markdown("""For the following pie chart to look at a specific country you need to only select one country. Otherwise it wil do a summation of all the seleted countires.
    At the same time its possible to change the 'Year' slider to either look at a specific year or a number of consecutive years. 
""")
    selected_columns = ['Electricity from fossil fuels (TWh)', 'Electricity from nuclear (TWh)', 'Electricity from renewables (TWh)']
    labels = selected_columns
    data = filtered_df[selected_columns].sum().values
    fig, ax = plt.subplots()
    ax.pie(data, labels = labels, autopct = '%1.2f%%', startangle = 90)
    ax.axis('equal')
    st.pyplot(fig)

elif visualization_option == "Access to electricity":
    st.markdown("""This last folder shows the different selected countries access til energi. This is done to show the relevanse of the UN World Goals(Specifictly number seven) to secure energy for the whole world.
    By including this chart it's posible to show a lot of countries isn't near 100 percent access to electricity.
""")
    chart = alt.Chart(filtered_df).mark_line().encode(
        x = 'Year',
        y = 'Access to electricity (% of population)',
        color = 'Entity:N'
    ).properties(
        title = 'Access to electricity'
    )
    st.altair_chart(chart, use_container_width = True)

# Display dataset overview
st.header("Dataset Overview")
st.markdown("""The following overview shows the distribution of the variabels for the selected countries. If multipel countries are selected it will show the distribution for all selected countries. 
""")
st.dataframe(filtered_df.describe())

