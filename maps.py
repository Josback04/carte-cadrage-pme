import pandas as pd
import folium
import numpy as np
import openpyxl
# --- Étape 1: Lire les données à partir du fichier CSV fourni ---
file_path = '/Users/josback/Downloads/only_name_column.xlsx'
df_from_file = pd.read_excel(file_path)

# Nettoyer les noms de colonnes pour enlever les espaces ou sauts de ligne
df_from_file.columns = df_from_file.columns.str.strip()

# Sélectionner et renommer les colonnes pertinentes pour la suite
df_points = df_from_file[['Nom de l’entreprise', 'Commune']].copy()
df_points.rename(columns={'Nom de l’entreprise': 'Nom'}, inplace=True)


# --- Étape 2: Préparer les données de cartographie (Districts et Coordonnées) ---
district_mapping_data = [
    {'District': 'Funa', 'Commune': 'Bandal'}, {'District': 'Lukunga', 'Commune': 'Barumbu'},
    {'District': 'Funa', 'Commune': 'Bumbu'}, {'District': 'Lukunga', 'Commune': 'Gombe'},
    {'District': 'Funa', 'Commune': 'Kalamu'}, {'District': 'Funa', 'Commune': 'Kasa-vubu'},
    {'District': 'Tshangu', 'Commune': 'Kimbanseke'}, {'District': 'Lukunga', 'Commune': 'Kinshasa'},
    {'District': 'Lukunga', 'Commune': 'Kintambo'}, {'District': 'Mont Amba', 'Commune': 'Lemba'},
    {'District': 'Mont Amba', 'Commune': 'Limete'}, {'District': 'Lukunga', 'Commune': 'Lingwala'},
    {'District': 'Tshangu', 'Commune': 'Maluku'}, {'District': 'Tshangu', 'Commune': 'Masina'},
    {'District': 'Mont Amba', 'Commune': 'Matete'}, {'District': 'Tshangu', 'Commune': "Ndjili"},
    {'District': 'Tshangu', 'Commune': "Nsele"}, {'District': 'Mont Amba', 'Commune': 'Ngaba'},
    {'District': 'Lukunga', 'Commune': 'Ngaliema'}, {'District': 'Funa', 'Commune': 'Ngiri-ngiri'},
    {'District': 'Funa', 'Commune': 'Selembao'}, {'District': 'Mont Amba', 'Commune': 'Mont Ngafula'}
]
commune_to_district = {item['Commune']: item['District'] for item in district_mapping_data}

coords = {
    'Kinshasa': (-4.313837, 15.317140), 'Limete': (-4.3497, 15.3381),
    'Mont Ngafula': (-4.4269, 15.2914), 'Lemba': (-4.4239, 15.3344),
    'Kintambo': (-4.3269, 15.2728), "Nsele": (-4.3744, 15.4947),
    'Gombe': (-4.303056, 15.303333), 
    'Kasa-vubu': (-4.3425, 15.3053), # Alias pour 'Kasa-vubu' avec un 'v' minuscule
    'Kimbanseke': (-4.4223, 15.3713), 'Masina': (-4.3881, 15.3936),
    'Lingwala': (-4.3261, 15.3017), 'Ngiri-ngiri': (-4.3603, 15.2986),
    'Bandal': (-4.3486, 15.2797), 'Selembao': (-4.3733, 15.2856),
    'Bumbu': (-4.3756, 15.2975), 'Barumbu': (-4.3094, 15.3214),
    "Ndjili": (-4.4050, 15.3736), 'Kalamu': (-4.3475, 15.3200),
    'Matete': (-4.3911, 15.3533), 'Ngaliema': (-4.3617, 15.2183),
    'Maluku': (-4.4614, 16.0786), 'Ngaba': (-4.3844, 15.3242)
}

# Nettoyer la colonne 'Commune' du fichier et faire correspondre les données
df_points['Commune'] = df_points['Commune'].str.strip()
df_points['District'] = df_points['Commune'].map(commune_to_district)
df_points['Latitude'] = df_points['Commune'].map(lambda x: coords.get(x, (0, 0))[0])
df_points['Longitude'] = df_points['Commune'].map(lambda x: coords.get(x, (0, 0))[1])

# Retirer les points sans nom, district ou coordonnées valides
df_points.dropna(subset=['Nom','Commune','District', 'Latitude'], inplace=True)
df_points = df_points[df_points['Latitude'] != 0]

# Appliquer une dispersion aléatoire (Jittering) pour éviter la superposition
jitter_amount = 0.006
num_points = len(df_points)
df_points['Latitude'] += np.random.uniform(-jitter_amount, jitter_amount, num_points)
df_points['Longitude'] += np.random.uniform(-jitter_amount, jitter_amount, num_points)

# Couleurs pour chaque district
district_colors = {'Lukunga': 'blue', 'Mont Amba': 'green', 'Tshangu': 'red', 'Funa': 'purple'}


# --- Étape 3: Création de la carte et de la légende ---
m = folium.Map(location=[-4.35, 15.35], zoom_start=11, tiles='OpenStreetMap')

# Placer un point pour chaque établissement
for _, row in df_points.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        color=district_colors.get(row['District']),
        fill=True,
        fill_color=district_colors.get(row['District']),
        fill_opacity=0.8,
        popup=folium.Popup(f"<b>{row['Nom']}</b><br>{row['Commune']}", max_width=250)
    ).add_to(m)

# Calculer les statistiques pour la légende à partir des données du fichier
district_point_counts = df_points['District'].value_counts()
commune_point_counts = df_points['Commune'].value_counts().reset_index()
commune_point_counts.columns = ['Commune', 'Total']
commune_point_counts = commune_point_counts.sort_values('Total', ascending=False)

# Construire le HTML de la légende
legend_html = f'''
<div style="
    position: fixed; bottom: 20px; left: 10px; width: 220px; max-height: 40vh;
    overflow-y: auto; background-color: white; border:2px solid grey;
    z-index:9999; padding: 10px; font-family: Arial, sans-serif; font-size: 12px;
">
<b style="font-size: 14px;">LÉGENDE ET STATISTIQUES</b><br><br>
<b>Points par District (Total: {len(district_point_counts)})</b><br>
'''
for district, count in district_point_counts.items():
    color = district_colors.get(district, 'black')
    legend_html += f'<i style="background:{color}; border-radius:50%; width:12px; height:12px; display:inline-block; margin-right:6px;"></i>{district}: {count}<br>'

legend_html += '<br><b>Entreprises par Commune</b><br>'
for _, row in commune_point_counts.iterrows():
    legend_html += f'📍 {row["Commune"]}: {row["Total"]}<br>'
legend_html += '</div>'
m.get_root().html.add_child(folium.Element(legend_html))


# --- Étape 4: Sauvegarde du fichier ---
m.save('index.html')