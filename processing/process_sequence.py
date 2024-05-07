import cv2
from .process_image import process_image
from utilities.extract_sequence_name_from_path import extract_sequence_name_from_path

def process_sequence(path, correct_values, model):
    _, imgs = cv2.imreadmulti(path)
    processed_images = []
    all_results = []

    for i, img in enumerate(imgs):
        print(f'Image {i}/{len(imgs) - 1}\n')
        img_with_line, results, _ = process_image(imgs[i], correct_values=correct_values, index=i + 1, model=model, save_path=extract_sequence_name_from_path(path))
        
        if img_with_line is not None and results is not None:
            temp = []
            temp.extend(results)
            all_results.extend(results)
            processed_images.append(img_with_line)
    
    return all_results, processed_images