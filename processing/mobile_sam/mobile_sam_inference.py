from mobile_sam import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import torch
import numpy as np
import cv2

import numpy as np

def save_output(masks, output_path):
     sorted_result = sorted(masks, key=(lambda x: x['area']), reverse=True)
     # Plot for each segment area
     for val in sorted_result:
        mask = val['segmentation']
        img = np.ones((mask.shape[0], mask.shape[1], 3))
        color_mask = np.random.random((1, 3)).tolist()[0]
        for i in range(3):
            img[:,:,i] = color_mask[i]
            cv2.imwrite(output_path, np.dstack((img, mask*0.5)))

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
  
  save_output(masks, output_path)
