import folium
import requests
import os

# ==============================
# Coordonnées
# ==============================
VICTOIRE = (-4.3276, 15.3126)
CENTRE_VILLE = (-4.3190, 15.3070)
FICHIER = "routes_toutes_victoire_centreville.html"

# Supprimer ancienne carte
if os.path.exists(FICHIER):
    os.remove(FICHIER)

# ==============================
# OSRM Public — routes multiples
# ==============================
url = (
    f"https://router.project-osrm.org/route/v1/driving/"
    f"{VICTOIRE[1]},{VICTOIRE[0]};{CENTRE_VILLE[1]},{CENTRE_VILLE[0]}"
    "?overview=full&geometries=geojson&alternatives=true"
)

response = requests.get(url).json()

if "routes" not in response:
    print("❌ Impossible de récupérer les routes")
    exit()

routes = response["routes"]
# Trier par distance : courte → longue
routes_sorted = sorted(routes, key=lambda r: r["distance"])

# ==============================
# Création carte interactive
# ==============================
m = folium.Map(location=VICTOIRE, zoom_start=14)

# Vue terrestre
folium.TileLayer("OpenStreetMap", name="Terrestre").add_to(m)
# Vue satellite
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery",
    name="Satellite"
).add_to(m)

# ==============================
# Marqueurs départ/arrivée
# ==============================
folium.Marker(VICTOIRE, popup="Rond-Point Victoire").add_to(m)
folium.Marker(CENTRE_VILLE, popup="Centre-Ville (Gombe)").add_to(m)

# ==============================
# Tracé des routes
# ==============================
for i, route in enumerate(routes_sorted):
    coords = route["geometry"]["coordinates"]
    line = [(lat, lon) for lon, lat in coords]

    # La plus courte en rouge
    if i == 0:
        folium.PolyLine(line, color="red", weight=6, tooltip="Route la plus courte").add_to(m)
    # Autres routes en bleu
    else:
        folium.PolyLine(line, color="blue", weight=4, tooltip=f"Route alternative {i}").add_to(m)

# ==============================
# Contrôle des couches
# ==============================
folium.LayerControl(collapsed=False).add_to(m)

# ==============================
# Sauvegarde
# ==============================
m.save(FICHIER)
print("✅ Carte générée :", FICHIER)
