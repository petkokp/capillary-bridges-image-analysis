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
    
    predictor = SamPredictor(mobile_sam)
    predictor.set_image(image)
    
    height, width, _ = image.shape

    x_left = width - (width - 50)
    x_right = width - 50
    y = (height / 2) + 50

    input_point = np.array([[x_left, y], [x_right, y]])
    input_label = np.array([1, 1])

    masks, iou_pred, low_res_iou = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=False
    )
  
    save_output(masks[0], output_path)
