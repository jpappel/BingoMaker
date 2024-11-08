import json
import random

from flask import Flask, jsonify, render_template, request

from data.disk_reader import read_text
from data.serialization import BoardEncoder
from game.game import Board


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return render_template("index.html")

    @app.route("/bingocard/<tilepoolId>")
    def generate_card(tilepoolId):
        size = request.args.get("size", 5, type=int)
        seed = request.args.get("seed", random.randint(0, 1 << 8), type=int)
        # excluded_tags = request.args.get("excluded_tags")
        board = Board(read_text("nouns"), size=size, free_square=False, seed=seed)
        board.id = str(tilepoolId)
        # HACK: serializing and deserializing is done to use jsonify on a dict
        return jsonify(json.loads(json.dumps(board, cls=BoardEncoder)))

    return app
