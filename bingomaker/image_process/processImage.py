import io

from PIL import Image


def resize_image(fp, width: int = 128, height: int = 128):
    """
    Resize the image to the specified width and height.
    :param width: Target width of the image.
    :param height: Target height of the image.
    :return: Resized Image object.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers.")
    # if image isn't square raise a warning and resize to square
    image = Image.open(fp)
    if image.size[0] != image.size[1]:
        print("Warning: Image is not square. Resizing to square.")

    return image.resize((width, height))


def process_gif(fp) -> list[Image.Image]:
    """
    Process the GIF to extract all frames as RGBA images.
    :return: List of Image objects representing each frame.
    """
    gif = Image.open(fp)
    frames = []
    palette = gif.getpalette()  # Get the palette for the GIF if available

    try:
        while True:
            # Create a copy of the current frame
            new_frame = gif.copy()

            # Apply the palette if the frame is in 'P' mode
            if new_frame.mode == "P" and palette:
                new_frame.putpalette(palette)

            # Convert the frame to RGBA for consistent processing
            processed_frame = new_frame.convert("RGBA")
            frames.append(processed_frame)

            # Move to the next frame
            gif.seek(gif.tell() + 1)
    except EOFError:
        # End of the GIF, all frames processed
        pass

    return frames


def resize_frames(
    frames: list[Image.Image], width: int = 128, height: int = 128
) -> list[Image.Image]:
    """
    Resize the list of frames to the specified width and height.
    :param frames: List of Image objects representing each frame.
    :param width: Target width of the frames.
    :param height: Target height of the frames.
    :return: List of resized Image objects.
    """
    resized_frames = []

    for frame in frames:
        # High-quality resizing
        resized_frame = frame.resize((width, height), Image.Resampling.LANCZOS)
        resized_frames.append(resized_frame)

    return resized_frames


def combine_frames(frames: list[Image.Image]):
    """
    Combine the list of frames into a single GIF.
    :param frames: List of Image objects representing each frame.
    :fp : arbitrary file object
    """
    buffer = io.BytesIO()
    frames[0].save(buffer, "GIF", save_all=True, append_images=frames[1:], loop=0)
    return buffer


def resize_gif(fp, width: int = 128, height: int = 128):
    frames = process_gif(fp)
    resized_frames = resize_frames(frames, width, height)
    return combine_frames(resized_frames)
