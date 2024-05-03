"""Main module."""

import ipyleaflet
from ipyleaflet import Map, basemaps, WidgetControl, Marker, Polyline, TileLayer
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


    def add_xy_data(
        self,
        in_csv,
        x="longitude",
        y="latitude",
        label=None,
        layer_name="Marker cluster",
    ):
        """Adds points from a CSV file containing lat/lon information and display data on the map.

        Args:
            in_csv (str): The file path to the input CSV file.
            x (str, optional): The name of the column containing longitude coordinates. Defaults to "longitude".
            y (str, optional): The name of the column containing latitude coordinates. Defaults to "latitude".
            label (str, optional): The name of the column containing label information to used for marker popup. Defaults to None.
            layer_name (str, optional): The layer name to use. Defaults to "Marker cluster".

        Raises:
            FileNotFoundError: The specified input csv does not exist.
            ValueError: The specified x column does not exist.
            ValueError: The specified y column does not exist.
            ValueError: The specified label column does not exist.
        """


import pandas as pd
from shapely.geometry import Point

def csv_to_df(data):
    df = pd.read_csv(data)
    df["geometry"] = df.apply(lambda x: Point((float(x["longitude"]), float(x["latitude"]))), axis=1)
    return df

import geopandas as gpd
from shapely.geometry import Point
import pandas as pd



import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def csv_to_shp(input_csv_path, output_shp_path):
    # Load data
    df = pd.read_csv(input_csv_path)

    # Ensure the CSV has 'Longitude' and 'Latitude' columns
    if 'longitude' not in df.columns or 'latitude' not in df.columns:
        raise ValueError("CSV file must contain 'longitude' and 'latitude' columns.")

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df['longitude'], df['latitude'])],
        crs="EPSG:4326"
    )

    # Save to shapefile
    gdf.to_file(output_shp_path)
    print(f"Shapefile created at {output_shp_path}")
    


import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

def csv_to_geojson(input_csv_path, display_map=False):
    # Load data
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {input_csv_path}")
        return None

    # Ensure the CSV has 'Longitude', 'Latitude', and 'Population' columns
    required_columns = ['longitude', 'latitude', 'population']
    if not all(col in df.columns for col in required_columns):
        missing_columns = [col for col in required_columns if col not in df.columns]
        print(f"Error: CSV file must contain the following columns: {', '.join(missing_columns)}")
        return None

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df['longitude'], df['latitude'])],
        crs="EPSG:4326"
    )

    # Display the map if requested
    if display_map:
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(column='population', cmap='viridis', legend=True, ax=ax)
        ax.set_title('Population Map')
        plt.show()

    return gdf


import os
import urllib.request
import zipfile
import tarfile

def download_from_url(
    url: str,
    out_file_name: str = None,
    out_dir: str = ".",
    unzip: bool = True,
    verbose: bool = True,
):
    """Download a file from a URL and optionally unzip it.

    Args:
        url (str): The HTTP URL to download.
        out_file_name (str, optional): The output file name to use. Defaults to None.
        out_dir (str, optional): The output directory to use. Defaults to '.'.
        unzip (bool, optional): Whether to unzip the downloaded file if it is a zip file. Defaults to True.
        verbose (bool, optional): Whether to display or not the output of the function.
    """


def add_data(
    self,
    data,
    column,
    colors=None,
    labels=None,
    cmap=None,
    scheme="Quantiles",
    k=5,
    add_legend=True,
    legend_title=None,
    legend_position="bottomright",
    legend_kwds=None,
    classification_kwds=None,
    layer_name="Untitled",
    style=None,
    hover_style=None,
    style_callback=None,
    marker_radius=10,
    marker_args=None,
    info_mode="on_hover",
    encoding="utf-8",
    **kwargs,
):
    """Add vector data to the map with a variety of classification schemes.

    Args:
        data (str | pd.DataFrame | gpd.GeoDataFrame): The data to classify. It can be a filepath to a vector dataset, a pandas dataframe, or a geopandas geodataframe.
        column (str): The column to classify.
        cmap (str, optional): The name of a colormap recognized by matplotlib. Defaults to None.
        colors (list, optional): A list of colors to use for the classification. Defaults to None.
        labels (list, optional): A list of labels to use for the legend. Defaults to None.
        scheme (str, optional): Name of a choropleth classification scheme (requires mapclassify).
            Name of a choropleth classification scheme (requires mapclassify).
            A mapclassify.MapClassifier object will be used
            under the hood. Supported are all schemes provided by mapclassify (e.g.
            'BoxPlot', 'EqualInterval', 'FisherJenks', 'FisherJenksSampled',
            'HeadTailBreaks', 'JenksCaspall', 'JenksCaspallForced',
            'JenksCaspallSampled', 'MaxP', 'MaximumBreaks',
            'NaturalBreaks', 'Quantiles', 'Percentiles', 'StdMean',
            'UserDefined'). Arguments can be passed in classification_kwds.
        k (int, optional): Number of classes (ignored if scheme is None or if column is categorical). Default to 5.
        add_legend (bool, optional): Whether to add a legend to the map. Defaults to True.
        legend_title (str, optional): The title of the legend. Defaults to None.
        legend_position (str, optional): The position of the legend. Can be 'topleft', 'topright', 'bottomleft', or 'bottomright'. Defaults to 'bottomright'.
        legend_kwds (dict, optional): Keyword arguments to pass to :func:`matplotlib.pyplot.legend` or `matplotlib.pyplot.colorbar`. Defaults to None.
            Keyword arguments to pass to :func:`matplotlib.pyplot.legend` or
            Additional accepted keywords when `scheme` is specified:
            fmt : string
                A formatting specification for the bin edges of the classes in the
                legend. For example, to have no decimals: ``{"fmt": "{:.0f}"}``.
            labels : list-like
                A list of legend labels to override the auto-generated labblels.
                Needs to have the same number of elements as the number of
                classes (`k`).
            interval : boolean (default False)
                An option to control brackets from mapclassify legend.
                If True, open/closed interval brackets are shown in the legend.
        classification_kwds (dict, optional): Keyword arguments to pass to mapclassify. Defaults to None.
        layer_name (str, optional): The layer name to be used.. Defaults to "Untitled".
        style (dict, optional): A dictionary specifying the style to be used. Defaults to None.
            style is a dictionary of the following form:
                style = {
                "stroke": False,
                "color": "#ff0000",
                "weight": 1,
                "opacity": 1,
                "fill": True,
                "fillColor": "#ffffff",
                "fillOpacity": 1.0,
                "dashArray": "9"
                "clickable": True,
            }
        hover_style (dict, optional): Hover style dictionary. Defaults to {}.
            hover_style is a dictionary of the following form:
                hover_style = {"weight": style["weight"] + 1, "fillOpacity": 0.5}
        style_callback (function, optional): Styling function that is called for each feature, and should return the feature style. This styling function takes the feature as argument. Defaults to None.
            style_callback is a function that takes the feature as argument and should return a dictionary of the following form:
            style_callback = lambda feat: {"fillColor": feat["properties"]["color"]}
        info_mode (str, optional): Displays the attributes by either on_hover or on_click. Any value other than "on_hover" or "on_click" will be treated as None. Defaults to "on_hover".
        encoding (str, optional): The encoding of the GeoJSON file. Defaults to "utf-8".
        **kwargs: Additional keyword arguments to pass to the GeoJSON class, such as fields, which can be a list of column names to be included in the popup.

    """

    gdf, legend_dict = classify(
        data=data,
        column=column,
        cmap=cmap,
        colors=colors,
        labels=labels,
        scheme=scheme,
        k=k,
        legend_kwds=legend_kwds,
        classification_kwds=classification_kwds,
    )

    if legend_title is None:
        legend_title = column

    if style is None:
        style = {
            # "stroke": False,
            # "color": "#ff0000",
            "weight": 1,
            "opacity": 1,
            # "fill": True,
            # "fillColor": "#ffffff",
            "fillOpacity": 1.0,
            # "dashArray": "9"
            # "clickable": True,
        }
        if colors is not None:
            style["color"] = "#000000"

    if hover_style is None:
        hover_style = {"weight": style["weight"] + 1, "fillOpacity": 0.5}

    if style_callback is None:
        style_callback = lambda feat: {"fillColor": feat["properties"]["color"]}

    if gdf.geometry.geom_type.unique().tolist()[0] == "Point":
        columns = gdf.columns.tolist()
        if "category" in columns:
            columns.remove("category")
        if "color" in columns:
            columns.remove("color")
        if marker_args is None:
            marker_args = {}
        if "fill_color" not in marker_args:
            marker_args["fill_color"] = gdf["color"].tolist()
        if "stroke" not in marker_args:
            marker_args["stroke"] = False
        if "fill_opacity" not in marker_args:
            marker_args["fill_opacity"] = 0.8

        marker_args["radius"] = marker_radius

        self.add_markers(gdf[columns], layer_name=layer_name, **marker_args)
    else:
        self.add_gdf(
            gdf,
            layer_name=layer_name,
            style=style,
            hover_style=hover_style,
            style_callback=style_callback,
            info_mode=info_mode,
            encoding=encoding,
            **kwargs,
        )
    if add_legend:
        self.add_legend(
            title=legend_title, legend_dict=legend_dict, position=legend_position
        )