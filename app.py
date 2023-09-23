from flask import Flask, render_template, Response, request, redirect, url_for
import cv2

app = Flask(__name__)

# Default mobile camera IP address and port
default_mobile_camera_ip = "http://192.168.2.21"
default_mobile_camera_port = 8080

# Flag to determine if the camera feed should be displayed
camera_updated = False

def mobile_camera(ip, port):
    # Capture the mobile camera feed using OpenCV
    cap = cv2.VideoCapture(f'{ip}:{port}/video')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame as a response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def index():
    global camera_updated
    return render_template('index.html', camera_updated=camera_updated, default_mobile_camera_ip=default_mobile_camera_ip, default_mobile_camera_port=default_mobile_camera_port)

@app.route('/update_ip', methods=['POST'])
def update_ip():
    global camera_updated, default_mobile_camera_ip, default_mobile_camera_port
    new_ip = request.form.get('new_ip')
    new_port = request.form.get('new_port')
    default_mobile_camera_ip = f"http://{new_ip}"
    default_mobile_camera_port = int(new_port)
    camera_updated = True
    return redirect(url_for('index'))

# SSE route to stream the video to the browser
@app.route('/video_feed')
def video_feed():
    return Response(mobile_camera(default_mobile_camera_ip, default_mobile_camera_port), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
