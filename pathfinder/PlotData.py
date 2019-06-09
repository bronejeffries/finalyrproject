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


def remove_blank(elem):
    if elem is not '':
        return True
    else:
        return False


def clean_co_ordinates(list_obj):
    clean_list = filter(remove_blank, list_obj)
    return [item for item in clean_list]


def get_co_ordinates(crimescenes):
    crimes_scenes = []
    if crimescenes is not None:
        crimes_scenes = crimescenes
    else:
        # create crimescenes data for the current year
        year_mask = '%Y'
        year = dt.strftime(dt.today(), year_mask)
        for crime_scene in CrimeScene.query.all():
            if dt.strftime(crime_scene.date_posted, year_mask) == year:
                crimes_scenes.append(crime_scene)
    longitudes = clean_co_ordinates(
        [crimescene.longitude for crimescene in crimes_scenes])
    latitudes = clean_co_ordinates(
        [crimescene.latitude for crimescene in crimes_scenes])
    colors = [crimescene.scene.category_color for crimescene in crimes_scenes]
    return latitudes, longitudes, colors, len(crimes_scenes)-len(latitudes)


def showmap(output_name=None, crimescenes=None):
    storage_endpoint = f"{output_name}.html" if output_name is not None else 'gmap_plot.html'
    tools = "pan,wheel_zoom,box_zoom,reset,save,hover,zoom_in,box_edit,poly_draw"
    map_options = GMapOptions(
        lat=0.3476, lng=32.5825, map_type="roadmap", zoom=13)
    GOOGLE_API_KEY = "AIzaSyAFCR-n7VxtftzPKR4gCje1T-cAxQXn7S8"
    plot = gmap(GOOGLE_API_KEY, map_options, tools=tools,
                title="Crimes visualizing center", height=700, width=1100)
    latitude_list, longitude_list, colors_list, uncategorized_count = get_co_ordinates(
        crimescenes)
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
    map_path = os.path.join(storage_path, storage_endpoint)
    output_file(map_path)
    print("saved...")
    save(plot)
    return uncategorized_count
