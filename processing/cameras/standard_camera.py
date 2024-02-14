import cv2
from camera import Camera

class StandardCamera(Camera):
  def __init__(self):
    self.camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    
  def record(self, process):
    _, frame = self.camera.read()
    
    img, results, values = process(frame, 0)
    
    process(img, 0)
    
  def release(self):
    self.camera.release()