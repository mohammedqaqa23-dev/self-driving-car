import cv2
import numpy as np
import socketio
import eventlet
from flask import Flask
from io import BytesIO
import base64
from PIL import Image

# إعداد السيرفر للاتصال بالمحاكي
sio = socketio.Server()
app = Flask(__name__)

def process_image(img):
    # 1. تحويل الصورة لرمادي (Grayscale)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) [cite: 7]
    # 2. تقليل الضوضاء (Blur) وتطبيق Canny Edge Detection
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150) [cite: 8]
    # 3. تحويل الحواف لخطوط باستخدام Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, maxLineGap=50) [cite: 8]
    return lines

@sio.on('telemetry')
def telemetry(sid, data):
    if data:
        # استقبال الصورة من المحاكي
        image = Image.open(BytesIO(base64.b64decode(data["image"])))
        image = np.asarray(image)
        
        # معالجة الصورة واتخاذ قرار التوجيه
        lines = process_image(image)
        steering_angle = 0.0 # هنا بنحسب الزاوية بناءً على الخطوط [cite: 9]
        throttle = 0.1       # سرعة السيارة [cite: 17]
        
        send_control(steering_angle, throttle)

def send_control(steering_angle, throttle):
    sio.emit("steer", data={
        'steering_angle': steering_angle.__str__(),
        'throttle': throttle.__str__()
    })

if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
