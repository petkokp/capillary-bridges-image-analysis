from mobile_sam import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import torch
import numpy as np
import cv2

import numpy as np

def save_output(mask, output_path, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    cv2.imwrite(output_path, mask_image)

def mobile_sam(image, output_path):
  model_type = "vit_t"
  sam_checkpoint = "./weights/mobile_sam_weights/mobile_sam.pt"

  device = "cuda" if torch.cuda.is_available() else "cpu"

  mobile_sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
  mobile_sam.to(device=device)
  mobile_sam.eval()

  # bboxes=[[0, 0, 870, 930], [1100, 0, 2000, 950]])
  
  predictor = SamPredictor(mobile_sam)
  predictor.set_image(image)

  input_box = np.array([0, 0, 870, 930])

  masks, _, _ = predictor.predict(
      point_coords=None,
      point_labels=None,
      box=input_box[None, :],
      multimask_output=False,
  )
  
  save_output(masks[0], output_path)
