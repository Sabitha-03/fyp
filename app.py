import streamlit as st
import cv2
import os
import os.path as osp
from PIL import Image

class FrameExtractor:
    def __init__(self, video_file, output_dir, frame_ext='.jpg'):
        if osp.exists(video_file):
            self.video_file = video_file
        else:
            raise FileExistsError(f'Video file {video_file} does not exist.')

        self.output_dir = output_dir
        if not osp.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.frame_ext = frame_ext
        self.video = cv2.VideoCapture(self.video_file)
        self.video_fps = self.video.get(cv2.CAP_PROP_FPS)
        self.video_length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

    def extract(self):
        success, frame = self.video.read()
        frame_cnt = 0
        while success:
            yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv_frame)
            self.save_yuv_components(y, u, v, frame_cnt)
            success, frame = self.video.read()
            frame_cnt += 1

    def save_yuv_components(self, y, u, v, frame_cnt):
        y_filename = osp.join(self.output_dir, "{:08d}_Y{}".format(frame_cnt, self.frame_ext))
        u_filename = osp.join(self.output_dir, "{:08d}_U{}".format(frame_cnt, self.frame_ext))
        v_filename = osp.join(self.output_dir, "{:08d}_V{}".format(frame_cnt, self.frame_ext))
        cv2.imwrite(y_filename, y)
        cv2.imwrite(u_filename, u)
        cv2.imwrite(v_filename, v)

# Streamlit frontend
def main():
    st.title("Video Frame Extractor")
    uploaded_video = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
    frame_ext = st.selectbox("Choose frame extension", ['.jpg', '.png'])

    if uploaded_video:
        st.video(uploaded_video)

        # Set up the output directory
        output_dir = 'extracted_frames'
        if st.button('Extract Frames'):
            # Save uploaded video to a temp file
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_video.read())

            # Extract frames
            extractor = FrameExtractor(video_file="temp_video.mp4", output_dir=output_dir, frame_ext=frame_ext)
            extractor.extract()
            st.success("Frames extracted successfully!")

            # Display extracted frames
            frame_files = os.listdir(output_dir)
            for file in frame_files:
                if file.endswith(frame_ext):
                    img = Image.open(osp.join(output_dir, file))
                    st.image(img, caption=file)

if __name__ == '__main__':
    main()
