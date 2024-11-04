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
    print("Downloaded", os.path.getsize(output_path), "bytes")


def create_text_overlay(
    frame: np.ndarray, product_name: str, tagline: str, alpha: float = 1.0
) -> np.ndarray:
    """
    Create text overlay on a single frame with product name and tagline

    Args:
        frame: Input video frame
        product_name: Main text to overlay
        tagline: Secondary text to display below product name
        alpha: Opacity of text (0.0 to 1.0)

    Returns:
        Frame with text overlay
    """
    # Create a copy of the frame
    overlay = frame.copy()

    # Get frame dimensions
    height, width = frame.shape[:2]

    # Set text properties for product name
    font = cv2.FONT_HERSHEY_DUPLEX
    product_font_scale = min(width, height) / 180  # Scale font based on frame size
    product_thickness = max(4, int(product_font_scale * 3))

    # Set text properties for tagline (smaller size)
    tagline_font_scale = product_font_scale * 0.4  # Tagline is 60% of product name size
    tagline_thickness = max(2, int(tagline_font_scale * 2))

    # Get text sizes
    (product_width, product_height), product_baseline = cv2.getTextSize(
        product_name, font, product_font_scale, product_thickness
    )
    (tagline_width, tagline_height), tagline_baseline = cv2.getTextSize(
        tagline, font, tagline_font_scale, tagline_thickness
    )

    # Calculate vertical spacing between product name and tagline
    spacing = int(product_height * 0.5)  # 50% of product text height

    # Calculate text positions (center horizontally, stack vertically)
    product_x = (width - product_width) // 2
    tagline_x = (width - tagline_width) // 2

    # Position both texts vertically centered as a group
    total_height = product_height + spacing + tagline_height
    group_y = (height - total_height) // 2

    product_y = group_y + product_height
    tagline_y = product_y + spacing + tagline_height

    # Draw product name shadow (outline)
    shadow_color = (0, 0, 0)
    shadow_thickness = product_thickness + 2
    cv2.putText(
        overlay,
        product_name,
        (product_x, product_y),
        font,
        product_font_scale,
        shadow_color,
        shadow_thickness,
        cv2.LINE_AA,
    )

    # Draw product name main text
    cv2.putText(
        overlay,
        product_name,
        (product_x, product_y),
        font,
        product_font_scale,
        (255, 255, 255),
        product_thickness,
        cv2.LINE_AA,
    )

    # Draw tagline shadow (outline)
    tagline_shadow_thickness = tagline_thickness + 2
    cv2.putText(
        overlay,
        tagline,
        (tagline_x, tagline_y),
        font,
        tagline_font_scale,
        shadow_color,
        tagline_shadow_thickness,
        cv2.LINE_AA,
    )

    # Draw tagline main text
    cv2.putText(
        overlay,
        tagline,
        (tagline_x, tagline_y),
        font,
        tagline_font_scale,
        (255, 255, 255),
        tagline_thickness,
        cv2.LINE_AA,
    )

    # Blend the overlay with the original frame
    return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)


def add_text_overlay(video_url: str, product_name: str, tagline: str) -> Optional[str]:
    """
    Add centered text overlay to video and return path to processed video

    Args:
        video_url: URL of the input video
        product_name: Main text to overlay
        tagline: Secondary text to display below product name

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
        output_path = os.path.abspath(os.path.join(temp_dir, "output.webM"))

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
        fourcc = cv2.VideoWriter_fourcc("V", "P", "8", "0")
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
            frame_with_text = create_text_overlay(frame, product_name, tagline, alpha)

            # Write the frame
            out.write(frame_with_text)

            frame_count += 1
            if frame_count % fps == 0:  # Print progress every second
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}%")

        # Release resources
        cap.release()
        out.release()

        print("Processing complete!")
        return output_path

    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return None

    finally:
        # Clean up temporary directory
        pass


# Example usage:
if __name__ == "__main__":
    video_url = "YOUR_VIDEO_URL"
    product_name = "Your Product Name"
    tagline = "Your Amazing Tagline"
    output = add_text_overlay(video_url, product_name, tagline)
    if output:
        print(f"Video saved to: {output}")
    else:
        print("Video processing failed")
