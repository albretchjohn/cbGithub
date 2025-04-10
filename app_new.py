import math
import random
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import io
import numpy as np
from scipy.spatial import cKDTree as KDTree
from multiprocessing import Pool

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

BACKGROUND = (255, 255, 255)
TOTAL_CIRCLES = 1500

color = lambda c: ((c >> 16) & 255, (c >> 8) & 255, c & 255)

COLORS_ON = [
    color(0xF9BB82), color(0xEBA170), color(0xFCCD84)
]
COLORS_OFF = [
    color(0x9CA594), color(0xACB4A5), color(0xBBB964),
    color(0xD7DAAA), color(0xE5D57D), color(0xD1D6AF)
]


# Number generation part
def create_image_with_number(number):
    width, height = 800, 800
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    font_path = "C:/Windows/Fonts/arial.ttf"
    max_font_size = 600
    font = None

    while max_font_size > 0:
        try:
            font = ImageFont.truetype(font_path, max_font_size)
            text_bbox = draw.textbbox((0, 0), str(number), font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            if text_width <= width and text_height <= height:
                break
        except IOError:
            font = ImageFont.load_default()
            break
        max_font_size -= 1

    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2 - text_height * 0.3
    draw.text((text_x, text_y), str(number), fill="black", font=font)

    return image


# Optimized Circle Generation
def generate_circles_fast(image_width, image_height, min_diameter, max_diameter, num_circles):
    radii = np.random.triangular(min_diameter / 2, (min_diameter + max_diameter) / 4, max_diameter / 2, num_circles)
    angles = np.random.uniform(0, 2 * np.pi, num_circles)
    distances = np.random.uniform(0, image_width * 0.48 - radii, num_circles)

    x = image_width / 2 + np.cos(angles) * distances
    y = image_height / 2 + np.sin(angles) * distances

    return list(zip(x, y, radii))


# Optimized Circle Overlap Checking Using KD-Tree
def check_circle_overlap(circle, circles, kd_tree):
    if len(circles) == 0:
        return False

    x, y, r = circle
    points = np.array([(c[0], c[1]) for c in circles])
    distances, _ = kd_tree.query((x, y), k=len(circles), distance_upper_bound=r * 2)

    return np.any(distances < r * 2)  # If any distance is less than sum of radii, they overlap


# Optimized Motive Overlap Checking with NumPy
def overlaps_motive(image, circle):
    x, y, r = map(int, circle)
    img_array = np.array(image)

    x_min, x_max = max(0, x - r), min(img_array.shape[1], x + r)
    y_min, y_max = max(0, y - r), min(img_array.shape[0], y + r)

    sub_region = img_array[y_min:y_max, x_min:x_max]

    return not np.all(sub_region == BACKGROUND)  # If any pixel isn't background, it overlaps


# Parallelized Circle Drawing
def draw_single_circle(args):
    draw, x, y, r, color = args
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=color)


def draw_circles_parallel(draw_image, circles, colors):
    args = [(draw_image, x, y, r, color) for (x, y, r), color in zip(circles, colors)]
    with Pool() as pool:
        pool.map(draw_single_circle, args)


# Generate Ishihara Plate with Optimized Performance
def generate_ishihara_plate(number):
    image = create_image_with_number(number)
    image2 = Image.new('RGB', image.size, BACKGROUND)
    draw_image = ImageDraw.Draw(image2)
    width, height = image.size
    min_diameter = (width + height) / 200
    max_diameter = (width + height) / 75

    circles = generate_circles_fast(width, height, min_diameter, max_diameter, TOTAL_CIRCLES)
    kd_tree = KDTree([(c[0], c[1]) for c in circles])

    filtered_circles = []
    for circle in circles:
        if not check_circle_overlap(circle, filtered_circles, kd_tree):
            filtered_circles.append(circle)

    colors = [random.choice(COLORS_ON if overlaps_motive(image, c) else COLORS_OFF) for c in filtered_circles]

    draw_circles_parallel(draw_image, filtered_circles, colors)

    return image2


@app.route('/generate_plate', methods=['POST'])
def generate_plate():
    data = request.get_json()
    number = data.get('number', 1)
    print(f"Received number: {number}")
    image = generate_ishihara_plate(number)

    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
