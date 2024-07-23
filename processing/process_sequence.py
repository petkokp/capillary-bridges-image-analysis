import cv2
import glob
from .process_image import process_image
from utilities.extract_sequence_name_from_path import extract_sequence_name_from_path
from utilities.default_conversion_scale import DEFAULT_CONVERSION_SCALE

def process_sequence(path: str, correct_values, model):
    imgs = []
    
    if path.endswith('.tif'):
         _, imgs = cv2.imreadmulti(path)
    else:
        filenames = glob.glob(f"{path}/*.png")
        filenames.sort()
        imgs = [cv2.imread(img) for img in filenames]
        
    processed_images = []
    all_results = []

    for i, img in enumerate(imgs):
        print(f'Image {i}/{len(imgs) - 1}\n')
        img_with_line, results, _ = process_image(imgs[i], index=i + 1, conversion_scale=DEFAULT_CONVERSION_SCALE, model=model, save_path=extract_sequence_name_from_path(path), correct_values=correct_values)
        
        if img_with_line is not None and results is not None:
            temp = []
            temp.extend(results)
            all_results.extend(results)
            processed_images.append(img_with_line)
    
    return all_results, processed_images