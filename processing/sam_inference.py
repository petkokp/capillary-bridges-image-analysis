import os
from FastSAM import fastsam
import torch
import numpy as np

def fast_sam(image_path, output_path, image):
  HOME = os.getcwd()
  
  model = fastsam.FastSAM(f'{HOME}/weights/FastSAM.pt')

  device = "cuda" if torch.cuda.is_available() else "cpu"

  everything_results = model(image_path, device=device, retina_masks=True, conf=0.4, iou=0.9,)

  prompt_process = fastsam.FastSAMPrompt(image_path, everything_results, device=device)
  
  height, width, _ = image.shape
  
  x_left = width - (width - 50)
  x_right = width - 50
  y = (height / 2) + 50
  
  points = np.array([[x_left, y], [x_right, y]])
  input_label = np.array([1, 1])
  
  ann = prompt_process.point_prompt(points=points, pointlabel=input_label)

  prompt_process.plot(annotations=ann, output_path=output_path)