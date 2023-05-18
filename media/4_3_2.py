import cv2
import base64


filename = '/home/dcb/Desktop/dcb.png'
img = cv2.imread(filename)

text = base64.b64encode(cv2.imencode('.png',img)[1]).decode()

print(text)
