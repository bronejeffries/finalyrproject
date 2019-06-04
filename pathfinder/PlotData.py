from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, GMapOptions
from bokeh.plotting import gmap
from .model import CrimeScene
from bokeh.io import output_file, output_notebook, show, save
from bokeh.models import (
    GMapPlot, GMapOptions, ColumnDataSource, Circle, LogColorMapper, BasicTicker, ColorBar,
    Range1d, PanTool, WheelZoomTool, BoxSelectTool
)
from bokeh.models.mappers import ColorMapper, LinearColorMapper
from bokeh.palettes import Viridis5
import os
from datetime import datetime as dt


def get_co_ordinates():
    crimes_scenes = []
    year_mask = '%Y'
    year = dt.strftime(dt.today(), year_mask)
    for crime_scene in CrimeScene.query.all():
        if dt.strftime(crime_scene.date_posted, year_mask) == year:
            crimes_scenes.append(crime_scene)
    longitudes = [crimescene.longitude for crimescene in crimes_scenes]
    latitudes = [crimescene.latitude for crimescene in crimes_scenes]
    colors = [crimescene.scene.category_color for crimescene in crimes_scenes]
    return latitudes, longitudes, colors


def showmap():
    tools = "pan,wheel_zoom,box_zoom,reset,save,hover,zoom_in,box_edit,poly_draw"
    # tools = " box_edit, box_select, box_zoom, click, crosshair, help, hover, lasso_select, pan, point_draw, poly_draw, poly_edit, poly_select, previewsave, redo, reset, save, tap, undo, wheel_zoom, xbox_select, xbox_zoom, xpan, xwheel_pan, xwheel_zoom, xzoom_in, xzoom_out, ybox_select, ybox_zoom, ypan, ywheel_pan, ywheel_zoom, yzoom_in, yzoom_out, zoom_in"
    map_options = GMapOptions(
        lat=0.3476, lng=32.5825, map_type="roadmap", zoom=13)
    GOOGLE_API_KEY = "AIzaSyAFCR-n7VxtftzPKR4gCje1T-cAxQXn7S8"
    plot = gmap(GOOGLE_API_KEY, map_options, tools=tools,
                title="Crimes visualizing center", height=700, width=1100)
    latitude_list, longitude_list, colors_list = get_co_ordinates()
    source = ColumnDataSource(
        data=dict(
            lat=latitude_list,
            lon=longitude_list,
            color=colors_list
        )
    )
    plot.circle(x="lon", y="lat", size=15, fill_color="color",
                fill_alpha=0.8, source=source)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    storage_path = os.path.join(BASE_DIR, 'pathfinder/templates/pages')
    map_path = os.path.join(storage_path, 'gmap_plot.html')
    output_file(map_path)
    print("saved...")
    save(plot)
