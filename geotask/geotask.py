"""Main module."""

import ipyleaflet
from ipyleaflet import Map, basemaps, WidgetControl, Marker, Polyline, TileLayer, GeoData, Circle
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

        self.add_toolbar()
        self.add_basemap_gui()

    def add_tile_layer(self, url, name, **kwargs):
        """
        Adds a tile layer to the current map.

        Parameters:
        url (str): The URL of the tile layer.
        name (str): The name of the tile layer.
        **kwargs: Additional keyword arguments for the TileLayer constructor.

        Returns:
        None
        """
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
        
        if isinstance(data, str):
            if data.startswith('http://') or data.startswith('https://'):
                response = requests.get(data)
                response.raise_for_status() 
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

    

    def add_basemap_gui(self, basemaps=None, position="topright"):
        """Adds a basemap GUI to the map.
    
        Args:
            position (str, optional): The position of the basemap GUI. Defaults to "topright".
        """
    
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left
    
        basemap_selector = widgets.Dropdown(
            options=[
                "OpenStreetMap",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "Esri.NatGeoWorldMap",
            ],
            description="",
            layout=widgets.Layout(width='auto')  # Set the width to auto
        )
    
        def update_basemap(change):
            """
            Updates the basemap with the new selected value.

            Parameters:
            change (dict): A dictionary containing the new value. The new basemap is expected to be in change['new'].

            Returns:
            None
            """
            self.add_basemap(change["new"])
    
        basemap_selector.observe(update_basemap, "value")
    
        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            button_style="primary",
            layout=widgets.Layout(height="28px", width="28px", padding=padding),
        )
    
        def on_close_button_clicked(change):
            """
            Handles the event when the close button is clicked. If the new value of the change is True, it removes the control.

            Parameters:
            change (dict): A dictionary containing the new value. The new state of the button is expected to be in change['new'].

            Returns:
            None
            """
            if change["new"]:
                # Remove the control when the close button is clicked
                self.remove(control)
    
        close_button.observe(on_close_button_clicked, "value")
    
        # Create a box to hold the dropdown and the close button
        box = widgets.HBox([close_button, basemap_selector])
    
        control = ipyleaflet.WidgetControl(widget=box, position=position)
        self.add(control)


    
    def add_toolbar(self, position="topright"):
        """Adds a toolbar to the map.

        Args:
            position (str, optional): The position of the toolbar. Defaults to "topright".

        """
        
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left

        toolbar_button = widgets.ToggleButton(
            value=False,
            tooltip="Toolbar",
            icon="wrench",
            layout=widgets.Layout(width="28px", height="28px", padding=padding),
        )

        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            button_style="primary",
            layout=widgets.Layout(height="28px", width="28px", padding=padding),
        )

        toolbar = widgets.VBox([toolbar_button])
        
        def close_click(change):
            """
            Handles the event when the close button is clicked. If the new value of the change is True, it closes the toolbar_button, close_button, and toolbar.

            Parameters:
            change (dict): A dictionary containing the new value. The new state of the button is expected to be in change['new'].

            Returns:
            None
            """
            if change["new"]:
                toolbar_button.close()
                close_button.close()
                toolbar.close()


        close_button.observe(close_click, "value")

        rows = 2
        cols = 2
        grid = widgets.GridspecLayout(
            rows, cols, grid_gap="0px", layout=widgets.Layout(width="65px")
        )

        icons = ["folder-open", "map", "info", "question"]

        for i in range(rows):
            for j in range(cols):
                grid[i, j] = widgets.Button(
                    description="",
                    button_style="primary",
                    icon=icons[i * rows + j],
                    layout=widgets.Layout(width="28px", padding="0px"),
                )


        def toolbar_click(change):
            """
            Handles the event when the toolbar button is clicked. If the new value of the change is True, it sets the children of the toolbar to include both the close button and the toolbar button, as well as the grid. Otherwise, it sets the children of the toolbar to only include the toolbar button.

            Parameters:
            change (dict): A dictionary containing the new value. The new state of the button is expected to be in change['new'].

            Returns:
            None
            """
            if change["new"]:
                toolbar.children = [widgets.HBox([close_button, toolbar_button]), grid]
            else:
                toolbar.children = [toolbar_button]

        toolbar_button.observe(toolbar_click, "value")
        toolbar_ctrl = WidgetControl(widget=toolbar, position="topright")
        self.add(toolbar_ctrl)

        output = widgets.Output()
        output_control = WidgetControl(widget=output, position="bottomright")
        self.add(output_control)

        def toolbar_callback(change):
            """
            Handles the event when a toolbar button is clicked. Depending on the icon of the clicked button, it performs different actions.

            Parameters:
            change: An object representing the clicked button. The icon of the button is expected to be in change.icon.

            Returns:
            None
            """
            if change.icon == "folder-open":
                with output:
                    output.clear_output()
                    print(f"You can open a file")
            elif change.icon == "map":
                with output:
                    output.clear_output()
                    print(f"You can add a layer")
            else:
                with output:
                    output.clear_output()
                    print(f"Icon: {change.icon}")
        

        for tool in grid.children:
            tool.on_click(toolbar_callback)

        with output:
            print("Toolbar is ready")



    import pandas as pd
    import geopandas as gpd
    import json


    def add_points(self, df):
        """
        Adds points to the map based on the data in the DataFrame. Each point represents a city, with its color indicating the population of the city. A rank column is added to the DataFrame based on the population. A legend is also added to the map to indicate the population ranges for each color.

        Parameters:
        df (pandas.DataFrame): The DataFrame containing the data. It is expected to have columns 'population', 'latitude', 'longitude', 'name', and 'country'.

        Returns:
        None
        """

        # Add a rank column based on population
        df['rank'] = df['population'].rank(method='min')
    
        # Define the color bins for the population
        bins = [500, 50000, 500000, 5000000, 50000000, float('inf')]
        colors = ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15']
        for _, row in df.iterrows():
            # Determine the color for the population
            for i, b in enumerate(bins):
                if row['population'] <= b:
                    color = colors[i]
                    break
    
            circle = ipyleaflet.Circle(
                location=(row['latitude'], row['longitude']),
                radius=50000,  # Increase the radius to make the circle bigger
                color=color,
                fill_color=color,
                fill_opacity=0.8
            )
            message = widgets.HTML(
                value=f"City: {row['name']}<br><b>Country: {row['country']}</b><br>Population: {row['population']}<br><b>Rank: {row['rank']}</b>",
                placeholder='',
                description='',
            )
            circle.popup = message
            self.add_layer(circle)
    
        # Add a legend
        legend_html = """
        <div style="width: 100px; height: 90px; 
            border:2px solid grey; z-index:9999; font-size:10px; line-height:1.2;">
        <strong>&nbsp; Population </strong><br>
        <div style="margin-top:5px;">
        &nbsp; 500 &nbsp; <i class="fa fa-circle fa-1x" style="color:#fee5d9"></i><br>
        &nbsp; 50000 &nbsp; <i class="fa fa-circle fa-1x" style="color:#fcae91"></i><br>
        &nbsp; 500000 &nbsp; <i class="fa fa-circle fa-1x" style="color:#fb6a4a"></i><br>
        &nbsp; 5000000 &nbsp; <i class="fa fa-circle fa-1x" style="color:#de2d26"></i><br>
        &nbsp; 50000000 &nbsp; <i class="fa fa-circle fa-1x" style="color:#a50f15"></i>
        </div>
        """
        legend = widgets.HTML(legend_html)
        legend_control = WidgetControl(widget=legend, position='bottomleft')
        self.add_control(legend_control)