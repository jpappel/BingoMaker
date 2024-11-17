import os
from urllib import parse

from flask import Blueprint, current_app, redirect, request, send_file

from images.image_manager import ImageInfo, ImageManager

bp = Blueprint("images", __name__)


@bp.post("/images")
def upload():
    if "file" not in request.files:
        return "Missing file", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    manager: ImageManager = current_app.config["IMAGES"]
    info: ImageInfo = {"mimetype": file.mimetype, "size": file.content_length}
    id_ = manager.add_image(file, info)

    return id_


@bp.get("/images/<image_id>")
def get_image(image_id: str):
    manager: ImageManager = current_app.config["IMAGES"]
    try:
        uri = manager.get_image(image_id)
    except FileNotFoundError:
        return "", 404

    parsed = parse.urlparse(uri)
    if parsed.scheme != "file":
        return redirect(uri)

    path = parse.unquote(parsed.path)

    if not os.path.isfile(path):
        return "", 404

    return send_file(path)


@bp.post("/images/<image_id>/confirm")
def adjust_counts(image_id: str):
    manager: ImageManager = current_app.config["IMAGES"]
    try:
        manager.confirm_image(image_id)
    except KeyError:
        return "Image not found", 404
    count = manager.references[image_id]
    return {"confirmed": count.confirmed, "unconfirmed": count.unconfirmed}


@bp.post("/images/<image_id>/unconfirm")
def delete(image_id: str):
    manager: ImageManager = current_app.config["IMAGES"]
    try:
        manager.deref_image(image_id)
    except KeyError:
        return "Image not found", 404
    count = manager.references[image_id]
    return {"confirmed": count.confirmed, "unconfirmed": count.unconfirmed}
