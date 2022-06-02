from collections import Counter

import h3
import overpy
import pandas as pd
import pydeck as pdk

api = overpy.Overpass()
iso2 = "HU"
tag_key = "amenity"
tag_value = "doctors"

r = api.query(
    f"""
    ( area["ISO3166-1"="{iso2}"][admin_level=2]; )->.searchArea;
    ( node[{tag_key}={tag_value}]( area.searchArea );
      way[{tag_key}={tag_value}]( area.searchArea );
      relation[{tag_key}={tag_value}]( area.searchArea );
    );
    out center;"""
)

print(f"We've got {len(r.nodes)} nodes, {len(r.ways)} ways, and {len(r.relations)} relations")

hexes_at_level5 = []
hexes_at_level6 = []
ll_level5 = []
for node in r.nodes:
    l5_hex = h3.geo_to_h3(node.lat, node.lon, 5)
    hexes_at_level5.append(l5_hex)
    l6_hex = h3.geo_to_h3(node.lat, node.lon, 6)
    hexes_at_level6.append(l6_hex)
    ll_level5.append(h3.h3_to_geo(l5_hex))


hexes_at_level5 = Counter(hexes_at_level5)
hexes_at_level6 = Counter(hexes_at_level6)

level5_json = []
for k,v in hexes_at_level5.items():
    t = {"hex": k,
         "count": v}
    level5_json.append(t)

level6_json = []
for k,v in hexes_at_level6.items():
    t = {"hex": k,
         "count": v}
    level6_json.append(t)

df5 = pd.DataFrame(level5_json)
df6 = pd.DataFrame(level6_json)

layer5 = pdk.Layer(
    "H3HexagonLayer",
    df5,
    pickable=True,
    stroked=True,
    filled=True,
    extruded=False,
    get_hexagon="hex",
    get_fill_color="[0, 255, count]",
    get_line_color=[255, 255, 255],
    line_width_min_pixels=2,
)

layer6 = pdk.Layer(
    "H3HexagonLayer",
    df6,
    pickable=True,
    stroked=True,
    filled=True,
    extruded=False,
    get_hexagon="hex",
    get_fill_color="[0, 255, count]",
    get_line_color=[255, 255, 255],
    line_width_min_pixels=2,
)

view_state5 = pdk.ViewState(latitude=47.497913, longitude=19.040236, zoom=7, bearing=0, pitch=30)
view_state6 = pdk.ViewState(latitude=47.497913, longitude=19.040236, zoom=7, bearing=0, pitch=30)

r5 = pdk.Deck(layers=[layer5], initial_view_state=view_state5, tooltip={"text": "Count: {count}"})
r6 = pdk.Deck(layers=[layer6], initial_view_state=view_state6, tooltip={"text": "Count: {count}"})

r5.to_html(f"hexes/{tag_key}_{tag_value}_level5.html")
r6.to_html(f"hexes/{tag_key}_{tag_value}_level6.html")

# 3D hexes
df_3d_l5 = pd.DataFrame(ll_level5, columns=["lat", "long"])
df_3d_l5.to_csv("hexes/csv/doctors_heatmap.csv", sep=",", index=False)
# HEXAGON_LAYER_DATA = "hexes/csv/doctors_heatmap.csv"
HEXAGON_LAYER_DATA = (
    "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv"  # noqa
)

layer = pdk.Layer(
    "HexagonLayer",
    HEXAGON_LAYER_DATA,
    get_position=["lng", "lat"],
    auto_highlight=True,
    elevation_scale=50,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
)

view_state = pdk.ViewState(latitude=47.497913, longitude=19.040236, zoom=7, bearing=0, pitch=30)
r = pdk.Deck(layers=[layer], initial_view_state=view_state)
r.to_html("hexes/hexagon_layer.html")



print("READY"*100)
