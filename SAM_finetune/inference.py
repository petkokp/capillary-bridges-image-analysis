import argparse
import torch
import numpy as np
from .src.segment_anything import build_sam_vit_b, SamPredictor
from .src.lora import LoRA_sam
import matplotlib.pyplot as plt
from .src.utils import get_bounding_box
from PIL import Image
from pathlib import Path
from os.path import split
import cv2

parser = argparse.ArgumentParser(description="SAM-fine-tune Inference")
parser.add_argument("-r", "--rank", default=512, help="LoRA model rank.")
parser.add_argument("-l", "--lora", default="lora_weights/lora_rank512.safetensors", help="Location of LoRA Weight file.")
parser.add_argument("-d", "--device", choices=["cuda", "cpu"], default="cuda", help="What device to run the inference on.")
parser.add_argument("-b", "--baseline", action="store_true", help="Use baseline SAM instead of a LoRA model.")

args = parser.parse_args()

def inference_model(image_path, save_name):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    image = Image.open(image_path)

    sam_checkpoint = "sam_vit_b_01ec64.pth"
    sam = build_sam_vit_b(checkpoint=sam_checkpoint)

    if args.baseline:
        model = sam
    else:
        rank = args.rank
        sam_lora = LoRA_sam(sam, rank)
        sam_lora.load_lora_parameters(args.lora)
        model = sam_lora.sam
        
    image = np.array(image)

    model.eval()
    model.to(device)
    
    predictor = SamPredictor(model)
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
    
    plt.imsave(save_name, masks[0])
    print("IoU Prediction:", iou_pred[0])
