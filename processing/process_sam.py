import cv2
from .sam_inference import fast_sam
from utilities.create_dir import create_dir

def process_sam(save_path, index, roi):
  create_dir(f'images/{save_path}')
  
  PATH = f'./images/{save_path}/{index}.png'
  
  cv2.imwrite(PATH, roi)
  
  create_dir(f'sam_results/{save_path}')
  
  SAM_PATH = f'./sam_results/{save_path}/{index}.png'
  
  fast_sam(PATH, SAM_PATH)
  
  return cv2.imread(SAM_PATH)