from PyPDF2 import PdfReader
from PIL import Image
import os
import io
import zlib
 
# Read the uploaded PDF file
pdf_path = "/home/nam/Downloads/lorem_picsum_2.pdf"
reader = PdfReader(pdf_path)
 
# Create output directory
output_dir = "./extracted_images"
os.makedirs(output_dir, exist_ok=True)
 
# Extract images
images = []
for page_num, page in enumerate(reader.pages):
    if "/XObject" in page["/Resources"]:
        xObject = page["/Resources"]["/XObject"].get_object()
        for obj in xObject:
            if xObject[obj]["/Subtype"] == "/Image":
                img_data = xObject[obj]._data
                img_filter = xObject[obj]["/Filter"]
                width = xObject[obj]["/Width"]
                height = xObject[obj]["/Height"]
                bits_per_component = xObject[obj].get("/BitsPerComponent", 8)  # Default to 8-bit
                color_space = xObject[obj].get("/ColorSpace", "/DeviceGray")
 
                # Determine Image Mode
                if color_space == "/DeviceRGB":
                    mode = "RGB"
                elif color_space == "/DeviceCMYK":
                    mode = "CMYK"
                elif color_space == "/DeviceGray":
                    mode = "L"
                else:
                    mode = "RGB"  # Default to RGB if unknown
 
                # Determine file extension
                if img_filter == "/DCTDecode":
                    ext = "jpg"
                elif img_filter == "/JPXDecode":
                    ext = "jp2"
                elif img_filter == "/FlateDecode":
                    ext = "png"
                else:
                    ext = "bin"  # Unknown format
 
                img_path = os.path.join(output_dir, f"image_page{page_num+1}.{ext}")
 
                if img_filter == "/FlateDecode":
                    try:
                        # Decompress FlateDecode (LZW compressed data)
                        decompressed_data = zlib.decompress(img_data)
 
                        # Check if it's a zipped JPEG
                        if decompressed_data[:2] == b"\xff\xd8":
                            ext = "jpg"
                            img_path = img_path.replace(".png", ".jpg")
                            with open(img_path, "wb") as f:
                                f.write(decompressed_data)
                        else:
                            # Convert grayscale images properly
                            if mode == "L" and bits_per_component == 1:
                                # Convert 1-bit monochrome image to black/white
                                img = Image.frombytes("1", (width, height), decompressed_data)
                            else:
                                img = Image.frombytes(mode, (width, height), decompressed_data)
 
                            # Convert CMYK to RGB for better viewing
                            if mode == "CMYK":
                                img = img.convert("RGB")
 
                            img.save(img_path, "PNG")
 
                    except Exception as e:
                        print(f"Error processing FlateDecode image on page {page_num + 1}: {e}")
 
                else:
                    # Save directly for standard JPEGs and JPX images
                    with open(img_path, "wb") as f:
                        f.write(img_data)
 
                images.append(img_path)
 
# List extracted images
print(f"Extracted images: {images}")