from moviepy.editor import VideoFileClip
import cv2
import numpy as np
import os
import tempfile
import requests
import uuid
from typing import Optional


def download_video(url: str, output_path: str) -> None:
    """Download video from URL to local file"""
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def create_text_overlay(frame: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
    """
    Create text overlay on a single frame

    Args:
        frame: Input video frame
        text: Text to overlay
        alpha: Opacity of text (0.0 to 1.0)

    Returns:
        Frame with text overlay
    """
    # Create a copy of the frame
    overlay = frame.copy()

    # Get frame dimensions
    height, width = frame.shape[:2]

    # Set text properties
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = min(width, height) / 500  # Scale font based on frame size
    thickness = max(4, int(font_scale * 3))

    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )

    # Calculate text position (center)
    text_x = (width - text_width) // 2
    text_y = (height + text_height) // 2

    # Draw text shadow (outline)
    shadow_color = (0, 0, 0)
    shadow_thickness = thickness + 2
    cv2.putText(
        overlay,
        text,
        (text_x, text_y),
        font,
        font_scale,
        shadow_color,
        shadow_thickness,
        cv2.LINE_AA,
    )

    # Draw main text
    cv2.putText(
        overlay,
        text,
        (text_x, text_y),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )

    # Blend the overlay with the original frame
    return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)


def add_text_overlay(video_url: str, product_name: str) -> Optional[str]:
    """
    Add centered text overlay to video and return path to processed video

    Args:
        video_url: URL of the input video
        product_name: Text to overlay on video

    Returns:
        Path to processed video file or None if processing fails
    """
    # Create unique temporary directory path
    temp_dir = os.path.join(
        tempfile.gettempdir(), f"video_processing_{uuid.uuid4().hex}"
    )

    try:
        # Ensure temp directory exists
        os.makedirs(temp_dir, exist_ok=True)

        # Use absolute paths for all files
        input_path = os.path.abspath(os.path.join(temp_dir, "input.mp4"))
        output_path = os.path.abspath(os.path.join(temp_dir, "output.mp4"))

        # Download video
        print("Downloading video...")
        download_video(video_url, input_path)

        # Open the video file
        cap = cv2.VideoCapture(input_path)

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Process each frame
        print("Processing frames...")
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Calculate fade effect (fade in first second, fade out last second)
            frame_position = frame_count / total_frames
            if frame_count < fps:  # Fade in
                alpha = frame_count / fps
            elif frame_count > total_frames - fps:  # Fade out
                alpha = (total_frames - frame_count) / fps
            else:  # Full opacity
                alpha = 1.0

            # Add text overlay
            frame_with_text = create_text_overlay(frame, product_name, alpha)

            # Write the frame
            out.write(frame_with_text)

            frame_count += 1
            if frame_count % fps == 0:  # Print progress every second
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}%")

        # Release resources
        cap.release()
        out.release()

        # Copy audio from original to new video
        print("Adding audio...")
        try:
            # Load original video with MoviePy to get audio
            original_video = VideoFileClip(input_path)
            # Load the new video we created
            new_video = VideoFileClip(output_path)

            if original_video.audio is not None:
                # Create final video with original audio
                final_output = os.path.abspath(
                    os.path.join(temp_dir, "final_output.mp4")
                )
                new_video.set_audio(original_video.audio).write_videofile(
                    final_output, codec="libx264", audio_codec="aac"
                )
                # Clean up
                original_video.close()
                new_video.close()
                # Use the final output as our result
                output_path = final_output
            else:
                print("Original video has no audio track")

        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            print("Continuing with video-only output")

        print("Processing complete!")
        return output_path

    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return None

    finally:
        # Clean up temporary directory
        try:
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary directory: {str(e)}")


# Example usage:
if __name__ == "__main__":
    video_url = "YOUR_VIDEO_URL"
    product_name = "Your Product Name"
    output = add_text_overlay(video_url, product_name)
    if output:
        print(f"Video saved to: {output}")
    else:
        print("Video processing failed")
