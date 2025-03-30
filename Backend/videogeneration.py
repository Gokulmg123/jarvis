import cv2
import os

image_folder = "Data\images"  # Folder containing images
video_name = "output.mp4"
fps = 3  # Frames per second

images = sorted([img for img in os.listdir(image_folder) if img.endswith(".jpg")])

# Read first image to get dimensions
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

# Define video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec
video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

# Add images to video
for image in images:
    frame = cv2.imread(os.path.join(image_folder, image))
    video.write(frame)

video.release()
cv2.destroyAllWindows()

print("Video saved as", video_name)
