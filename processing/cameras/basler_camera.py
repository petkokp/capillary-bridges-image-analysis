import cv2
from pypylon import pylon
from camera import Camera

class BaslerCamera(Camera):
  def __init__(self):
    self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    
  def record(self, process):
    converter = pylon.ImageFormatConverter()

    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    
    while self.camera.IsGrabbing():
        grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)  
        
        if grabResult.GrabSucceeded():
          image = converter.Convert(grabResult)
          frame = image.GetArray()
          
          img, results, values = process(frame, 0)
          
          cv2.namedWindow('title', cv2.WINDOW_NORMAL)
          cv2.imshow('title', img)
          k = cv2.waitKey(1)
          if k == 27:
              break
            
        grabResult.Release()
        
  def release(self):
    self.camera.StopGrabbing()
