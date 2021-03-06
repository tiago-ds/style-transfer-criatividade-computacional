import os

from flask import Flask, request, abort, jsonify, send_from_directory
from flask_cors import CORS

from kpopify import kpopify as stilyze

UPLOAD_DIRECTORY = "./api_files/"
EXPORT_DIRECTORY = "./results/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api = Flask("kpopifier")
CORS(api)

@api.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    return send_from_directory(EXPORT_DIRECTORY, path, as_attachment=True)


@api.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""
    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories allowed")

    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)

    # Return 201 CREATED
    return "OK", 201


@api.route('/kpopify/<filename>/<genre>')
def kpopify(filename, genre):
    """Transforms the music"""
    stilyze.kpopify(filename, genre)
    return "OK", 200

def get_webservice():
    return api

if __name__ == "__main__":
    api.run(debug=True, port=8000)
