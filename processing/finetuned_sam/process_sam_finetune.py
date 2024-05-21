import cv2
import os
from .sam_finetune_inference import sam_finetune
from utilities.create_dir import create_dir

def process_sam_finetune(save_path, index, roi):
  create_dir(f'images/{save_path}')
  
  PATH = f'./images/{save_path}/{index}.png'
  
  cv2.imwrite(PATH, roi)
  
  create_dir(f'sam_finetune_results/{save_path}')
  
  SAM_PATH = f'./sam_finetune_results/{save_path}/{index}.png'
  
  sam_finetune(roi, SAM_PATH)
  
  image = cv2.imread(SAM_PATH)
  
  os.remove(SAM_PATH)
  
  return image