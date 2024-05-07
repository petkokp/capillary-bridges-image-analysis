import os
from FastSAM import fastsam
import torch

def fast_sam(image_path, output_path):
  HOME = os.getcwd()
  
  model = fastsam.FastSAM(f'{HOME}/weights/FastSAM.pt')

  device = "cuda" if torch.cuda.is_available() else "cpu"

  everything_results = model(image_path, device=device, retina_masks=True, conf=0.4, iou=0.9,)

  prompt_process = fastsam.FastSAMPrompt(image_path, everything_results, device=device)

  # everything prompt
  # ann = prompt_process.everything_prompt()

  # text prompt
  # ann = prompt_process.text_prompt(text='the two green objects on the sides of the image')
  
  # ann = prompt_process.point_prompt(points=[[620, 360]], pointlabel=[1])
  
  ann = prompt_process.box_prompt(bboxes=[[0, 0, 870, 930], [1100, 0, 2000, 950]])

  prompt_process.plot(annotations=ann, output_path=output_path)