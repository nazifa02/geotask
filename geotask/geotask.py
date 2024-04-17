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
        """Adds a raster layer to the map.

        Args:
            data (str or rasterio.DatasetReader): The raster data to add. This can be a file path or a rasterio dataset.
            colormap (str, optional): The name of the colormap to use. Defaults to "inferno".
            name (str, optional): The name of the raster layer. Defaults to "raster".
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
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

        Returns:
            None
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

        Returns:
            None
        """
        control = ipyleaflet.WidgetControl(widget=widget, position=position)
        self.add(control)


    def add_opacity_slider(
            self, layer_index=-1, description="Opacity:", position="topright"
    ):
        """Adds an opacity slider for the specified layer.

        Args:
            layer (object): The layer for which to add the opacity slider.
            description (str, optional): The description of the opacity slider. Defaults to "Opacity:".
            position (str, optional): The position of the opacity slider. Defaults to "topright".

        Returns:
            None
        """
        layer = self.layers[layer_index]
        opacity_slider = widgets.FloatSlider(
            description=description, min=0, max=1, value=layer.opacity, style={"description_width": "initial"}
        )

        def update_opacity(change):
            """
            Updates the opacity of a layer based on the new value from a slider.

            This function is designed to be used as a callback for an ipywidgets slider. 
            It takes a dictionary with a "new" key representing the new value of the slider, 
            and sets the opacity of a global layer variable to this new value.

            Args:
            change (dict): A dictionary with a "new" key representing the new value of the slider.

            Returns:
                None
            """
            layer.opacity = change["new"]
            
        opacity_slider.observe(update_opacity, "value")
        
        control = ipyleaflet.WidgetControl(widget=opacity_slider, position=position)
        self.add(control)

        from ipywidgets import Dropdown, Button, HBox

    def add_basemap_gui(self, position="topright"):
        """Adds a basemap GUI to the map.

        Args:
            position (str, optional): The position of the basemap GUI. Defaults to "topright".

        Returns:
            None
        """
        basemap_selector = widgets.Dropdown(
            options=[
                "OpenStreetMap",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "CartoDB.DarkMatter",
                "Esri.NatGeoWorldMap",
            ],
            value="OpenStreetMap",
        )

        close_button = widgets.Button(
            icon='times', 
            layout={'width': '35px'}  
        )

        def on_basemap_change(change):
            """
            Handles the event of changing the basemap on the map.

            This function is designed to be used as a callback for an ipywidgets dropdown. 
            It takes a dictionary with a "new" key representing the new value of the dropdown, 
            and calls the add_basemap method with this new value.

            Args:
                change (dict): A dictionary with a "new" key representing the new value of the dropdown.

            Returns:
                None
            """
            
            self.add_basemap(change['new'])


        def on_close_button_clicked(button):
            """
            Handles the event of clicking the close button on a control.

            This function is designed to be used as a callback for a button click event. 
            It takes a button instance as an argument, and calls the remove method 
            to remove a global control variable from the map.

            Args:
                button (ipywidgets.Button): The button that was clicked.

            Returns:
                None
            """
            self.remove(control)

        basemap_selector.observe(on_basemap_change, "value")
        close_button.on_click(on_close_button_clicked)

        widget_box = widgets.HBox([basemap_selector, close_button])
        control = ipyleaflet.WidgetControl(widget=widget_box, position=position)
        self.add(control)