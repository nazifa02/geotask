"""The common module contains common functions and classes used by the other modules.
"""

def hello_world():
    """Prints "Hello World!" to the console.
    """
    print("Hello World!")

def hello (name):
    """Prints "Hello {name}!" to console.

    Args:
       name (str): The name to print.
    """
    print(f"Hello {name}!")
    

def random_number():
    """Returns a random number between 0 and 1.

    Returns:
        float: A random number between 0 and 1.
    """
    import random
    return random.random()

import os

def download_file(
    url=None,
    output=None,
    quiet=False,
    proxy=None,
    speed=None,
    use_cookies=True,
    verify=True,
    id=None,
    fuzzy=False,
    resume=False,
    unzip=True,
    overwrite=False,
    subfolder=False,
):
    """Download a file from URL, including Google Drive shared URL.

    Args:
        url (str, optional): Google Drive URL is also supported. Defaults to None.
        output (str, optional): Output filename. Default is basename of URL.
        quiet (bool, optional): Suppress terminal output. Default is False.
        proxy (str, optional): Proxy. Defaults to None.
        speed (float, optional): Download byte size per second (e.g., 256KB/s = 256 * 1024). Defaults to None.
        use_cookies (bool, optional): Flag to use cookies. Defaults to True.
        verify (bool | str, optional): Either a bool, in which case it controls whether the server's TLS certificate is verified, or a string,
            in which case it must be a path to a CA bundle to use. Default is True.. Defaults to True.
        id (str, optional): Google Drive's file ID. Defaults to None.
        fuzzy (bool, optional): Fuzzy extraction of Google Drive's file Id. Defaults to False.
        resume (bool, optional): Resume the download from existing tmp file if possible. Defaults to False.
        unzip (bool, optional): Unzip the file. Defaults to True.
        overwrite (bool, optional): Overwrite the file if it already exists. Defaults to False.
        subfolder (bool, optional): Create a subfolder with the same name as the file. Defaults to False.

    Returns:
        str: The output file path.
    """
    try:
        import gdown
    except ImportError:
        print(
            "The gdown package is required for this function. Use `pip install gdown` to install it."
        )
        return

    if output is None:
        if isinstance(url, str) and url.startswith("http"):
            output = os.path.basename(url)

    out_dir = os.path.abspath(os.path.dirname(output))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if isinstance(url, str):
        if os.path.exists(os.path.abspath(output)) and (not overwrite):
            print(
                f"{output} already exists. Skip downloading. Set overwrite=True to overwrite."
            )
            return os.path.abspath(output)
        else:
            url = github_raw_url(url)

    if "https://drive.google.com/file/d/" in url:
        fuzzy = True

    output = gdown.download(
        url, output, quiet, proxy, speed, use_cookies, verify, id, fuzzy, resume
    )

    if unzip:
        if output.endswith(".zip"):
            with zipfile.ZipFile(output, "r") as zip_ref:
                if not quiet:
                    print("Extracting files...")
                if subfolder:
                    basename = os.path.splitext(os.path.basename(output))[0]

                    output = os.path.join(out_dir, basename)
                    if not os.path.exists(output):
                        os.makedirs(output)
                    zip_ref.extractall(output)
                else:
                    zip_ref.extractall(os.path.dirname(output))
        elif output.endswith(".tar.gz") or output.endswith(".tar"):
            if output.endswith(".tar.gz"):
                mode = "r:gz"
            else:
                mode = "r"

            with tarfile.open(output, mode) as tar_ref:
                if not quiet:
                    print("Extracting files...")
                if subfolder:
                    basename = os.path.splitext(os.path.basename(output))[0]
                    output = os.path.join(out_dir, basename)
                    if not os.path.exists(output):
                        os.makedirs(output)
                    tar_ref.extractall(output)
                else:
                    tar_ref.extractall(os.path.dirname(output))

    return os.path.abspath(output)


def make_gif(images, out_gif, ext="jpg", fps=10, loop=0, mp4=False, clean_up=False):
    """Creates a gif from a list of images.

    Args:
        images (list | str): The list of images or input directory to create the gif from.
        out_gif (str): File path to the output gif.
        ext (str, optional): The extension of the images. Defaults to 'jpg'.
        fps (int, optional): The frames per second of the gif. Defaults to 10.
        loop (int, optional): The number of times to loop the gif. Defaults to 0.
        mp4 (bool, optional): Whether to convert the gif to mp4. Defaults to False.

    """
    import glob
    from PIL import Image

    ext = ext.replace(".", "")

    if isinstance(images, str) and os.path.isdir(images):
        images = list(glob.glob(os.path.join(images, f"*.{ext}")))
        if len(images) == 0:
            raise ValueError("No images found in the input directory.")
    elif not isinstance(images, list):
        raise ValueError("images must be a list or a path to the image directory.")

    images.sort()

    frames = [Image.open(image) for image in images]
    frame_one = frames[0]
    frame_one.save(
        out_gif,
        format="GIF",
        append_images=frames,
        save_all=True,
        duration=int(1000 / fps),
        loop=loop,
    )

    if mp4:
        if not is_tool("ffmpeg"):
            print("ffmpeg is not installed on your computer.")
            return

        if os.path.exists(out_gif):
            out_mp4 = out_gif.replace(".gif", ".mp4")
            cmd = f"ffmpeg -loglevel error -i {out_gif} -vcodec libx264 -crf 25 -pix_fmt yuv420p {out_mp4}"
            os.system(cmd)
            if not os.path.exists(out_mp4):
                raise Exception(f"Failed to create mp4 file.")
    if clean_up:
        for image in images:
            os.remove(image)

    
def add_text_to_gif(
    in_gif,
    out_gif,
    xy=None,
    text_sequence=None,
    font_type="arial.ttf",
    font_size=20,
    font_color="#000000",
    add_progress_bar=True,
    progress_bar_color="white",
    progress_bar_height=5,
    duration=100,
    loop=0,
):
    """Adds animated text to a GIF image.

    Args:
        in_gif (str): The file path to the input GIF image.
        out_gif (str): The file path to the output GIF image.
        xy (tuple, optional): Top left corner of the text. It can be formatted like this: (10, 10) or ('15%', '25%'). Defaults to None.
        text_sequence (int, str, list, optional): Text to be drawn. It can be an integer number, a string, or a list of strings. Defaults to None.
        font_type (str, optional): Font type. Defaults to "arial.ttf".
        font_size (int, optional): Font size. Defaults to 20.
        font_color (str, optional): Font color. It can be a string (e.g., 'red'), rgb tuple (e.g., (255, 127, 0)), or hex code (e.g., '#ff00ff').  Defaults to '#000000'.
        add_progress_bar (bool, optional): Whether to add a progress bar at the bottom of the GIF. Defaults to True.
        progress_bar_color (str, optional): Color for the progress bar. Defaults to 'white'.
        progress_bar_height (int, optional): Height of the progress bar. Defaults to 5.
        duration (int, optional): controls how long each frame will be displayed for, in milliseconds. It is the inverse of the frame rate. Setting it to 100 milliseconds gives 10 frames per second. You can decrease the duration to give a smoother animation.. Defaults to 100.
        loop (int, optional): controls how many times the animation repeats. The default, 1, means that the animation will play once and then stop (displaying the last frame). A value of 0 means that the animation will repeat forever. Defaults to 0.

    """
    import io

    import pkg_resources
    from PIL import Image, ImageDraw, ImageFont, ImageSequence

    warnings.simplefilter("ignore")
    pkg_dir = os.path.dirname(pkg_resources.resource_filename("leafmap", "leafmap.py"))
    default_font = os.path.join(pkg_dir, "data/fonts/arial.ttf")

    in_gif = os.path.abspath(in_gif)
    out_gif = os.path.abspath(out_gif)

    if not os.path.exists(in_gif):
        print("The input gif file does not exist.")
        return

    if not os.path.exists(os.path.dirname(out_gif)):
        os.makedirs(os.path.dirname(out_gif))

    if font_type == "arial.ttf":
        font = ImageFont.truetype(default_font, font_size)
    elif font_type == "alibaba.otf":
        default_font = os.path.join(pkg_dir, "data/fonts/alibaba.otf")
        font = ImageFont.truetype(default_font, font_size)
    else:
        try:
            font_list = system_fonts(show_full_path=True)
            font_names = [os.path.basename(f) for f in font_list]
            if (font_type in font_list) or (font_type in font_names):
                font = ImageFont.truetype(font_type, font_size)
            else:
                print(
                    "The specified font type could not be found on your system. Using the default font instead."
                )
                font = ImageFont.truetype(default_font, font_size)
        except Exception as e:
            print(e)
            font = ImageFont.truetype(default_font, font_size)

    color = check_color(font_color)
    progress_bar_color = check_color(progress_bar_color)

    try:
        image = Image.open(in_gif)
    except Exception as e:
        print("An error occurred while opening the gif.")
        print(e)
        return

    count = image.n_frames
    W, H = image.size
    progress_bar_widths = [i * 1.0 / count * W for i in range(1, count + 1)]
    progress_bar_shapes = [
        [(0, H - progress_bar_height), (x, H)] for x in progress_bar_widths
    ]

    if xy is None:
        # default text location is 5% width and 5% height of the image.
        xy = (int(0.05 * W), int(0.05 * H))
    elif (xy is not None) and (not isinstance(xy, tuple)) and (len(xy) == 2):
        print("xy must be a tuple, e.g., (10, 10), ('10%', '10%')")
        return
    elif all(isinstance(item, int) for item in xy) and (len(xy) == 2):
        x, y = xy
        if (x > 0) and (x < W) and (y > 0) and (y < H):
            pass
        else:
            print(
                f"xy is out of bounds. x must be within [0, {W}], and y must be within [0, {H}]"
            )
            return
    elif all(isinstance(item, str) for item in xy) and (len(xy) == 2):
        x, y = xy
        if ("%" in x) and ("%" in y):
            try:
                x = int(float(x.replace("%", "")) / 100.0 * W)
                y = int(float(y.replace("%", "")) / 100.0 * H)
                xy = (x, y)
            except Exception:
                raise Exception(
                    "The specified xy is invalid. It must be formatted like this ('10%', '10%')"
                )
    else:
        print(
            "The specified xy is invalid. It must be formatted like this: (10, 10) or ('10%', '10%')"
        )
        return

    if text_sequence is None:
        text = [str(x) for x in range(1, count + 1)]
    elif isinstance(text_sequence, int):
        text = [str(x) for x in range(text_sequence, text_sequence + count + 1)]
    elif isinstance(text_sequence, str):
        try:
            text_sequence = int(text_sequence)
            text = [str(x) for x in range(text_sequence, text_sequence + count + 1)]
        except Exception:
            text = [text_sequence] * count
    elif isinstance(text_sequence, list) and len(text_sequence) != count:
        print(
            f"The length of the text sequence must be equal to the number ({count}) of frames in the gif."
        )
        return
    else:
        text = [str(x) for x in text_sequence]

    try:
        frames = []
        # Loop over each frame in the animated image
        for index, frame in enumerate(ImageSequence.Iterator(image)):
            # Draw the text on the frame
            frame = frame.convert("RGB")
            draw = ImageDraw.Draw(frame)
            # w, h = draw.textsize(text[index])
            draw.text(xy, text[index], font=font, fill=color)
            if add_progress_bar:
                draw.rectangle(progress_bar_shapes[index], fill=progress_bar_color)
            del draw

            b = io.BytesIO()
            frame.save(b, format="GIF")
            frame = Image.open(b)

            frames.append(frame)
        # https://www.pythoninformer.com/python-libraries/pillow/creating-animated-gif/
        # Save the frames as a new image

        frames[0].save(
            out_gif,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=loop,
            optimize=True,
        )
    except Exception as e:
        print(e)



from typing import Union, List, Optional, Tuple
from ipywidgets import widgets

def create_timelapse(
    images: Union[List[str], str],
    out_gif: str,
    ext: str = ".tif",
    bands: Optional[List] = None,
    size: Optional[Tuple] = None,
    bbox: Optional[List] = None,
    fps: int = 5,
    loop: int = 0,
    add_progress_bar: bool = True,
    progress_bar_color: str = "blue",
    progress_bar_height: int = 5,
    add_text: bool = False,
    text_xy: Optional[Tuple] = None,
    text_sequence: Optional[List] = None,
    font_type: str = "arial.ttf",
    font_size: int = 20,
    font_color: str = "black",
    mp4: bool = False,
    quiet: bool = True,
    reduce_size: bool = False,
    clean_up: bool = True,
    **kwargs,
):
    """Creates a timelapse gif from a list of images.

    Args:
        images (Union[List[str], str]): The list of images or input directory to create the gif from.
            For example, '/path/to/images/*.tif' or ['/path/to/image1.tif', '/path/to/image2.tif', ...]
        ...
    """
    import glob

    if isinstance(images, str):
        if not images.endswith(ext):
            images = os.path.join(images, f"*{ext}")
        images = sorted(glob.glob(images))

    if not images:
        raise ValueError("No images found in the input directory or list.")

    if isinstance(images, list) and not all(isinstance(img, str) for img in images):
        raise ValueError("images must be a list of strings or a path to the image directory.")

    import tempfile

    images.sort()

    temp_dir = os.path.join(tempfile.gettempdir(), "timelapse")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if bbox is not None:
        clip_dir = os.path.join(tempfile.gettempdir(), "clip")
        if not os.path.exists(clip_dir):
            os.makedirs(clip_dir)

        if len(bbox) == 4:
            bbox = bbox_to_geojson(bbox)

    else:
        clip_dir = None

    output = widgets.Output()

    if "out_ext" in kwargs:
        out_ext = kwargs["out_ext"].lower()
    else:
        out_ext = ".jpg"

    try:
        for index, image in enumerate(images):
            if bbox is not None:
                clip_file = os.path.join(clip_dir, os.path.basename(image))
                with output:
                    clip_image(image, mask=bbox, output=clip_file, to_cog=False)
                image = clip_file

            if "add_prefix" in kwargs:
                basename = (
                    str(f"{index + 1}").zfill(len(str(len(images))))
                    + "-"
                    + os.path.basename(image).replace(ext, out_ext)
                )
            else:
                basename = os.path.basename(image).replace(ext, out_ext)
            if not quiet:
                print(f"Processing {index+1}/{len(images)}: {basename} ...")

            # ignore GDAL warnings
            with output:
                numpy_to_image(
                    image, os.path.join(temp_dir, basename), bands=bands, size=size
                )
        make_gif(
            temp_dir,
            out_gif,
            ext=out_ext,
            fps=fps,
            loop=loop,
            mp4=mp4,
            clean_up=clean_up,
        )

        if clip_dir is not None:
            shutil.rmtree(clip_dir)

        if add_text:
            add_text_to_gif(
                out_gif,
                out_gif,
                text_xy,
                text_sequence,
                font_type,
                font_size,
                font_color,
                add_progress_bar,
                progress_bar_color,
                progress_bar_height,
                1000 / fps,
                loop,
            )
        elif add_progress_bar:
            add_progress_bar_to_gif(
                out_gif,
                out_gif,
                progress_bar_color,
                progress_bar_height,
                1000 / fps,
                loop,
            )

        if reduce_size:
            reduce_gif_size(out_gif)
    except Exception as e:
        print(e)

def show_image(
    img_path: str, width: Optional[int] = None, height: Optional[int] = None
):
    """Shows an image within Jupyter notebook.

    Args:
        img_path (str): The image file path.
        width (int, optional): Width of the image in pixels. Defaults to None.
        height (int, optional): Height of the image in pixels. Defaults to None.

    """
    from IPython.display import display

    try:
        out = widgets.Output()
        # layout={'border': '1px solid black'})
        # layout={'border': '1px solid black', 'width': str(width + 20) + 'px', 'height': str(height + 10) + 'px'},)
        out.outputs = ()
        display(out)
        with out:
            file = open(img_path, "rb")
            image = file.read()
            if (width is None) and (height is None):
                display(widgets.Image(value=image))
            elif (width is not None) and (height is not None):
                display(widgets.Image(value=image, width=width, height=height))
            else:
                print("You need set both width and height.")
                return
    except Exception as e:
        print(e)



