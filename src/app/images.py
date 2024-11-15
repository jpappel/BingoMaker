from flask import Blueprint, current_app, request

from images.manager import ImageManager

bp = Blueprint("images", __name__)


@bp.post("/images/upload")
def upload():
    man: ImageManager = current_app.config["IMAGES"]
    # TODO: call image filter
    # TODO: save file
    file = request.files["file"]
    man.add_image(file)
    return ""
