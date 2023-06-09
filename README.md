# Image Stitcher
An image stitcher script that stitches together a set of images into a grid and saves the result as an output image file. The script also provides the ability to use a fill image that fills in all parts of the output made transparent by a specified color key.

## Requirements
- Python 3.6+
- PIL (Python Imaging Library)
- Optional: `pngquant` for reducing the output file size. Install it or place it in the same folder as this script.

## Usage

### Arguments
- `--dir_path`: The directory containing the images. (Default: `./`)
- `--out_file`: The output file name. (Default: `output.png`)
- `--fill`: An optional fill image. (Default: None)
- `--reduce`: Use `pngquant` to reduce the output file size.
- `--verbose`: Print verbose output.
- `--colorkey R G B`: Specify the RGB color key to make pixels transparent. (Default: `255 0 228`)
- `--process-colorkey`: Process the color key.
- `--grid-rows`: The number of rows in the grid. (Default: `10`)
- `--grid-cols`: The number of columns in the grid. (Default: `10`)

### Example Command
```
python mapstitch.py --dir_path ./images --out_file result.png --fill fill.png --reduce --verbose --colorkey 255 0 228 --process-colorkey --grid-rows 10 --grid-cols 10
```
This command takes all PNG images in the `./images` directory, stitches them into a 10x10 grid, processes the color key `255 0 228` to make those pixels transparent, uses `fill.png` as the fill image for transparent pixels, reduces the output file size with `pngquant`, and saves the result as `result.png` in the `./output` directory.

## Notes
When using the `--reduce` option, the script relies on the availability of `pngquant`. Make sure that `pngquant` is either installed and accessible in your system's PATH or placed in the same folder as this script.

The fill image will be resized to fit each cell of the grid and will show through wherever an image in the grid is transparent. This is particularly useful when using the `--colorkey` option to make certain pixels transparent.
