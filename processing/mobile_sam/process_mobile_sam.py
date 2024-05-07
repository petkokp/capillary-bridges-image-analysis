import cv2
from .mobile_sam_inference import mobile_sam
from utilities.create_dir import create_dir

def process_mobile_sam(save_path, index, roi):
  create_dir(f'images/{save_path}')
  
  PATH = f'./images/{save_path}/{index}.png'
  
  cv2.imwrite(PATH, roi)
  
  create_dir(f'mobile_sam_results/{save_path}')
  
  SAM_PATH = f'./mobile_sam_results/{save_path}/{index}.png'
  
  mobile_sam(roi, SAM_PATH)
  
  return cv2.imread(SAM_PATH)