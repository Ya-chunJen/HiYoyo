from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import tank
import cv2
import base64

app = Flask(__name__)

class VideoCamera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(1) 
    
    def __del__(self):
        self.cap.release()
    
    def get_frame(self):
        success, image = self.cap.read()
        if success:
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
      
# 定义四个路由，与四个按钮对应，并将其连接到相应的函数
@app.route('/forward', methods=['GET', 'POST'])
def forward():
    tank.right_motor(1,100)
    tank.left_motor(1,100)
    return "向前"

@app.route('/backup', methods=['GET', 'POST'])
def backup():
    tank.right_motor(2,100)
    tank.left_motor(2,100)
    return "向后"

@app.route('/turnleft', methods=['GET', 'POST'])
def turnleft():
    tank.right_motor(1,100)
    tank.left_motor(0,100)
    return "左转"


@app.route('/turnright', methods=['GET', 'POST'])
def turnright():
    tank.right_motor(1,100)
    tank.left_motor(0,100)
    return "右转"

@app.route('/stop', methods=['GET', 'POST'])
def stop():
    tank.right_motor(0,100)
    tank.left_motor(0,100)
    return "停止"

# 定义一个默认路由，将其连接到一个 HTML 文件，其中包含四个按钮和相应的 JavaScript 代码
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()
