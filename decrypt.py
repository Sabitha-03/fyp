import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_aes_video(encrypted_video_path, output_video_path, key, width, height, frame_count):
    # Open the binary file with the encrypted data
    with open(encrypted_video_path, 'rb') as encrypted_file:
        
        # Initialize the video writer to save the decrypted video
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        decrypted_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (width, height))

        if not decrypted_writer.isOpened():
            print("Error: Could not open the video writer.")
            return

        for frame_index in range(frame_count):
            # Read the IV (first 16 bytes) and the encrypted frame data
            iv = encrypted_file.read(16)
            encrypted_frame_bytes = encrypted_file.read(width * height * 3 + AES.block_size)
            
            if not iv or not encrypted_frame_bytes:
                print(f"Error: Failed to read frame {frame_index}.")
                break
            
            # Initialize the AES cipher for decryption using the extracted IV
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            try:
                # Decrypt the encrypted frame bytes and remove padding
                decrypted_frame_bytes = unpad(cipher.decrypt(encrypted_frame_bytes), AES.block_size)
            except ValueError as e:
                print(f"Error: Decryption failed at frame {frame_index}: {str(e)}")
                break
            
            # Convert the decrypted bytes back into a numpy array (frame)
            try:
                decrypted_frame = np.frombuffer(decrypted_frame_bytes, dtype=np.uint8).reshape(height, width, 3)
            except ValueError as e:
                print(f"Error: Could not reshape decrypted frame {frame_index}: {str(e)}")
                continue
            
            # Write the decrypted frame to the output video
            decrypted_writer.write(decrypted_frame)
    
    # Release the video writer
    decrypted_writer.release()
    print("Decryption completed.")

# Example usage
encrypted_video_path = "C:/Users/Shabitha/Downloads/python/video/hidden_Video1.bin"  # This is the encrypted video file
output_video_path = "C:/Users/Shabitha/Downloads/python/video/de_video.avi"  # This will be the decrypted video
key = b'1234567890abcdef'  # Same 16-byte AES key used for encryption
width = 640  # Width of your video
height = 360  # Height of your video
frame_count = 300  # Number of frames in your video

decrypt_aes_video(encrypted_video_path, output_video_path, key, width, height, frame_count)
