import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

def inspect_image(image_path):
    image = Image.open(image_path)

    print("Image Format:", image.format)
    print("Image Dimensions:", image.size)
    print("Image Mode:", image.mode)

    pixels = np.array(image)

    print("Pixel Array Shape:", pixels.shape)

    alpha = pixels[:,:,3]
    print("Minimum Alpha:", alpha.min())
    print("Maximum Alpha:", alpha.max())

def convert_to_rgb(image_path):
    with Image.open(image_path) as image:
        rgb_image = image.convert("RGB")
    return rgb_image

def get_image_pixels(image_path):
    rgb_image = convert_to_rgb(image_path)
    pixels = np.array(rgb_image)
    pixels = pixels.reshape(-1, 3)

    return pixels

def cluster_colors(pixels, number_of_colors=5):
    model = KMeans(n_clusters=number_of_colors, random_state=42, n_init=10)
    model.fit(pixels)
    return model

def calculate_color_percentages(model):
    counts = np.bincount(model.labels_)
    percentages = (counts / len(model.labels_)) * 100
    return percentages

def build_palette(model, percentages):
    palette = []

    for center, percentage in zip(model.cluster_centers_, percentages):
        rgb = center.round().astype(int)
        hex_color = "#{:02X}{:02X}{:02X}".format(*rgb)
        palette.append({"hex": hex_color,"rgb": rgb.tolist(),"percentage": round(float(percentage), 2) })

    palette = sorted(palette, key=lambda color: color["percentage"], reverse=True)
    return palette

def extract_palette(
    image_path,
    number_of_colors=5,
    sample_size=10000
):

    pixels = get_image_pixels(image_path)

    sampled_pixels = sample_pixels(
        pixels,
        sample_size
    )

    model = cluster_colors(
        sampled_pixels,
        number_of_colors
    )

    percentages = calculate_color_percentages(model)

    palette = build_palette(model, percentages)

    return palette

def sample_pixels(pixels, sample_size=10000, random_state=42):
    rng = np.random.default_rng(random_state)
    sample_size = min(sample_size, len(pixels))

    indices = rng.choice(len(pixels), size = sample_size, replace=False)

    return pixels[indices]

def find_images(folder_path):
    folder = Path(folder_path)
    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    image_files = [file for file in folder.iterdir() if file.is_file() and file.suffix.lower() in image_extensions]

    return image_files

def process_images(folder_path):
    images = find_images(folder_path)
    failed_images = []
    results = []

    for image in images:
        try:
            palette = extract_palette(image)
            results.append({"Image Name": image.stem, "Image File": image.name, "Dominant HEX": palette[0]["hex"], "Dominant RGB": palette[0]["rgb"], "Color Palette": palette})
            print(f"Processed: {image.name}")
        except Exception as error:

            failed_images.append({
            "Image File": image.name,
            "Error": str(error)
            })

            print(f"Failed: {image.name} - {error}")

    return results, failed_images

def export_to_csv(results, output_path):
    fieldnames = ["Image Name", "Image File", "Engine", "Set", "Dominant HEX", "Dominant RGB", "Color Palette"]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for image in results:
            row = {"Image Name": image["Image Name"], "Image File": image["Image File"], "Engine": "", "Set": "", "Dominant HEX": image["Dominant HEX"], "Dominant RGB": image["Dominant RGB"], "Color Palette": json.dumps(image["Color Palette"])}

            writer.writerow(row)









#test
if __name__ == "__main__":
    folder_path = r"C:\Users\christopher.ortega\Desktop\TFTCap\misc\ArenaImageArchive\Original_Images"

    output_path = r"C:\Users\christopher.ortega\Desktop\TFTCap\misc\ArenaImageArchive\CSVExports\MasterImageDatabase.csv"

    results, failed_images = process_images(folder_path)

    export_to_csv(results, output_path)

    print("\nProcessing complete!")
    print("Images processed:", len(results))
    print("Images failed:", len(failed_images))
    print("CSV exported to:", output_path)



  