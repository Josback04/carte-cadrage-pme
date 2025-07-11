import folium
import pandas as pd

# Données des communes et districts de Kinshasa
data = [
    {'District': 'Funa', 'Commune': 'Bandalungwa', 'Total': 13},
    {'District': 'Lukunga', 'Commune': 'Barumbu', 'Total': 13},
    {'District': 'Funa', 'Commune': 'Bumbu', 'Total': 3},
    {'District': 'Lukunga', 'Commune': 'Gombe', 'Total': 61},
    {'District': 'Funa', 'Commune': 'Kalamu', 'Total': 16},
    {'District': 'Funa', 'Commune': 'Kasa-Vubu', 'Total': 21},
    {'District': 'Tshangu', 'Commune': 'Kimbanseke', 'Total': 7},
    {'District': 'Lukunga', 'Commune': 'Kinshasa', 'Total': 15},
    {'District': 'Lukunga', 'Commune': 'Kintambo', 'Total': 31},
    {'District': 'Mont Amba', 'Commune': 'Lemba', 'Total': 46},
    {'District': 'Mont Amba', 'Commune': 'Limete', 'Total': 54},
    {'District': 'Lukunga', 'Commune': 'Lingwala', 'Total': 15},
    {'District': 'Tshangu', 'Commune': 'Maluku', 'Total': 3},
    {'District': 'Tshangu', 'Commune': 'Masina', 'Total': 8},
    {'District': 'Mont Amba', 'Commune': 'Matete', 'Total': 6},
    {'District': 'Tshangu', 'Commune': "N'djili", 'Total': 9},
    {'District': 'Tshangu', 'Commune': "N'sele", 'Total': 10},
    {'District': 'Mont Amba', 'Commune': 'Ngaba', 'Total': 2},
    {'District': 'Lukunga', 'Commune': 'Ngaliema', 'Total': 54},
    {'District': 'Funa', 'Commune': 'Ngiri-Ngiri', 'Total': 6},
    {'District': 'Funa', 'Commune': 'Selembao', 'Total': 7}
]

# Coordonnées géographiques des communes
coords = {
    'Kinshasa': (-4.313837, 15.317140), 'Limete': (-4.3497, 15.3381),
    'Mont Ngafula': (-4.4269, 15.2914), 'Lemba': (-4.4239, 15.3344),
    'Kintambo': (-4.3269, 15.2728), "N'sele": (-4.3744, 15.4947),
    'Gombe': (-4.303056, 15.303333), 'Kasa-Vubu': (-4.3425, 15.3053),
    'Kimbanseke': (-4.4223, 15.3713), 'Masina': (-4.3881, 15.3936),
    'Lingwala': (-4.3261, 15.3017), 'Ngiri-Ngiri': (-4.3603, 15.2986),
    'Bandalungwa': (-4.3486, 15.2797), 'Selembao': (-4.3733, 15.2856),
    'Bumbu': (-4.3756, 15.2975), 'Barumbu': (-4.3094, 15.3214),
    "N'djili": (-4.4050, 15.3736), 'Kalamu': (-4.3475, 15.3200),
    'Matete': (-4.3911, 15.3533), 'Ngaliema': (-4.3617, 15.2183),
    'Maluku': (-4.4614, 16.0786), 'Ngaba': (-4.3844, 15.3242)
}

df = pd.DataFrame(data)
df['Latitude'] = df['Commune'].map(lambda x: coords.get(x, (0, 0))[0])
df['Longitude'] = df['Commune'].map(lambda x: coords.get(x, (0, 0))[1])

# Couleurs pour chaque district
district_colors = {
    'Lukunga': 'blue',
    'Mont Amba': 'green',
    'Tshangu': 'red',
    'Funa': 'purple'
}

# --- Création de la carte ---
m = folium.Map(location=[-4.35, 15.35], zoom_start=11, tiles='OpenStreetMap')

# Calcul du centre et total (somme) par district pour les cercles sur la carte
district_summary = df.groupby('District').agg({
    'Latitude': 'mean',
    'Longitude': 'mean',
    'Total': 'sum'
}).reset_index()

# AJOUT 1 : Afficher les grands cercles transparents pour les districts
# for _, row in district_summary.iterrows():
#     folium.Circle(
#         location=[row['Latitude'], row['Longitude']],
#         radius=row['Total'] * 50,
#         color=district_colors.get(row['District']),
#         fill=True,
#         fill_color=district_colors.get(row['District']),
#         fill_opacity=0.3, # Opacité réduite pour bien voir les points
#         popup=f"District {row['District']} (Total général: {row['Total']})"
#     ).add_to(m)

# AJOUT 2 : Placer un point spécifique pour chaque commune
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5, # Taille du point de la commune
        color=district_colors.get(row['District']),
        fill=True,
        fill_color=district_colors.get(row['District']),
        fill_opacity=0.9,
        # Le popup affiche le nom et le total de la commune
        popup=folium.Popup(f"<b>{row['Commune']}</b><br>Total: {row['Total']}", max_width=150)
    ).add_to(m)

# --- LÉGENDE (inchangée) ---
total_unique_districts = df['District'].nunique()
district_commune_counts = df['District'].value_counts()
top_communes = df.sort_values('Total', ascending=False)

# On ajoute max-height et overflow-y pour la compatibilité mobile
legend_html = f'''
<div style="
    position: fixed; 
    bottom: 20px; 
    left: 10px; 
    width: 200px; 
    max-height: 35vh; /* Hauteur max = 40% de l'écran */
    overflow-y: auto;  /* Ajoute une scrollbar si nécessaire */
    background-color: white; 
    border:2px solid grey; 
    z-index:9999; 
    padding: 10px;
    font-family: Arial, sans-serif;
    font-size: 12px;
">
<b style="font-size: 14px;">LÉGENDE ET STATISTIQUES</b><br><br>
<b>Districts (Total: {total_unique_districts})</b><br>
'''
for district, count in district_commune_counts.items():
    color = district_colors.get(district, 'black')
    legend_html += f'<i style="background:{color}; border-radius:50%; width:12px; height:12px; display:inline-block; margin-right:6px;"></i>{district}: {count}<br>'

legend_html += '<br><b>Communes les plus présentes</b><br>'

# Boucle sur TOUTES les communes triées
for _, row in top_communes.iterrows():
    # &#128205; est le code HTML pour l'émoji 📍, mais sur votre image c'est ❤️
    # On utilise donc &#10084; pour le coeur rouge.
    legend_html += f'<span style="color:red; margin-right: 3px;">&#128205;</span> {row["Commune"]}: {row["Total"]}<br>'

legend_html += '</div>'

# 3. Ajouter la légende à la carte
m.get_root().html.add_child(folium.Element(legend_html))

# --- Sauvegarde de la carte ---
m.save('index.html')
print("Carte sauvegardée sous 'index.html'")
