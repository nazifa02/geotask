"""Main module."""

import ipyleaflet
from ipyleaflet import Map, basemaps, Marker, Polyline, TileLayer
import ipywidgets as widgets

class Map(ipyleaflet.Map):
    """This is the map class that inherits from ipyleaflet.Map.

    Args:
        ipyleaflet (Map): The ipyleaflet.Map class.
    """    

    def __init__(self, center=[20, 0], zoom=2, **kwargs):
        """Initialize the map.

        Args:
            center (list, optional): Set the center of the map. Defaults to [20, 0].
            zoom (int, optional): Set the zoom level of the map. Defaults to 2.
        """        

        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True

        if "add_layer_control" not in kwargs:
            layer_control_flag = True

        else:
            layer_control_flag = kwargs["add_layer_control"]
        kwargs.pop("add_layer_control", None)


        super().__init__(center=center, zoom=zoom, **kwargs)
        if layer_control_flag:
            self.add_layers_control()


    def add_tile_layer(self, url, name, **kwargs):
        layer = ipyleaflet.TileLayer(url=url, name=name, **kwargs)
        self.add(layer)   

    def add_basemap(self, name):
        """
        Adds a basemap to the current map.

        Args:
            name (str or object): The name of the basemap as a string, or an object representing the basemap.

        Raises:
            TypeError: If the name is neither a string nor an object representing a basemap.

        Returns:
            None
        """       
        if isinstance(name, str):
            url = eval(f"basemaps.{name}").build_url()
            self.add_tile_layer(url, name) 
        else:
            self.add(name)

    def add_layers_control(self, position="topright"):
        """Adds a layers control to the map.

        Args:
            position (str, optional): The position of the layers control. Defaults to "topright".
        """
        self.add_control(ipyleaflet.LayersControl(position=position))


    def add_geojson(self, data, name="geojson", **kwargs):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str | dict): The GeoJSON data as a string, a dictionary, or a URL.
            name (str, optional): The name of the layer. Defaults to "geojson".
        """
        import json
        import requests

        # If the input is a string, check if it's a file path or URL
        
        if isinstance(data, str):
            if data.startswith('http://') or data.startswith('https://'):
            # It's a URL, so we fetch the GeoJSON
                response = requests.get(data)
                response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
                data = response.json()
            else:
                # It's a file path
                with open(data, 'r') as f:
                    data = json.load(f)


        if "style" not in kwargs:
            kwargs["style"] = {"color": "black", "weight": 1, "fillOpacity": 0}

        if "hover_style" not in kwargs:
            kwargs["hover_style"] = {"fillColor": "#542974", "fillOpacity": 0.7}

        layer = ipyleaflet.GeoJSON(data=data, name=name, **kwargs)
        self.add(layer)


    def add_shp(self, data, name="shp", **kwargs):
        """
        Adds a shapefile to the current map.

        Args:
            data (str or dict): The path to the shapefile as a string, or a dictionary representing the shapefile.
            name (str, optional): The name of the layer. Defaults to "shp".
            **kwargs: Arbitrary keyword arguments.

        Raises:
            TypeError: If the data is neither a string nor a dictionary representing a shapefile.

        Returns:
            None
        """
        import shapefile
        import json

        if isinstance(data, str):
            with shapefile.Reader(data) as shp:
                data = shp.__geo_interface__

        self.add_geojson(data, name, **kwargs)

    

        import geopandas as gpd
        from ipyleaflet import GeoData
        from shapely.geometry import Point, LineString

    def add_vector(self, data):
        """
        Add vector data to the map.

        Args:
            data (str or geopandas.GeoDataFrame): The vector data to add. This can be a file path or a GeoDataFrame.
        """
        import geopandas as gpd
        from ipyleaflet import GeoData

        if isinstance(data, gpd.GeoDataFrame):
            vector_layer = GeoData(geo_dataframe=data)
            
        elif isinstance(data, str):
            vector_layer = GeoData(geo_dataframe=gpd.read_file(data))
            
        else:
            raise ValueError("Unsupported data format. Please provide a GeoDataFrame or a file path.")

        self.add_layer(vector_layer)



    def add_image(self, url, bounds, name="image", **kwargs):
        """
        Adds an image overlay to the map.

        Args:
            url (str): The URL of the image to add.
            bounds (list): The bounds of the image as a list of tuples.
            name (str, optional): The name of the image overlay. Defaults to "image".
        """
        layer = ipyleaflet.ImageOverlay(url=url, bounds=bounds, name=name, **kwargs)
        self.add(layer)


    def add_raster(self, data, name="raster", zoom_to_layer=True, **kwargs):
        """
        Adds a raster layer to the map.

        Args:
            data (str or rasterio.DatasetReader): The raster data to add. This can be a file path or a rasterio dataset.
            colormap (str, optional): The name of the colormap to use. Defaults to "inferno".
            name (str, optional): The name of the raster layer. Defaults to "raster".
            **kwargs: Arbitrary keyword arguments.
        """

        try:
            from localtileserver import TileClient, get_leaflet_tile_layer
        except ImportError:
            raise ImportError("Please install the localtileserver package.")
        
        
        client = TileClient(data)
        layer = get_leaflet_tile_layer(client, name=name, **kwargs)
        self.add(layer)

        if zoom_to_layer:
            self.center = client.center()
            self.zoom = client.default_zoom

    def add_zoom_slider(
            self, description="Zoom level:", min=0, max=24, value=10, position="topright"
    ):
        """Adds a zoom slider to the map.

        Args:
            position (str, optional): The position of the zoom slider. Defaults to "topright".
        """
        zoom_slider = widgets.IntSlider(
            description=description, min=min, max=max, value=value
        )

        control = ipyleaflet.WidgetControl(widget=zoom_slider, position=position)
        self.add(control)
        widgets.jslink((zoom_slider, "value"), (self, "zoom"))

    def add_widget(self, widget, position="topright"):
        """Adds a widget to the map.

        Args:
            widget (object): The widget to add.
            position (str, optional): The position of the widget. Defaults to "topright".
        """
        control = ipyleaflet.WidgetControl(widget=widget, position=position)
        self.add(control)