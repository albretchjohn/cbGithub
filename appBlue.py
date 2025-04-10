import math
import random
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import io
import numpy as np
from scipy.spatial import cKDTree as cKDTree

app = Flask(__name__)

BACKGROUND = (255, 255, 255)
TOTAL_CIRCLES = 1500

color = lambda c: ((c >> 16) & 255, (c >> 8) & 255, c & 255)

COLORS_ON = [  # Blue shades for the number
    color(0x4A90E2),  # Light blue
    color(0x3478F6),  # Medium blue
    color(0x0057B8)   # Deep blue
]

COLORS_OFF = [  # Yellow/orange/green shades for the background
    color(0xFFD166),  # Yellow-orange
    color(0xFFB74D),  # Warm orange
    color(0xE8C547),  # Gold
    color(0xA7C957),  # Yellow-green
    color(0xD4A017)   # Darker yellow
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
    
    circles = []
    circle_positions = []
    
    # Generate first circle
    first_circle = generate_circle(width, height, min_diameter, max_diameter)
    circles.append(first_circle)
    circle_positions.append((first_circle[0], first_circle[1]))  # Only store (x, y) in KD-Tree
    circle_draw(draw_image, image, first_circle)
    
    # Create KD-Tree with first circle
    tree = cKDTree(circle_positions)  # Efficient lookup structure
    
    for _ in range(TOTAL_CIRCLES - 1):
        max_attempts = 50  # Avoid infinite loops
        
        for _ in range(max_attempts):
            circle = generate_circle(width, height, min_diameter, max_diameter)
            x, y, r = circle
            
            # Query KD-Tree for nearby circles
            nearby_indices = tree.query_ball_point((x, y), r * 2)
            if not nearby_indices:  # If no intersections, place the circle
                circles.append(circle)
                circle_positions.append((x, y))
                circle_draw(draw_image, image, circle)
                
                # Update KD-Tree with new circle
                tree = cKDTree(circle_positions)
                break  # Successfully placed circle, exit attempt loop
    
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
