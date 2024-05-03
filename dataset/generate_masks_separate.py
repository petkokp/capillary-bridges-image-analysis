import json
import os
import numpy as np
import PIL.Image
import cv2
import matplotlib.pyplot as plt

with open("annotations.json", "r") as read_file:
    data = json.load(read_file)

all_file_names = list(data.keys())

Files_in_directory = []
for root, dirs, files in os.walk("images"):
    for filename in files:
        Files_in_directory.append(filename)

for j in range(len(all_file_names)):
    image_name = data[all_file_names[j]]['filename']
    if image_name in Files_in_directory:
        img = np.asarray(PIL.Image.open('images/' + image_name))
    else:
        continue

    regions = data[all_file_names[j]]['regions']
    if regions:
        fig = plt.figure()
        plt.imshow(img.astype(np.uint8))

        if isinstance(regions, list):  # Handle case when regions is a list
            for i, region_data in enumerate(regions):
                shape_x = region_data['shape_attributes']['all_points_x']
                shape_y = region_data['shape_attributes']['all_points_y']
                plt.scatter(shape_x, shape_y, zorder=2, color='red', marker='.', s=55)

                ab = np.stack((shape_x, shape_y), axis=1)
                img = cv2.drawContours(img, [ab], -1, (255, 255, 255), -1)

                mask = np.zeros((img.shape[0], img.shape[1]))
                mask = cv2.drawContours(mask, [ab], -1, 255, -1)

                cv2.imwrite(f'masks/{all_file_names[j]}_{i}.png', mask.astype(np.uint8))

        elif isinstance(regions, dict):
            for region_index, region_data in regions.items():
                shape_x = region_data['shape_attributes']['all_points_x']
                shape_y = region_data['shape_attributes']['all_points_y']
                plt.scatter(shape_x, shape_y, zorder=2, color='red', marker='.', s=55)

                ab = np.stack((shape_x, shape_y), axis=1)
                img = cv2.drawContours(img, [ab], -1, (255, 255, 255), -1)

                mask = np.zeros((img.shape[0], img.shape[1]))
                mask = cv2.drawContours(mask, [ab], -1, 255, -1)

                cv2.imwrite(f'masks/{all_file_names[j]}_{region_index}.png', mask.astype(np.uint8))

