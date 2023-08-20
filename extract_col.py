from colorthief import ColorThief
import numpy as np
import distinctipy
from sklearn.metrics import pairwise_distances_argmin_min

def color_difference(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    distance = (r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2
    return distance

def calculate_colorfulness(color):
	r, g, b = color
	return (r - g)**2 + (g - b)**2 + (b - r)**2

def bias_colors(distinct_colors_dict, colorfulness_bias=0.1):
    for color, frequency in distinct_colors_dict.items():
        colorfulness = calculate_colorfulness(color)
        
        # Adjust the frequency based on colorfulness and the provided bias factor
        adjusted_frequency = frequency * (1 + colorfulness * colorfulness_bias)
        
        # Update the frequency in the dictionary
        distinct_colors_dict[color] = adjusted_frequency
    

def build_color_buckets(bucket_count, distinct_colors):
	buckets = [[] for _ in range(bucket_count)]
	for color in distinct_colors:
		closest_bucket = np.argmin(np.linalg.norm(np.array(buckets) - color, axis=2))
		buckets[closest_bucket].append(color)
	return buckets

def get_most_similar_bucket(color, buckets):
    min_distance = float('inf')
    closest_color = None
    
    for other_color in buckets:
        distance = color_difference(color, other_color)
        if distance < min_distance:
            min_distance = distance
            closest_color = other_color
            
    return closest_color

def get_most_popular_bucket(distinct_colors_dict):
    most_popular_color = max(distinct_colors_dict, key=distinct_colors_dict.get)
    return most_popular_color
			

def match_color_to_bucket(color, color_buckets):
	distances = pairwise_distances_argmin_min([color], color_buckets)[1]
	closest_bucket = np.argmin(distances)
	return closest_bucket

def extract_top_dominant_colors_per_frame(im_path, quality=1, colors_per_frame=16):
	# Create a ColorThief object
	color_thief = ColorThief(im_path)
	if colors_per_frame == 1:
		return [color_thief.get_color(10)]
	# Path pattern for frame files
	top_colors = color_thief.get_palette(color_count=colors_per_frame, quality=quality)
	return top_colors

def create_color_buckets(bucket_count):
	colors = [(0, 0, 0), (1, 1, 1)]  # Initialize with black and white

	# Get additional distinct colors from distinctipy
	additional_colors = distinctipy.get_colors(bucket_count - len(colors))
	
	# Extend the list of colors with additional distinct colors
	colors.extend(additional_colors)
	
	# Scale and round down each value in every tuple
	scaled_colors = [(int(value * 256) if value < 1 else 255) for color in colors for value in color]
	
	return [(scaled_colors[i], scaled_colors[i+1], scaled_colors[i+2]) for i in range(0, len(scaled_colors), 3)]



