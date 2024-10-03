import pyvips
import tifffile
from ome_types import from_xml, to_xml
import copy
import numpy as np

class OMESlicer:
    def __init__(self, ome_tiff_path=None, existing_slicer=None, x=None, y=None, width=None, height=None):
        """
        Initialize the OMESlicer class.

        Args:
            ome_tiff_path (str, optional): Path to the OME-TIFF file.
            existing_slicer (OMESlicer, optional): Another OMESlicer object to create a new instance from (e.g., for cropping).
            x (int, optional): X coordinate for cropping.
            y (int, optional): Y coordinate for cropping.
            width (int, optional): Width of the crop.
            height (int, optional): Height of the crop.
        """
        if ome_tiff_path:
            # Initialize from file path
            self.ome_tiff_path = ome_tiff_path
            self.pyvips_image = None  # Lazy load pyvips image when needed
            self.ome_metadata = self._load_ome_metadata()
            self.ome = from_xml(self.ome_metadata)
            self.crop_info = None
            self.cropped_dimensions = None  # No cropping yet
        elif existing_slicer:
            # Initialize from an existing OMESlicer (e.g., after cropping)
            self.ome_tiff_path = existing_slicer.ome_tiff_path
            self.ome = copy.deepcopy(existing_slicer.ome)  # Deep copy of the metadata to avoid modifying the original
            self.crop_info = (x, y, width, height)
            self.cropped_dimensions = (width, height)  # Store cropped dimensions
            self.ome_metadata = self._update_metadata_for_crop(width, height)
            self.pyvips_image = None  # Lazy load for the cropped version
        else:
            raise ValueError("Either ome_tiff_path or existing_slicer must be provided.")

    def _load_ome_metadata(self):
        """Load OME metadata from the TIFF file."""
        with tifffile.TiffFile(self.ome_tiff_path) as tif:
            return tif.ome_metadata

    def _update_metadata_for_crop(self, width, height):
        """Update the OME metadata to reflect the cropped dimensions."""
        cropped_ome = copy.deepcopy(self.ome)
        pixels = cropped_ome.images[0].pixels
        pixels.size_x = width
        pixels.size_y = height
        return to_xml(cropped_ome)

    def load_pyvips_image(self, page=0):
        """Lazy load a specific page of the image using pyvips."""
        if not self.pyvips_image:
            self.pyvips_image = pyvips.Image.new_from_file(self.ome_tiff_path, page=page, access='sequential')
        return self.pyvips_image

    def get_image_dimensions(self):
        """
        Get the width, height, and number of channels from OME metadata.

        If the image is cropped, return the cropped dimensions.
        """
        if self.cropped_dimensions:
            width, height = self.cropped_dimensions
        else:
            pixels = self.ome.images[0].pixels
            width, height = pixels.size_x, pixels.size_y
        return width, height, self.ome.images[0].pixels.size_c

    def get_number_of_channels(self):
        """Get the number of channels from OME metadata."""
        return self.ome.images[0].pixels.size_c

    def get_dtype_from_metadata(self):
        """Get the correct NumPy dtype based on the OME metadata."""
        pixel_type = self.ome.images[0].pixels.type
        dtype_map = {
            'uint8': np.uint8,
            'uint16': np.uint16,
            'uint32': np.uint32,
            'int8': np.int8,
            'int16': np.int16,
            'int32': np.int32,
            'float': np.float32,
            'double': np.float64
        }
        return dtype_map.get(pixel_type, np.uint16)  # Default to uint16 if not found

    def crop(self, x, y, width, height):
        """
        Crop the image based on the provided dimensions.
        Returns a new OMESlicer object with updated metadata, but does not save the cropped image.
        
        Args:
            x (int): The X coordinate to start cropping.
            y (int): The Y coordinate to start cropping.
            width (int): The width of the cropped image.
            height (int): The height of the cropped image.
        
        Returns:
            OMESlicer: A new OMESlicer object representing the cropped image.
        """
        return OMESlicer(existing_slicer=self, x=x, y=y, width=width, height=height)

    def save(self, output_path):
        """Save the cropped or original image to a new OME-TIFF file."""
        if not self.crop_info:
            raise ValueError("This slicer instance has no crop info; nothing to save.")

        x, y, width, height = self.crop_info
        cropped_channel_arrays = []
        num_channels = self.get_number_of_channels()

        # Get the correct dtype for the image
        dtype = self.get_dtype_from_metadata()

        # Process each channel using pyvips and crop it
        for c in range(num_channels):
            print(f"Processing channel {c+1}/{num_channels}")
            channel_image = pyvips.Image.new_from_file(
                self.ome_tiff_path, page=c, access='sequential'
            )
            cropped_channel = channel_image.crop(x, y, width, height)

            # Convert the cropped channel to a NumPy array
            channel_array = np.ndarray(
                buffer=cropped_channel.write_to_memory(),
                dtype=dtype,
                shape=[cropped_channel.height, cropped_channel.width]
            )
            cropped_channel_arrays.append(channel_array)

        # Write the cropped image to a new OME-TIFF file
        with tifffile.TiffWriter(output_path, bigtiff=True) as tif:
            for c in range(num_channels):
                print(f"Writing channel {c+1}/{num_channels}")
                tif.write(
                    data=cropped_channel_arrays[c],
                    photometric='minisblack',
                    compression='lzw',
                    tile=(512, 512),
                    dtype=np.uint16,  # Ensure consistent dtype
                    description=self.ome_metadata if c == 0 else None,  # Embed updated OME-XML in the first page
                    metadata=None  # Omit 'metadata' parameter
                )

    def get_ome_metadata(self):
        """Return the OME metadata."""
        return self.ome_metadata

