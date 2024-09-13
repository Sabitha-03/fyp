import cv2
import numpy as np
import os
import os.path as osp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tqdm import tqdm
import argparse
import math

# Define video and frame supported formats
supported_video_ext = ('.avi', '.mp4', '.yuv')
supported_frame_ext = ('.jpg', '.png')

def encrypt_frame(frame, key):
    """Encrypts a frame using AES CBC mode."""
    cipher = AES.new(key, AES.MODE_CBC)
    # Convert frame to bytes
    frame_bytes = frame.tobytes()
    # Encrypt frame bytes and return
    return cipher.encrypt(pad(frame_bytes, AES.block_size))

def embed_lsb(cover_block, secret_data):
    """Embeds secret data (encrypted) into cover block using LSB."""
    cover_flat = cover_block.flatten()
    secret_flat = np.frombuffer(secret_data, dtype=np.uint8)

    # Embed the secret data into the LSB of the cover frame
    for i in range(len(secret_flat)):
        cover_flat[i] = (cover_flat[i] & 0xFE) | (secret_flat[i] & 0x01)

    return cover_flat.reshape(cover_block.shape)

def assemble_video_from_frames(frame_directory, output_video_path, fps):
    """Assembles frames into a video file."""
    frame_files = sorted([osp.join(frame_directory, f) for f in os.listdir(frame_directory) if f.endswith(('.jpg', '.png'))])
    frame = cv2.imread(frame_files[0])
    height, width, layers = frame.shape

    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame_file in tqdm(frame_files, desc="Assembling video"):
        frame = cv2.imread(frame_file)
        video_out.write(frame)

    video_out.release()
    print(f"Video saved to {output_video_path}")

class FrameExtractor:
    def __init__(self, video_file, output_dir, frame_ext='.jpg', sampling=-1, convert_yuv=False):
        """Extract frames from video file and save them under a given output directory."""
        if not osp.exists(output_dir):
            os.makedirs(output_dir)  # Ensure directory creation
        if osp.exists(video_file):
            self.video_file = video_file
        else:
            raise FileExistsError(f'Video file {video_file} does not exist.')
        self.sampling = sampling
        self.output_dir = output_dir
        self.frame_ext = frame_ext if frame_ext in supported_frame_ext else '.jpg'
        self.convert_yuv = convert_yuv
        self.video = cv2.VideoCapture(self.video_file)
        self.video_fps = self.video.get(cv2.CAP_PROP_FPS)
        self.video_length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.sampling != -1:
            self.video_length = self.video_length // self.sampling

    def extract(self):
        success, frame = self.video.read()
        frame_cnt = 0
        while success:
            if self.convert_yuv:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            filename = osp.join(self.output_dir, "{:08d}{}".format(frame_cnt, self.frame_ext))
            cv2.imwrite(filename, frame)
            success, frame = self.video.read()
            frame_cnt += 1 if self.sampling == -1 else math.ceil(self.sampling * self.video_fps)
            if self.sampling != -1:
                self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_cnt)

def main():
    parser = argparse.ArgumentParser("Steganography in Video")
    parser.add_argument('--cover_video', type=str, help='Path to the cover video')
    parser.add_argument('--secret_video', type=str, help='Path to the secret video')
    parser.add_argument('--output_video', type=str, default='video_out.mp4', help='Path to save the steganographed video')
    args = parser.parse_args()

    # AES encryption key
    key = b'1234567890abcdef'  # 16-byte AES key
    
    # Step 1: Extract frames from both cover and secret videos
    cover_frames_dir = 'cover_frames'
    secret_frames_dir = 'secret_frames'
    
    # Extract cover video frames
    cover_extractor = FrameExtractor(args.cover_video, cover_frames_dir, convert_yuv=False)
    cover_extractor.extract()

    # Check if cover frames directory has been populated
    if not os.listdir(cover_frames_dir):
        raise FileNotFoundError(f"No frames extracted from cover video. Check the video format: {args.cover_video}")
    
    # Extract secret video frames
    secret_extractor = FrameExtractor(args.secret_video, secret_frames_dir, convert_yuv=False)
    secret_extractor.extract()

    # Check if secret frames directory has been populated
    if not os.listdir(secret_frames_dir):
        raise FileNotFoundError(f"No frames extracted from secret video. Check the video format: {args.secret_video}")

    # Step 2: Encrypt secret frames and embed them into cover frames
    cover_frame_files = sorted(os.listdir(cover_frames_dir))
    secret_frame_files = sorted(os.listdir(secret_frames_dir))
    
    # Directory for stego frames
    stego_frames_dir = 'stego_frames'
    if not osp.exists(stego_frames_dir):
        os.makedirs(stego_frames_dir)

    for i, (cover_frame_file, secret_frame_file) in enumerate(tqdm(zip(cover_frame_files, secret_frame_files), desc="Processing frames")):
        cover_frame = cv2.imread(osp.join(cover_frames_dir, cover_frame_file))
        secret_frame = cv2.imread(osp.join(secret_frames_dir, secret_frame_file))

        # Encrypt the secret frame as bytes
        encrypted_frame = encrypt_frame(secret_frame, key)

        # Embed the encrypted secret frame bytes into the cover frame using LSB
        embedded_frame = embed_lsb(cover_frame, encrypted_frame)

        # Save the embedded frame
        embedded_frame_filename = osp.join(stego_frames_dir, "{:08d}.jpg".format(i))
        cv2.imwrite(embedded_frame_filename, embedded_frame)

    # Step 3: Reassemble video from stego frames
    video_fps = cover_extractor.video_fps
    assemble_video_from_frames(stego_frames_dir, args.output_video, video_fps)

if __name__ == '__main__':
    main()
