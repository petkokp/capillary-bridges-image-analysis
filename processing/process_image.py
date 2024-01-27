import random as rng
import cv2
import numpy as np
import matplotlib.pyplot as plt
from utilities.create_dir import create_dir
from utilities.calculate_percentage_error import calculate_percentage_error
from utilities.calculate_neck_properties import calculate_neck_properties
from utilities.collect_results import collect_results
from utilities.pixels_to_micrometers import pixels_to_micrometers
from utilities.calculate_farthest_points import calculate_farthest_points
from .brighten import brighten
from .process_sam import process_sam

rng.seed(12345)

def standard_process(roi, index, correct_values=None):
    brightened_image = brighten(roi)

    standard_imgray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    brightened_imgray = cv2.cvtColor(brightened_image, cv2.COLOR_BGR2GRAY)

    _, standard_thresh = cv2.threshold(
        standard_imgray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    _, brightened_thresh = cv2.threshold(
        brightened_imgray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    brightened_contours, _ = cv2.findContours(
        brightened_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    standard_contours, _ = cv2.findContours(
        standard_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    standard_filtered_contours = sorted(
        standard_contours, key=lambda x: cv2.contourArea(x), reverse=True)[:2]

    brightened_filtered_contours = sorted(
        brightened_contours, key=lambda x: cv2.contourArea(x), reverse=True)[:2]

    img_with_line = roi.copy()
    
    standard_contour1 = None
    standard_contour2 = None
    
    if len(standard_filtered_contours) >= 2:
        standard_contour1 = np.vstack(standard_filtered_contours[0])
        standard_contour2 = np.vstack(standard_filtered_contours[1])
    else:
        return None, None
    
    brightened_contour1 = None
    brightened_contour2 = None

    if brightened_filtered_contours:
        brightened_contour1 = np.vstack(brightened_filtered_contours[0])
        brightened_contour2 = np.vstack(brightened_filtered_contours[1])
    else:
        return None, None

    neck_distance, left_contour_rightmost_point, right_contour_leftmost_point = calculate_neck_properties(
        standard_contour1, standard_contour2)

    results = []
    
    values = {
        'neck': neck_distance,
    }

    if correct_values is not None and neck_distance is not None:
        neck_error = calculate_percentage_error(
            neck_distance, correct_values['neck'][index - 1])
        results.append({'Image': index, 'Type': 'Neck',
                       'Error': f'{neck_distance} µm, {neck_error} % error'})

    hull1 = cv2.convexHull(brightened_contour1, returnPoints=False)

    hull1[::-1].sort(axis=0)

    hull2 = cv2.convexHull(brightened_contour2, returnPoints=False)

    hull2[::-1].sort(axis=0)

    cv2.drawContours(
        img_with_line, brightened_filtered_contours, -1, (0, 255, 0), 3)

    hull_list = []
    for i in range(len(brightened_filtered_contours)):
        hull = cv2.convexHull(brightened_filtered_contours[i])
        hull_list.append(hull)

    if len(brightened_filtered_contours) >= 2:
        defects1 = cv2.convexityDefects(brightened_contour1, hull1)
        defects2 = cv2.convexityDefects(brightened_contour2, hull2)

        contour1_farthest_points = calculate_farthest_points(
            defects1, brightened_contour1)
        contour2_farthest_points = calculate_farthest_points(
            defects2, brightened_contour2)

        contour1_start, contour1_end = np.array(
            contour1_farthest_points[0]), np.array(contour1_farthest_points[1])
        contour2_start, contour2_end = np.array(
            contour2_farthest_points[0]), np.array(contour2_farthest_points[1])

        if contour1_start[1] < contour1_end[1]:
            contour1_start, contour1_end = contour1_end, contour1_start

        if contour2_start[1] < contour2_end[1]:
            contour2_start, contour2_end = contour2_end, contour2_start

        down_distance = pixels_to_micrometers(
            np.linalg.norm(contour1_end - contour2_end))

        up_distance = pixels_to_micrometers(
            np.linalg.norm(contour1_start - contour2_start))

        left_distance = pixels_to_micrometers(
            np.linalg.norm(contour1_start - contour1_end))

        right_distance = pixels_to_micrometers(
            np.linalg.norm(contour2_start - contour2_end))
        
        values['down'] = down_distance
        values['up'] = up_distance
        values['left'] = left_distance
        values['right'] = right_distance

        if correct_values:
            results += collect_results(index, down_distance, up_distance,
                                       left_distance, right_distance, correct_values)

        cv2.line(img_with_line, contour1_start, contour2_start, (255, 0, 0), 2)

        cv2.line(img_with_line, contour1_end, contour2_end, (255, 0, 0), 2)

        cv2.line(img_with_line, contour1_start, contour1_end, (255, 0, 0), 2)

        cv2.line(img_with_line, contour2_start, contour2_end, (255, 0, 0), 2)

        if left_contour_rightmost_point and right_contour_leftmost_point:
            cv2.line(img_with_line, left_contour_rightmost_point,
                     right_contour_leftmost_point, (0, 0, 255), 2)
    else:
        print("Insufficient number of filtered contours.")

    return img_with_line, results
    
def sam_process(img, index, save_path, correct_values=None):
    brightened_image = process_sam(save_path, index, img)
    
    brightened_imgray = cv2.cvtColor(brightened_image, cv2.COLOR_BGR2GRAY)
    
    _, brightened_thresh = cv2.threshold(
        brightened_imgray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    brightened_contours, _ = cv2.findContours(
        brightened_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    img_with_line = img.copy()
    
    if (len(brightened_contours) < 2):
        cv2.drawContours(img_with_line, brightened_contours, -1, (0, 255, 0), 3)
        create_dir(f'broken/{save_path}')
        plt.imsave(f'./broken/{save_path}/{index}.png', img_with_line)
        print('Less than 2 contours found')
        return None, None
    
    brightened_filtered_contours = sorted(
        brightened_contours, key=lambda x: cv2.contourArea(x), reverse=True)[:2]
    
    brightened_contour1 = np.vstack(brightened_filtered_contours[0])
    brightened_contour2 = np.vstack(brightened_filtered_contours[1])
    
    neck_distance, left_contour_rightmost_point, right_contour_leftmost_point = calculate_neck_properties(brightened_contour1, brightened_contour2)
    
    results = []
        
    if correct_values is not None:
        neck_error = calculate_percentage_error(neck_distance, correct_values['neck'][index -1])
        results.append({'Image': index, 'Type': 'Neck', 'Error': f'{neck_distance} µm, {neck_error} % error' })
    
    hull1 = cv2.convexHull(brightened_contour1, returnPoints=False)
    
    hull1[::-1].sort(axis=0)
    
    hull2 = cv2.convexHull(brightened_contour2, returnPoints=False)
    
    hull2[::-1].sort(axis=0)

    cv2.drawContours(img_with_line, brightened_filtered_contours, -1, (0, 255, 0), 3)
    
    hull_list = []
    for i in range(len(brightened_filtered_contours)):
        hull = cv2.convexHull(brightened_filtered_contours[i])
        hull_list.append(hull)

    defects1 = cv2.convexityDefects(brightened_contour1, hull1)
    defects2 = cv2.convexityDefects(brightened_contour2, hull2)
    
    contour1_farthest_points = calculate_farthest_points(defects1, brightened_contour1)
    contour2_farthest_points = calculate_farthest_points(defects2, brightened_contour2)
    
    contour1_start, contour1_end = np.array(contour1_farthest_points[0]), np.array(contour1_farthest_points[1])
    contour2_start, contour2_end = np.array(contour2_farthest_points[0]), np.array(contour2_farthest_points[1])
    
    if contour1_start[1] < contour1_end[1]:
        contour1_start, contour1_end = contour1_end, contour1_start
    
    if contour2_start[1] < contour2_end[1]:
        contour2_start, contour2_end = contour2_end, contour2_start
    
    down_distance = pixels_to_micrometers(
        np.linalg.norm(contour1_end - contour2_end))
    
    up_distance = pixels_to_micrometers(
        np.linalg.norm(contour1_start - contour2_start))
    
    left_distance = pixels_to_micrometers(
        np.linalg.norm(contour1_start - contour1_end))

    right_distance = pixels_to_micrometers(
        np.linalg.norm(contour2_start - contour2_end))
    
    if correct_values:
        results += collect_results(index, down_distance, up_distance, left_distance, right_distance, correct_values)

    cv2.line(img_with_line, contour1_start, contour2_start, (255, 0, 0), 2)

    cv2.line(img_with_line, contour1_end, contour2_end, (255, 0, 0), 2)

    cv2.line(img_with_line, contour1_start, contour1_end, (255, 0, 0), 2)

    cv2.line(img_with_line, contour2_start, contour2_end, (255, 0, 0), 2)

    cv2.line(img_with_line, left_contour_rightmost_point, right_contour_leftmost_point, (0, 0, 255), 2)

    return img_with_line, results

def process_image(img, index, save_path, model="SAM", correct_values=None):
    top_crop = 60
    bottom_crop = 70
    left_crop = 60
    right_crop = 60
    
    roi = img[top_crop:-bottom_crop, left_crop:-right_crop]
    
    if model == "SAM":
        return sam_process(roi, index, save_path, correct_values)
            
    return standard_process(roi, index, correct_values)