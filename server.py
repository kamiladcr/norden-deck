from flask import Flask
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk
from shapely import wkb


MY_DATA = "data/nordic_1km_reproj.parquet"  # nordic grid
df = pd.read_parquet(MY_DATA)
df["geometry"] = df["geometry"].apply(lambda wkb_data: wkb.loads(wkb_data))
gdf = gpd.GeoDataFrame(df, geometry="geometry")
gdf["lng"] = gdf["geometry"].x
gdf["lat"] = gdf["geometry"].y
gdf["population"] = gdf["jan17"]
df = gdf.sort_values("population", ascending=False)
df = df[["lat", "lng", "population"]]
df = df[df["population"] != 0]


layer = pdk.Layer(
    "ColumnLayer",
    df,
    get_position=["lng", "lat"],
    get_fill_color=["population / 10", "population / 10", 0, 240],  # yellow
    get_elevation="population",
    get_elevation_weight="population",
    auto_highlight=True,
    radius=500,
    elevation_scale=6,
    pickable=True,
    # elevation_range=[0, 1000],
    extruded=True,
    coverage=1,
)

tooltip = {
    "html": "Population: <b>{population}</b>",
    "style": {
        "background": "grey",
        "color": "white",
        "font-family": '"Helvetica Neue", Arial',
    },
}

view_state = pdk.ViewState(
    longitude=10.7,
    latitude=59.9,
    zoom=6,
    min_zoom=4,
    max_zoom=15,
    pitch=40.5,
    bearing=0,
)


# render
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)


app = Flask(__name__)


df = pd.DataFrame(
    {
        "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
        "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
        "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
    }
)

fig = px.scatter(x=range(10), y=range(10))


@app.route("/")
def index():
    return """
    <a href="/plotly">Plotly example</a><br>
    <a href="/kepler">KeplerGl example</a><br>
    <a href="/deckgl">DeckGl example</a>
    """


@app.route("/plotly")
def plotly():
    return fig.to_html()


@app.route("/deckgl")
def deckgl():
    html = r.to_html(
        notebook_display=True,
        iframe_height=1000,
    )
    return getattr(html, "data", "")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=True, debug=True)
