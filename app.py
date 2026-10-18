import os
import subprocess
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://destav1.github.io"])

app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024


@app.get("/")
def home():
    return jsonify({
        "service": "DestaV1 FFmpeg Backend",
        "status": "online"
    })

@app.post("/process")
def process_video():
    if "video" not in request.files:
        return jsonify({"error": "Upload file dengan nama video"}), 400

    video = request.files["video"]
    method = request.form.get("method", "")

    if method not in ("itscale2", "itscale6"):
        return jsonify({"error": "Pilih itscale2 atau itscale6"}), 400

    if not video.filename:
        return jsonify({"error": "Nama file kosong"}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "output.mp4")
        video.save(input_path)

        scale = "2" if method == "itscale2" else "6"

        command = [
            "ffmpeg", "-y",
            "-itsscale", scale,
            "-i", input_path,
            "-c:v", "copy",
            "-c:a", "copy",
            "-movflags", "+faststart",
            output_path
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=900
        )

        if result.returncode != 0 or not os.path.exists(output_path):
            return jsonify({
                "error": "Pemrosesan gagal",
                "details": result.stderr[-2000:]
            }), 500

        return send_file(
            output_path,
            as_attachment=True,
            download_name="DestaV1_ITSCALE.mp4",
            mimetype="video/mp4"
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
