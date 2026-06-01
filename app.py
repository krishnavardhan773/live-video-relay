from flask import Flask, Response, stream_with_context
import subprocess

app = Flask(__name__)

STREAM_URL = "https://d1rznlx03muoan.cloudfront.net/v1/manifest/9d43eacaed199f8d5883927e7aef514a8a08e108/ETV_HD_H264_cloud_in/363f3fdf-5239-42e5-9d36-b3f77a8bd8af/3.m3u8"

def generate_live_stream():
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-i", STREAM_URL,
            "-c:v", "copy",
            "-c:a", "copy",
            "-f", "mpegts",
            "pipe:1"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=10**6
    )

    try:
        while True:
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            yield chunk
    finally:
        process.kill()

@app.route("/")
def home():
    return f"""
    Video service running.

    Stream Source:
    {STREAM_URL}

    Live endpoint:
    /live
    """
@app.route("/live")
def live():
    return Response(
        stream_with_context(generate_live_stream()),
        mimetype="video/mp2t"
    )


@app.route("/player")
def player():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Video Player</title>
        <script src="https://cdn.jsdelivr.net/npm/mpegts.js@1.7.3/dist/mpegts.min.js"></script>
    </head>
    <body>
        <h2>Live Video Stream</h2>

        <video id="video" controls autoplay muted style="width: 90%; max-width: 900px;"></video>

        <script>
            if (mpegts.getFeatureList().mseLivePlayback) {
                var videoElement = document.getElementById('video');

                var player = mpegts.createPlayer({
                    type: 'mpegts',
                    isLive: true,
                    url: '/live'
                });

                player.attachMediaElement(videoElement);
                player.load();
                player.play();
            } else {
                document.body.innerHTML += "<p>Your browser does not support MPEG-TS playback.</p>";
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, threaded=True)
