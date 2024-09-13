import cv2
import numpy as np

def extract_hidden_video(steg_video_path, output_hidden_video_path, output_cover_video_path, width, height, frame_count):
    # Open the steganographic video
    steg_video = cv2.VideoCapture(steg_video_path)
    
    # Define the codec and create VideoWriter objects for hidden and cover videos
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    hidden_writer = cv2.VideoWriter(output_hidden_video_path, fourcc, 30, (width, height))
    cover_writer = cv2.VideoWriter(output_cover_video_path, fourcc, 30, (width, height))
    
    # Process each frame
    for _ in range(frame_count):
        ret, frame = steg_video.read()
        if not ret:
            break
        
        # Split the frame into the hidden video and cover video
        # Assuming the hidden video is stored in the least significant bit (LSB)
        cover_frame = frame & 0b11111100  # Clear the last 2 bits
        hidden_frame = frame & 0b00000011  # Keep only the last 2 bits

        # Shift the hidden bits to the most significant bit position
        hidden_frame = hidden_frame << 6
        
        # Combine hidden and cover frames to form the final videos
        cover_writer.write(cover_frame)
        hidden_writer.write(hidden_frame)
    
    # Release everything
    steg_video.release()
    hidden_writer.release()
    cover_writer.release()
    print("Extraction completed.")

# Example usage
steg_video_path = "C:/Users/Shabitha/Downloads/python/video/video_op1.mp4"
output_hidden_video_path = "C:/Users/Shabitha/Downloads/python/video/hidden_video1.avi"
output_cover_video_path = "C:/Users/Shabitha/Downloads/python/video/cover_video1.avi"
width = 640  # Update with actual width of your video
height = 360  # Update with actual height of your video
frame_count = 300  # Update with the number of frames in your video

extract_hidden_video(steg_video_path, output_hidden_video_path, output_cover_video_path, width, height, frame_count)
