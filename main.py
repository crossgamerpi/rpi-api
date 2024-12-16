from flask import Flask, Response
import glob
import cv2

class cameras():
    def __init__(self):
        self.camera_indexes = []
        self.cameras = []

    def init_cameras(self):
        self.camera_indexes = []
        for video in glob.glob("/dev/video*"):
            index = int(video.split("video")[1])
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                self.camera_indexes.append(index)
            cap.release()

        self.cameras = {index: cv2.VideoCapture(index) for index in self.camera_indexes}

    def get_camera(self, index):
        if index not in self.camera_indexes:
            return None
        return self.cameras[index]

    def stream_video(self, index):
        camera = self.cameras[index]
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def release(self):
        for index in self.camera_indexes:
            self.cameras[index].release()

app = Flask(__name__)
CAMERAS = cameras()

@app.route('/')
def index():
    CAMERAS.init_cameras()
    html = ""
    for camera_index in CAMERAS.camera_indexes:
        html += f'<a href="video_feed/{camera_index}" target="_self" style="float:left">' + \
                f'  <img src="video_feed/{camera_index}" alt="Flujo de Video" style="width: 100%; max-width: 640px; border: 2px solid black;">' + \
                f'</a>'
    return html

@app.route('/video_feed/<int:camera_index>')
def video_feed(camera_index):
    return Response(CAMERAS.stream_video(camera_index), mimetype='multipart/x-mixed-replace; boundary=frame')

def cleanup(exception=None):
    CAMERAS.release()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)