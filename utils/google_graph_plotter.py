import os
import sys
import math
import csv

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Category10
from bokeh.models import ColumnDataSource, WMTSTileSource

# Allow running this file directly (python utils/google_graph_plotter.py)
# as well as via the module (python -m utils.google_graph_plotter)
if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.google_graph_writer import find_loc, get_data, get_routes
else:
    from utils.google_graph_writer import find_loc, get_data, get_routes

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUTPUT_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google_graph_plotter.html')
_DETAILED_GRAPH = os.path.join(_BASE_DIR, 'test_graphs', 'google_graph_detailed.txt')


def to_mercator(lat, lng):
    '''Convert lat/lng degrees to Web Mercator metres (used by tile maps).'''
    x = lng * 20037508.34 / 180.0
    y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0) * 20037508.34 / 180.0
    return x, y


def get_routes_from_cache(filename=_DETAILED_GRAPH):
    '''Load the graph edges from the cached Google Maps data as segments.'''

    def parse_coord(token):
        lat, lng = token.split('_')
        return float(lat), float(lng)

    segments = []
    with open(filename) as f:
        reader = csv.reader(f)
        for line in reader:
            if len(line) < 3:
                continue
            segments.append((parse_coord(line[0]), parse_coord(line[1])))
    return segments


def plot_google_graph(start, end, API='', directions_link="https://maps.googleapis.com/maps/api/directions/json?", zoom=12, map_type='roadmap'):
    # ---- Gather the coordinates to plot -------------------------------
    marker_points = None   # (start_latlng, end_latlng) when known
    if API:
        # Live mode: fetch routes from the Google Maps API (requires a valid key)
        try:
            start_loc = find_loc(start, API)
            end_loc = find_loc(end, API)
            data = get_data(start_loc, end_loc, API=API, directions_link=directions_link, alternatives='true')
            all_coords = get_routes(data)  # list of routes, each a list of (lat, lng)
            marker_points = (start_loc, end_loc)
            print(f'Plotting {len(all_coords)} live routes from the Google Maps API.')
        except Exception as err:
            print(f'Warning: could not fetch data from Google Maps ({err})')
            print('Falling back to the cached graph in test_graphs/google_graph_detailed.txt')
            API = ''
    if not API:
        # Offline mode: plot the cached graph - no API key needed
        segments = get_routes_from_cache()
        all_coords = [[a, b] for a, b in segments]
        marker_points = (segments[0][0], segments[-1][1])
        print(f'Plotting {len(all_coords)} cached road segments (no API key required).')

    # ---- Convert to Web Mercator --------------------------------------
    all_x = []
    all_y = []
    for coords in all_coords:
        xs = []
        ys = []
        for lat, lng in coords:
            x, y = to_mercator(lat, lng)
            xs.append(x)
            ys.append(y)
        all_x.append(xs)
        all_y.append(ys)

    # ---- Plot on a real (free) tile map --------------------------------
    x_min = min(min(xs) for xs in all_x)
    x_max = max(max(xs) for xs in all_x)
    y_min = min(min(ys) for ys in all_y)
    y_max = max(max(ys) for ys in all_y)
    pad_x = (x_max - x_min) * 0.1 or 500
    pad_y = (y_max - y_min) * 0.1 or 500

    bokeh_width, bokeh_height = 900, 800

    p = figure(
        title='BetterGoogleMaps - Routes on a real map',
        x_axis_type='mercator',
        y_axis_type='mercator',
        x_range=(x_min - pad_x, x_max + pad_x),
        y_range=(y_min - pad_y, y_max + pad_y),
        width=bokeh_width,
        height=bokeh_height,
        tools='pan,wheel_zoom,box_zoom,reset,save',
    )
    p.add_tile(WMTSTileSource(url='https://basemaps.cartocdn.com/light_all/{Z}/{X}/{Y}@2x.png',
                              attribution='&copy; OpenStreetMap contributors, &copy; CARTO'))

    # Cycle colours so any number of routes/segments renders correctly
    show_legend = len(all_x) <= 10
    for i in range(len(all_x)):
        source = ColumnDataSource({'x': all_x[i], 'y': all_y[i]})
        line_kwargs = {'line_width': 3, 'alpha': 0.8, 'color': Category10[10][i % 10]}
        if show_legend:
            line_kwargs['legend_label'] = f'Route {i + 1}'
        p.line('x', 'y', source=source, **line_kwargs)

    if marker_points is not None:
        m_start = to_mercator(*marker_points[0])
        m_end = to_mercator(*marker_points[1])
        p.scatter([m_start[0]], [m_start[1]], size=12, color='green', legend_label='Start')
        p.scatter([m_end[0]], [m_end[1]], size=12, color='red', legend_label='End')

    if p.legend:
        p.legend.location = 'top_right'
        p.legend.click_policy = 'hide'

    # Save to google_graph_plotter.html (self-contained - works offline) and open it
    output_file(_OUTPUT_HTML, title='BetterGoogleMaps - Route Map', mode='inline')
    show(p)

    print('')
    print('=' * 60)
    print('MAP SAVED & OPENED IN BROWSER')
    print(f'  File: {_OUTPUT_HTML}')
    print(f'  Plotted: {len(all_x)} route segments on a real map (no API key)')
    print('  If the browser shows an old Google error, do a hard')
    print('  refresh: Cmd+Shift+R  (it is showing a cached old page)')
    print('=' * 60)
    return p


if __name__ == '__main__':
    plot_google_graph('Four Seasons Hotel, Mumbai', 'Dhirubhai Ambani International School, Mumbai')
