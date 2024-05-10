from SAM_finetune.inference import inference_model
import cv2
import os

def sam_finetune(image, output_path):
  TEMP_IMG_PATH = 'temp.png'
  
  cv2.imwrite(TEMP_IMG_PATH, image)
  inference_model(TEMP_IMG_PATH, output_path, mask_path=None)
  
  os.remove(TEMP_IMG_PATH)