import cv2
import time
from processing.process_image import process_image
from utilities.create_dir import create_dir

MODEL = "NAIVE"

def process_realtime(CAM_INDEX):
  count = 0

  cap = cv2.VideoCapture(CAM_INDEX)

  prev_frame_time = 0

  # used to record the time at which we processed current frame 
  new_frame_time = 0

  RESULTS_PATH = 'realtime'

  create_dir(RESULTS_PATH)

  while True:
      ret, frame = cap.read()
      
      if frame is not None:
        img, results = process_image(frame, count + 1, RESULTS_PATH, MODEL)
        
        # font which we will be using to display FPS 
        font = cv2.FONT_HERSHEY_SIMPLEX 
        # time when we finish processing for this frame 
        new_frame_time = time.time() 
      
        # Calculating the fps 
      
        # fps will be number of frame processed in given time frame 
        # since their will be most of time error of 0.001 second 
        # we will be subtracting it to get more accurate result 
        fps = 1/(new_frame_time-prev_frame_time) 
        prev_frame_time = new_frame_time 
      
        # converting the fps into integer 
        fps = int(fps) 
      
        # converting the fps to string so that we can display it on frame 
        # by using putText function 
        print('fps: ', fps)
        fps = str(fps) 
      
        # putting the FPS count on the frame 
        cv2.putText(frame, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
        
        # cv2.imshow('Webcam Feed', img)
        return img

      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

  cap.release()
  cv2.destroyAllWindows()
