from flask import Flask
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk
from shapely import wkb


DATA = "data/nordic_points.geoparquet"  # nordic grid

df = pd.read_parquet(DATA)
df["geometry"] = df["geometry"].apply(wkb.loads)
df = gpd.GeoDataFrame(df, geometry="geometry")
df["lng"] = df["geometry"].x
df["lat"] = df["geometry"].y
df = df[
    [
        "lat",
        "lng",
        "population2017",
        "population2022",
        "municipality_name",
        "population_total",
    ]
]
df["population"] = df["population2022"]
df = df[df["population"] != 0].sort_values("population", ascending=False)
df = df[
    [
        "lat",
        "lng",
        "population",
        "municipality_name",
        # "population_total",
    ]
]


def assign_color(population):
    if population < 5:
        return [225, 237, 255, 255]  # #E1EDFF
    elif population < 15:
        return [211, 225, 255, 255]  # #D3E1FF
    elif population < 50:
        return [198, 212, 254, 255]  # #C6D4FE
    elif population < 100:
        return [185, 198, 252, 255]  # #B9C6FC
    elif population < 200:
        return [173, 182, 250, 255]  # #ADB6FA
    elif population < 1000:
        return [161, 165, 248, 255]  # #A1A5F8
    elif population < 4000:
        return [132, 139, 210, 255]  # #848BD2
    elif population < 6000:
        return [105, 112, 172, 255]  # #6970AC
    elif population < 10000:
        return [78, 86, 131, 255]  # #4E5683
    else:
        return [52, 59, 90, 255]  # #343B5A


df["fill_color"] = df["population"].apply(assign_color)

layer = pdk.Layer(
    "ColumnLayer",
    df,
    get_position=["lng", "lat"],
    get_fill_color="fill_color",
    get_elevation="population",
    get_elevation_weight="population",
    auto_highlight=True,
    radius=500,
    elevation_scale=6,
    pickable=True,
    extruded=True,
    coverage=1,
)

tooltip = {
    "html": "{population} <br><b>{municipality_name}</b>",
    "style": {
        "background": "white",
        "color": "black",
        "font-family": '"Helvetica Neue", Arial',
        "font-size": "10px",
    },
}

view_state = pdk.ViewState(
    longitude=10.7,
    latitude=59.9,
    zoom=6,
    min_zoom=4,
    max_zoom=15,
    pitch=50.5,
    bearing=0,
)


# render
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style=pdk.map_styles.LIGHT,
)


app = Flask(__name__)


@app.route("/")
def deckgl():
    html = r.to_html(
        notebook_display=True,
        iframe_height=1000,
    )
    return getattr(html, "data", "")


if __name__ == "__main__":
    html = r.to_html(
        notebook_display=False,
        as_string=True,
        offline=True,
    )

    with open("index.html", "w") as h:
        h.write(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=True, debug=True)
