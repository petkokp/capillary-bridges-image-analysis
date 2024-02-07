from .test_images import IMAGES_DATA
from .process_sequence import process_sequence

def process_test_data(model):
    sequences_results = []
    all_processed_images = []
    
    images_length = len(IMAGES_DATA)

    for i in range(images_length):
        image_data = IMAGES_DATA[i]
        print(f'Sequence {i}/{images_length - 1}\n')
        sequence_results, processed_images = process_sequence(image_data['path'], image_data['values'], model)
        sequences_results.append(sequence_results)
        all_processed_images.append(processed_images)
        
    return sequences_results, all_processed_images