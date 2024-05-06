"""This is the temp module that contains temp functions for the geotask package."""

import os
import xarray as xr
import matplotlib.pyplot as plt
import imageio
from IPython.display import Image

def save_yearly_images(netcdf_file, output_dir, output_file):
    """
    Save the yearly temperature image for each individual year as an image.
    
    Args:
        netcdf_file (str): The path to the NetCDF file.
        output_dir (str): The directory to save the images in.
        output_file (str): The path to the output gif file.
    
    Returns:
        list: A list of the image file paths that were created.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the NetCDF file
    ds = xr.open_dataset(netcdf_file, engine='netcdf4')

    # Get the number of years
    years = ds.year.values

    # Get the min and max temperature values for the colorbar
    vmin = ds.tavg.min().values
    vmax = ds.tavg.max().values

    images = []
    for year in years:
        # Select data for the current year
        year_data = ds.sel(year=year)

        # Create a plot
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(year_data.tavg.values, cmap='jet', vmin=vmin, vmax=vmax)
        ax.set_title(f"Average Annual Temperature of Sacramento Drainage, California - {year}", pad=20)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        plt.colorbar(im, ax=ax)

        # Set the ticks to display the actual latitude and longitude values
        ax.set_xticks(range(0, len(year_data.longitude), len(year_data.longitude) // 5))
        ax.set_yticks(range(0, len(year_data.latitude), len(year_data.latitude) // 5))
        ax.set_xticklabels([f"{lon:.1f}" for lon in year_data.longitude[::len(year_data.longitude) // 5].values])
        ax.set_yticklabels([f"{lat:.1f}" for lat in year_data.latitude[::len(year_data.latitude) // 5].values])

        # Save the image
        image_path = os.path.join(output_dir, f"temperature_map_year_{year}.png")
        plt.savefig(image_path)
        plt.close()

        # Append the image file path to the images list
        images.append(image_path)

    # Read the images and save them as a gif
    imageio.mimsave(output_file, [imageio.imread(img) for img in images], fps=5)
    # Get the absolute path of the output file
    abs_path = os.path.abspath(output_file)

    print(f"GIF saved at {abs_path}")

    # Close the dataset
    ds.close()

    #return images



def show_gif(output_file):
    """
    Display a gif file in a Jupyter notebook.
    
    Args:
        output_file (str): The path to the gif file.
    """
    return Image(filename=output_file)