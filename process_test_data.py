import cv2
import json
import sys
from utilities.visualize_test_results import visualize_test_results
from utilities.create_dir import create_dir
from utilities.compare_models import compare_models
from processing.process_test_data import process_test_data

MODEL = "SAM"

arg = ""

if len(sys.argv) > 1: arg = sys.argv[1] 

if arg == "NAIVE" or arg == "SAM": MODEL = arg

sequences_results, all_processed_images = process_test_data(MODEL)

INDEX_TO_SEQUENCE = {
    0: '20%',
    1: '16%',
    2: '15%',
    3: '5%',
    4: '3%',
    5: '0%',
    6: 'new_basler_camera'
}

with open(f"{MODEL}_values.json", "w") as f:
    json.dump(sequences_results, f)

visualize_test_results(sequences_results, INDEX_TO_SEQUENCE)

compare_models()

for i, image_sequence in enumerate(all_processed_images):
    SEQ = INDEX_TO_SEQUENCE[i]
    
    SAVE_PATH = f'./sam_final_results/{SEQ}' if MODEL == "SAM" else f'./standard_final_results/{SEQ}'
    
    create_dir(SAVE_PATH)

    for j, image in enumerate(image_sequence):
        cv2.imwrite(f'{SAVE_PATH}/{j}.png', image)