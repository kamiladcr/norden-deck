from flask import Flask, send_from_directory
import pandas as pd
import geopandas as gpd
from shapely import wkb
import ast
import json

# MUNICIPAL BORDERS LAYER
with open("data/nordic_polygons_flat.txt", "r") as file:
    content = file.read()

borders = ast.literal_eval(content.split("= ")[1])

# POPULATION GRID LAYER
DATA = "data/nordic_points.geoparquet"
df = pd.read_parquet(DATA)
df["geometry"] = df["geometry"].apply(wkb.loads)
df = gpd.GeoDataFrame(df, geometry="geometry")
df["lng"] = df["geometry"].x
df["lat"] = df["geometry"].y

df = df[
    [
        "lat",
        "lng",
        "population",
        "munname",
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

app = Flask(__name__)

@app.route("/save")
def save():
    with open("layers/polygon_layer.json", "w") as h:
        h.write(json.dumps(borders))

    with open("layers/column_layer.json", "w") as h:
        h.write(df.to_json(orient="records"))

    return "done"

    # index.html was generated with pydeck before

    # with open("index.html", "w") as h:
    #     h.write(html)

@app.route("/layers/<path:name>")
def serve_layers(name):
    return send_from_directory("layers", name)

@app.route("/")
def index():
    with open("index.html", "r") as h:
        return h.read()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=True, debug=True)
