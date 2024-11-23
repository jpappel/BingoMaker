import io

import pytest
from PIL import Image

from bingomaker.image_process import resize_gif, resize_image


@pytest.fixture
def large_image() -> io.BytesIO:
    buffer = io.BytesIO()
    image = Image.new("RGB", (1024, 1024), color="white")
    image.save(buffer, "JPEG")
    return buffer


@pytest.fixture
def small_image() -> io.BytesIO:
    buffer = io.BytesIO()
    image = Image.new("RGB", (50, 50), color="white")
    image.save(buffer, "JPEG")
    return buffer


@pytest.fixture
def gif() -> io.BytesIO:
    buffer = io.BytesIO()
    frames: list[Image.Image] = []
    for _ in range(5):
        frames.append(Image.new("RGB", (1024, 1024), color="white"))

    frames[0].save(buffer, format="GIF", save_all=True, append_images=frames[1:])

    return buffer


def test_resize_large_image(large_image: io.BytesIO):
    img = resize_image(large_image)
    assert img.size == (128, 128)


def test_resize_large_to_medium(large_image: io.BytesIO):
    img = resize_image(large_image, 512, 512)
    assert img.size == (512, 512)


def test_resize_small_image(small_image: io.BytesIO):
    img = resize_image(small_image)
    assert img.size == (128, 128)


def test_resize_small_to_medium(small_image: io.BytesIO):
    img = resize_image(small_image, 512, 512)
    assert img.size == (512, 512)


def test_resize_gif(gif: io.BytesIO):
    img = Image.open(resize_gif(gif))
    assert img.size == (128, 128)
    assert img.format == "GIF"
