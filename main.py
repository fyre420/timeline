import cv2
import os
from extract_col import get_most_similar_bucket, extract_top_dominant_colors_per_frame, get_most_popular_bucket, bias_colors
import shutil

def read_color_tuples_from_file(file_path):
	with open(file_path, 'r') as file:
		content = file.read()
		color_tuples = eval(content)
	return color_tuples



# Path to the input video file
video_path = 'videoplayback.mp4'

# Create a directory to store frames
output_dir = 'Frames'
os.makedirs(output_dir, exist_ok=True)

# Delete all files in the directory
shutil.rmtree(output_dir)

# Recreate the directory after deleting its contents
os.makedirs(output_dir)

# Open the video file
cap = cv2.VideoCapture(video_path)

# Get frames per second (fps) and total number of frames
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Calculate the number of frames for the first # 11 seconds
frames_to_extract = fps * 11

color_depth_bits = 8

# Calculate the maximum value for the reduced color depth
max_value = 2 ** color_depth_bits - 1

# Loop through frames and save them
for frame_number in range(frames_to_extract):
	ret, frame = cap.read()
	if not ret:
		break
	
	# Make frame 144p
	target_height = 144
	target_width = int(frame.shape[1] * (target_height / frame.shape[0]))
	resized_frame = cv2.resize(frame, (target_width, target_height))
	
	reduced_frame = (resized_frame // (256 // max_value)) * (256 // max_value)
	
	# Save the frame
	frame_filename = os.path.join(output_dir, f'frame_{frame_number:04d}.png')
	cv2.imwrite(frame_filename, reduced_frame)

# Release the video capture object
cap.release()

frame_colors = {}

# Get the most dominant 16 colors per frame and put them in frame_colors
for frame_number in range(frames_to_extract):
	frame_path = f'Frames/frame_{frame_number:04d}.png'
	top_colors = extract_top_dominant_colors_per_frame(frame_path, colors_per_frame=16)
	frame_colors[frame_path] = top_colors

BUCKETS_NUMBER = 256

 # read a text file and get the list of 256 tuples
distinct_colors = read_color_tuples_from_file('color_space.txt') 

# Create a dictionary with distinct colors as keys and initial counts as values
# this line took an embarrasingly long time (<3 python)
distinct_colors_dict = {t: 0 for t in distinct_colors}



# Calculate the closest bucket for each distinct color
bucket_mapping = {}
for distinct_color in distinct_colors:
	closest_bucket = get_most_similar_bucket(distinct_color, distinct_colors)
	bucket_mapping[distinct_color] = closest_bucket

# Iterate over frames and colors to update counts
for frame, colors in frame_colors.items():
	for color in colors:
		closest_bucket = bucket_mapping[get_most_similar_bucket(color, distinct_colors)]
		distinct_colors_dict[closest_bucket] += 1

#try to avoid greyish colors, the bias might be really extreme rn idk i cant really test it, it takes too long
bias_colors(distinct_colors_dict, colorfulness_bias=0.1)

print(distinct_colors_dict)

timeline_section = get_most_popular_bucket(distinct_colors_dict)
		
print(timeline_section)

# add code to add the color to the timeline