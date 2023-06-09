"""
@file
@brief Stitch Images Script
@details This script stitches together a set of images into a grid and saves the result as an output image file.
@version 1.0
@date 2023-06-09
@author Sovexe (https://github.com/Sovexe)
@license ISC
"""

import os
import argparse
import glob
from PIL import Image, ImageFile
import subprocess
import sys
import shutil

"""
Module Imports and Usage in This Script:
- os: Used for file and directory operations, such as checking file existence, creating directories, and removing files.
- argparse: Enables command-line argument parsing and provides a structured way to define and handle command-line arguments for this script.
- glob: Utilized to retrieve a list of file paths that match a specified pattern, used for gathering input image files.
- PIL (Python Imaging Library):
    - Image: Allows opening, manipulating, and saving various image formats. Used for loading and pasting images, as well as manipulating transparency.
    - ImageFile: Provides support for loading and saving images, particularly when working with truncated image files.
- subprocess: Invoked to execute the external program `pngquant` for reducing the file size of the output image.
- sys: Used for exiting the script if the user chooses not to overwrite an existing output file.
- shutil: Utilized for moving the temporary output file to the desired output path, as well as for removing the temporary file if it exists.

Note: When using the `--reduce` option, the script relies on the availability of `pngquant`. Ensure that `pngquant` is either installed and accessible in the system's PATH
      or placed in the same folder as this script. For more information about `pngquant`, visit https://pngquant.org/.
"""

ImageFile.LOAD_TRUNCATED_IMAGES = True

def lazy_open_image(filename):
    """
    Lazily opens an image file.

    Args:
        filename (str): The filename of the image.

    Yields:
        Image: The opened image object.

    """
    with open(filename, 'rb') as f:
        with Image.open(f) as image:
            yield image

def stitch_images(directory, output, fill, reduce, verbose, colorkey, process_colorkey, grid_rows, grid_cols):
    """
    Stitches images together into a grid and saves the result as an output image file.

    Args:
        directory (str): The directory containing the input images.
        output (str): The output file path.
        fill (str): The path to an optional fill image.
        reduce (bool): Flag to indicate whether to reduce the output file size using pngquant.
        verbose (bool): Flag to indicate whether to print verbose output.
        colorkey (List[int]): The RGB color key to be processed.
        process_colorkey (bool): Flag to indicate whether to process the color key.
        grid_rows (int): The number of rows in the grid.
        grid_cols (int): The number of columns in the grid.

    """
    if os.path.exists(output):
        response = input(f"File {output} already exists. Overwrite? (y/n) ")
        if response.lower() != 'y':
            print("Exiting without overwriting existing file.")
            sys.exit()
        os.remove(output)  # Remove the existing output file

    image_files = sorted(glob.glob(f"{directory}/*.png"))
    num_images = len(image_files)
    assert num_images > 0, "No input images found in the directory."

    num_cells = grid_rows * grid_cols
    assert num_images <= num_cells, "Number of images exceeds the grid capacity."

    # Get the largest dimension of the input images
    max_image_size = 0
    for img_file in image_files:
        with Image.open(img_file) as img:
            max_image_size = max(max_image_size, max(img.size))

    cell_size = max_image_size  # Set the grid cell size to the largest dimension of the images

    result_width = cell_size * grid_cols
    result_height = cell_size * grid_rows

    result = Image.new('RGBA', (result_width, result_height))

    # If a fill image is provided, open it and resize it to the cell size
    if fill:
        fill_image = Image.open(fill)
        fill_image_resized = fill_image.resize((cell_size, cell_size))

    for i, img_file in enumerate(image_files):
        x_pos = (i % grid_cols) * cell_size
        y_pos = (i // grid_cols) * cell_size
        if verbose:
            print(f"Pasting {img_file} at position ({x_pos}, {y_pos})")

        for img in lazy_open_image(img_file):
            if process_colorkey and colorkey:
                img = img.convert("RGBA")
                data = img.getdata()
                new_data = []
                for item in data:
                    if item[:3] == tuple(colorkey):
                        new_data.append((0, 0, 0, 0))  # Transparent pixel
                    else:
                        new_data.append(item)
                img.putdata(new_data)

            # If a fill image was provided, paste it onto the result image
            if fill:
                result.paste(fill_image_resized, (x_pos, y_pos))
            # Paste the individual image onto the result image
            result.paste(img, (x_pos, y_pos), mask=img)

    os.makedirs(os.path.dirname(output), exist_ok=True)

    temp_file = "temp.png"
    result.save(temp_file, "PNG")

    if reduce:
        if verbose:
            print(f"Reducing file size with pngquant")
        subprocess.run(['pngquant', '256', '-o', output, temp_file], check=True)
    else:
        shutil.move(temp_file, output)

    # Clean up the temporary file if it exists
    if os.path.exists(temp_file):
        os.remove(temp_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_path', default='./', help="The directory containing the images.")
    parser.add_argument('--out_file', default='output.png', help="The output file name.")
    parser.add_argument('--fill', default=None, help="An optional fill image.")
    parser.add_argument('--reduce', action='store_true', help="Use pngquant to reduce the output file size.")
    parser.add_argument('--verbose', action='store_true', help="Print verbose output.")
    parser.add_argument('--colorkey', type=int, nargs=3,
                        metavar=('R', 'G', 'B'), default=[255, 0, 228],
                        help="Specify the RGB color key. Default: 255 0 228")
    parser.add_argument('--process-colorkey', action='store_true',
                        help="Flag to indicate whether to process the color key.")
    parser.add_argument('--grid-rows', type=int, default=10,
                        help="The number of rows in the grid. Default: 10")
    parser.add_argument('--grid-cols', type=int, default=10,
                        help="The number of columns in the grid. Default: 10")

    args = parser.parse_args()
    output_path = os.path.join(os.path.dirname(__file__), args.out_file)

    stitch_images(args.dir_path, output_path, args.fill, args.reduce, args.verbose, args.colorkey, args.process_colorkey, args.grid_rows, args.grid_cols)
