import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Charger les données
data = pd.read_csv('donnees_ventes_etudiants.csv')

# Convertir 'order_date' en format datetime si ce n'est pas déjà le cas
data['order_date'] = pd.to_datetime(data['order_date'])

# Dictionnaire des États complets
state_mapping = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
    "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}

# Ajouter une colonne avec les noms complets des États
data['State Complet'] = data['State'].map(state_mapping)

# Déterminer les dates minimale et maximale dans le jeu de données
min_date = data['order_date'].min().date()
max_date = data['order_date'].max().date()

# --- Panneau latéral pour les filtres ---
st.sidebar.title("Filtres")

# Filtre multi-sélection pour la région (vide par défaut)
regions = data['Region'].unique()
selected_regions = st.sidebar.multiselect("Sélectionnez la Région(s)", options=regions, default=[])

# Filtre multi-sélection pour les États (vide par défaut)
states = data['State Complet'].unique()
selected_states = st.sidebar.multiselect("Sélectionnez l'État(s)", options=states, default=[])

# Filtre multi-sélection pour les comtés (vide par défaut)
counties = data['County'].unique()
selected_counties = st.sidebar.multiselect("Sélectionnez le Comté(s)", options=counties, default=[])

# Filtre multi-sélection pour les villes (vide par défaut)
cities = data['City'].unique()
selected_cities = st.sidebar.multiselect("Sélectionnez la Ville(s)", options=cities, default=[])

# Filtre multi-sélection pour le statut (vide par défaut)
statuses = data['status'].unique()
selected_statuses = st.sidebar.multiselect("Sélectionnez le Statut(s)", options=statuses, default=[])

# Appliquer les filtres de manière conditionnelle
filtered_data = data.copy()
if selected_regions:
    filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]
if selected_states:
    filtered_data = filtered_data[filtered_data['State Complet'].isin(selected_states)]
if selected_counties:
    filtered_data = filtered_data[filtered_data['County'].isin(selected_counties)]
if selected_cities:
    filtered_data = filtered_data[filtered_data['City'].isin(selected_cities)]
if selected_statuses:
    filtered_data = filtered_data[filtered_data['status'].isin(selected_statuses)]

# --- Sélection des dates ---
# Déplacer la sélection des dates à droite de la section des KPI
st.write("## Sélectionnez la période")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date de début", min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("Date de fin", max_date, min_value=min_date, max_value=max_date)

# Filtrer les données en fonction de la plage de dates sélectionnée
filtered_data = filtered_data[(filtered_data['order_date'] >= pd.to_datetime(start_date)) & 
                              (filtered_data['order_date'] <= pd.to_datetime(end_date))]

# --- Calcul des KPI (Indicateurs Clés de Performance) ---
total_sales = filtered_data['total'].sum()
distinct_customers = filtered_data['cust_id'].nunique()
total_orders = filtered_data['order_id'].nunique()

# --- Section d'affichage des KPI sous forme de cartes ---
kpi_fig = go.Figure()

# Affichage du Total des Ventes
kpi_fig.add_trace(go.Indicator(
    mode="number+delta",
    value=total_sales,
    title={"text": "Total des Ventes"},
    domain={'x': [0, 0.3], 'y': [0, 1]}
))

# Affichage des Clients Distincts
kpi_fig.add_trace(go.Indicator(
    mode="number+delta",
    value=distinct_customers,
    title={"text": "Clients Distincts"},
    domain={'x': [0.35, 0.65], 'y': [0, 1]}
))

# Affichage des Commandes Distinctes
kpi_fig.add_trace(go.Indicator(
    mode="number+delta",
    value=total_orders,
    title={"text": "Commandes Distinctes"},
    domain={'x': [0.7, 1], 'y': [0, 1]}
))

# Mise en page des KPI en une ligne
kpi_fig.update_layout(grid={'rows': 1, 'columns': 3}, margin=dict(t=50, b=50))

# Afficher le graphique des KPI
st.plotly_chart(kpi_fig, use_container_width=True)

# --- Visualisation des Ventes par Catégorie ---
sales_by_category = filtered_data.groupby('category')['total'].sum().reset_index()
fig_bar_category = px.bar(sales_by_category, x='category', y='total', title="Total des Ventes par Catégorie")

# --- Visualisation du pourcentage des ventes par Région ---
sales_by_region = filtered_data.groupby('Region')['total'].sum().reset_index()
fig_pie_region = px.pie(sales_by_region, values='total', names='Region', title="Pourcentage des Ventes par Région")

# Affichage des graphiques par catégorie et par région
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_bar_category)
with col2:
    st.plotly_chart(fig_pie_region)

# --- Top 10 des meilleurs clients en fonction des ventes ---
top_customers = filtered_data.groupby('full_name')['total'].sum().nlargest(10).reset_index()
fig_bar_top_customers = px.bar(top_customers, x='total', y='full_name', orientation='h', 
                               title="Top 10 des Meilleurs Clients", labels={'total': 'Total des Ventes', 'full_name': 'Client'})

# Afficher le graphique du top 10 des clients
st.plotly_chart(fig_bar_top_customers)

# --- Histogramme pour la répartition de l'âge des clients ---
fig_hist_age = px.histogram(filtered_data, x='age', nbins=20, title="Répartition de l'âge des clients", labels={'age': 'Âge des clients'})

# --- Répartition par genre (hommes et femmes) ---
gender_counts = filtered_data['Gender'].value_counts(normalize=True).reset_index()
gender_counts.columns = ['Gender', 'Percentage']
gender_counts['Percentage'] = gender_counts['Percentage'] * 100  # Convertir en pourcentage
fig_bar_gender = px.bar(gender_counts, x='Gender', y='Percentage', title="Répartition par Genre (Homme/Femme)", labels={'Gender': 'Genre', 'Percentage': 'Pourcentage (%)'})

# Affichage des graphiques pour l'âge et le genre
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_hist_age)
with col2:
    st.plotly_chart(fig_bar_gender)

# --- Courbe du nombre total de ventes par Mois-Année ---
filtered_data['month_year'] = filtered_data['order_date'].dt.to_period('M')
sales_by_month_year = filtered_data.groupby('month_year')['total'].sum().reset_index()
sales_by_month_year['month_year'] = sales_by_month_year['month_year'].dt.to_timestamp()
fig_sales_by_month = px.line(sales_by_month_year, x='month_year', y='total', title="Total des Ventes par Mois-Année", labels={'month_year': 'Mois-Année', 'total': 'Total des Ventes'})

# Afficher le graphique des ventes par mois-année
st.plotly_chart(fig_sales_by_month)

# --- Carte des États avec total des ventes par État ---
# Dictionnaire des latitudes et longitudes pour les États américains
state_coords = {
    "Alabama": {"lat": 32.806671, "lon": -86.791130},
    "Alaska": {"lat": 61.370716, "lon": -152.404419},
    "Arizona": {"lat": 33.729759, "lon": -111.431221},
    "Arkansas": {"lat": 34.969704, "lon": -92.373123},
    "California": {"lat": 36.116203, "lon": -119.681564},
    "Colorado": {"lat": 39.059811, "lon": -105.311104},
    "Connecticut": {"lat": 41.597782, "lon": -72.755371},
    "District of Columbia": {"lat": 38.89511, "lon": -77.03637},
    "Delaware": {"lat": 39.318523, "lon": -75.507141},
    "Florida": {"lat": 27.766279, "lon": -81.686783},
    "Georgia": {"lat": 33.040619, "lon": -83.643074},
    "Hawaii": {"lat": 21.094318, "lon": -157.498337},
    "Idaho": {"lat": 44.240459, "lon": -114.478828},
    "Illinois": {"lat": 40.349457, "lon": -88.986137},
    "Indiana": {"lat": 39.849426, "lon": -86.258278},
    "Iowa": {"lat": 42.011539, "lon": -93.210526},
    "Kansas": {"lat": 38.526600, "lon": -96.726486},
    "Kentucky": {"lat": 37.668140, "lon": -84.670067},
    "Louisiana": {"lat": 31.169546, "lon": -91.867805},
    "Maine": {"lat": 44.693947, "lon": -69.381927},
    "Maryland": {"lat": 39.063946, "lon": -76.802101},
    "Massachusetts": {"lat": 42.230171, "lon": -71.530106},
    "Michigan": {"lat": 43.326618, "lon": -84.536095},
    "Minnesota": {"lat": 45.694454, "lon": -93.900192},
    "Mississippi": {"lat": 32.741646, "lon": -89.678696},
    "Missouri": {"lat": 38.456085, "lon": -92.288368},
    "Montana": {"lat": 46.921925, "lon": -110.454353},
    "Nebraska": {"lat": 41.125370, "lon": -98.268082},
    "Nevada": {"lat": 38.313515, "lon": -117.055374},
    "New Hampshire": {"lat": 43.452492, "lon": -71.563896},
    "New Jersey": {"lat": 40.298904, "lon": -74.521011},
    "New Mexico": {"lat": 34.840515, "lon": -106.248482},
    "New York": {"lat": 42.165726, "lon": -74.948051},
    "North Carolina": {"lat": 35.630066, "lon": -79.806419},
    "North Dakota": {"lat": 47.528912, "lon": -99.784012},
    "Ohio": {"lat": 40.388783, "lon": -82.764915},
    "Oklahoma": {"lat": 35.565342, "lon": -96.928917},
    "Oregon": {"lat": 44.572021, "lon": -122.070938},
    "Pennsylvania": {"lat": 40.590752, "lon": -77.209755},
    "Rhode Island": {"lat": 41.680893, "lon": -71.511780},
    "South Carolina": {"lat": 33.856892, "lon": -80.945007},
    "South Dakota": {"lat": 44.299782, "lon": -99.438828},
    "Tennessee": {"lat": 35.747845, "lon": -86.692345},
    "Texas": {"lat": 31.054487, "lon": -97.563461},
    "Utah": {"lat": 40.150032, "lon": -111.862434},
    "Vermont": {"lat": 44.045876, "lon": -72.710686},
    "Virginia": {"lat": 37.769337, "lon": -78.169968},
    "Washington": {"lat": 47.400902, "lon": -121.490494},
    "West Virginia": {"lat": 38.491226, "lon": -80.954456},
    "Wisconsin": {"lat": 44.268543, "lon": -89.616508},
    "Wyoming": {"lat": 42.755966, "lon": -107.302490}
}
# Ajouter les colonnes de latitude et de longitude
data['lat'] = data['State Complet'].map(lambda x: state_coords[x]['lat'])
data['lon'] = data['State Complet'].map(lambda x: state_coords[x]['lon'])

# Grouper par État pour obtenir les ventes totales et les coordonnées
sales_by_state = data.groupby('State Complet').agg({'total': 'sum', 'lat': 'first', 'lon': 'first'}).reset_index()
fig_map = px.scatter_mapbox(sales_by_state, lat="lat", lon="lon", size="total", hover_name="State Complet", 
                            hover_data={"lat": False, "lon": False, "total": True}, title="Total des Ventes par État",
                            mapbox_style="open-street-map", zoom=3, size_max=50, height=600, width=1000)

# Afficher la carte des ventes par État
st.plotly_chart(fig_map)

# --- Affichage des données filtrées ---
st.write(filtered_data)
