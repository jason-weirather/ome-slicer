# ome-slicer

Efficient OME-TIFF manipulation for large datasets.

## Overview

**ome-slicer** is a Python library designed to facilitate efficient manipulation of OME-TIFF files, especially those too large to fit into memory. It provides a user-friendly API for common operations like cropping, slicing, and metadata editing while ensuring memory efficiency through lazy loading and tile-based processing.

## Features

- **Efficient Cropping and Slicing**: Crop images to specified coordinates without loading entire datasets into memory.
- **Metadata Management**: Read, modify, and write OME-XML metadata to keep it in sync with image data after modifications.
- **Lazy Loading**: Load image data only when needed to optimize memory usage.
- **Channel Handling**: Process images with multiple channels efficiently.
- **Tile-Based Processing**: Read and write data in tiles to handle large images.

## Installation

Ensure you have Python 3.8 or higher installed. Install **ome-slicer** using pip:

```bash
pip install ome-slicer
```

## Dependencies

The following packages are required and will be installed automatically:

- `numpy >= 1.20`
- `tifffile >= 2023.7.10`
- `pyvips >= 2.2.3`
- `ome-types >= 0.5.2`

## Usage

### Importing the Library

```python
from omeslicer.core import OMESlicer
```

### Cropping an OME-TIFF Image

```python
# Initialize the OMESlicer with the path to your OME-TIFF file
slicer = OMESlicer(ome_tiff_path='path_to_your_image.ome.tiff')

# Define cropping coordinates
x = 10000  # X coordinate to start cropping
y = 10000  # Y coordinate to start cropping
width = 5000  # Width of the cropped area
height = 5000  # Height of the cropped area

# Perform the cropping operation
cropped_slicer = slicer.crop(x=x, y=y, width=width, height=height)

# Save the cropped image to a new OME-TIFF file
cropped_slicer.save('cropped_image.ome.tiff')
```

### Accessing Metadata

```python
# Get the OME metadata as an XML string
metadata_xml = slicer.get_ome_metadata()
print(metadata_xml)
```

### Getting Image Dimensions

```python
# Get the dimensions and number of channels
width, height, num_channels = slicer.get_image_dimensions()
print(f"Width: {width}, Height: {height}, Channels: {num_channels}")
```

### Working with Channels

```python
# Get the number of channels
num_channels = slicer.get_number_of_channels()

# Process each channel individually
for channel_index in range(num_channels):
    print(f"Processing channel {channel_index + 1}/{num_channels}")
    # Add your channel-specific processing here
```

## Example Script

Below is an example script demonstrating how to use **ome-slicer** to crop an OME-TIFF image:

```python
from omeslicer.core import OMESlicer

# Initialize the slicer with your OME-TIFF file
slicer = OMESlicer(ome_tiff_path='large_image.ome.tiff')

# Define crop coordinates (e.g., crop the central region)
full_width, full_height, _ = slicer.get_image_dimensions()
x = full_width // 4
y = full_height // 4
width = full_width // 2
height = full_height // 2

# Perform the crop operation
cropped_slicer = slicer.crop(x=x, y=y, width=width, height=height)

# Save the cropped image
cropped_slicer.save('cropped_image.ome.tiff')
```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

**ome-slicer** leverages the capabilities of:

- [pyvips](https://pypi.org/project/pyvips/) for efficient image processing
- [tifffile](https://pypi.org/project/tifffile/) for TIFF file handling
- [ome-types](https://pypi.org/project/ome-types/) for OME-XML metadata management
- [NumPy](https://numpy.org/) for numerical operations

## Keywords

- OME-TIFF
- Imaging
- Image Processing
- Bioinformatics
- Large Datasets
