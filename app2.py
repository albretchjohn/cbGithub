import math
import random
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import io
import numpy as np
from scipy.spatial import cKDTree as KDTree

app = Flask(__name__)

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


# Number generation part (unchanged)
def create_image_with_number(number):
    width, height = 800, 800
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    max_font_size = 600
    font_path = "C:/Windows/Fonts/arial.ttf"
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


# Circle generation and drawing part (unchanged)
def generate_circle(image_width, image_height, min_diameter, max_diameter):
    radius = random.triangular(min_diameter, max_diameter, max_diameter * 0.8 + min_diameter * 0.2) / 2
    angle = random.uniform(0, math.pi * 2)
    distance_from_center = random.uniform(0, image_width * 0.48 - radius)
    x = image_width * 0.5 + math.cos(angle) * distance_from_center
    y = image_height * 0.5 + math.sin(angle) * distance_from_center
    return x, y, radius


def overlaps_motive(image, circle):
    x, y, r = circle
    points_x = [x, x, x, x - r, x + r, x - r * 0.93, x - r * 0.93, x + r * 0.93, x + r * 0.93]
    points_y = [y, y - r, y + r, y, y, y + r * 0.93, y - r * 0.93, y + r * 0.93, y - r * 0.93]

    for xy in zip(points_x, points_y):
        if image.getpixel(xy)[:3] != BACKGROUND:
            return True
    return False


def circle_intersection(circle1, circle2):
    x1, y1, r1 = circle1
    x2, y2, r2 = circle2
    return (x2 - x1) ** 2 + (y2 - y1) ** 2 < (r2 + r1) ** 2


def circle_draw(draw_image, image, circle):
    fill_colors = COLORS_ON if overlaps_motive(image, circle) else COLORS_OFF
    fill_color = random.choice(fill_colors)
    x, y, r = circle
    draw_image.ellipse((x - r, y - r, x + r, y + r), fill=fill_color, outline=fill_color)


def generate_ishihara_plate(number):
    image = create_image_with_number(number)
    image2 = Image.new('RGB', image.size, BACKGROUND)
    draw_image = ImageDraw.Draw(image2)
    width, height = image.size
    min_diameter = (width + height) / 200
    max_diameter = (width + height) / 75
    circles = [generate_circle(width, height, min_diameter, max_diameter)]
    circle_draw(draw_image, image, circles[0])
    for _ in range(TOTAL_CIRCLES - 1):
        circle = generate_circle(width, height, min_diameter, max_diameter)
        while any(circle_intersection(circle, circle2) for circle2 in circles):
            circle = generate_circle(width, height, min_diameter, max_diameter)
        circles.append(circle)
        circle_draw(draw_image, image, circle)
    return image2


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
