import cv2
import numpy as np
from utilities.calculate_percentage_error import calculate_percentage_error
from utilities.calculate_neck_properties import calculate_neck_properties
from utilities.collect_results import collect_results
from utilities.pixels_to_micrometers import pixels_to_micrometers
from utilities.calculate_farthest_points import calculate_farthest_points
from utilities.construct_ellipse_from_contour import construct_ellipse_from_contour
from .brighten import brighten

def get_filtered_and_sorted_contours(contours):
    areas = [cv2.contourArea(c) for c in contours]
    indices = np.argsort(areas)[::-1][:2]
    return [contours[i] for i in indices]

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

    standard_filtered_contours = get_filtered_and_sorted_contours(
        standard_contours)
    brightened_filtered_contours = get_filtered_and_sorted_contours(
        brightened_contours)

    img_with_line = roi.copy()

    standard_contour1 = None
    standard_contour2 = None

    if len(standard_filtered_contours) >= 2:
        standard_contour1 = np.vstack(standard_filtered_contours[0])
                
        standard_contour2 = np.vstack(standard_filtered_contours[1])
    else:
        return None, None, None

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

    if len(brightened_filtered_contours) >= 2:
        brightened_contour1 = np.vstack(brightened_filtered_contours[0])
        brightened_contour2 = np.vstack(brightened_filtered_contours[1])

        hull1 = cv2.convexHull(brightened_contour1, returnPoints=False)

        hull1[::-1].sort(axis=0)

        hull2 = cv2.convexHull(brightened_contour2, returnPoints=False)

        hull2[::-1].sort(axis=0)

        cv2.drawContours(
            img_with_line, brightened_filtered_contours, -1, (0, 255, 0), 3)

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
        
        brightened_contours = [brightened_contour1, brightened_contour2]
        
        bounding_boxes = [cv2.boundingRect(contour) for contour in brightened_contours]

        leftmost_index = 0 if bounding_boxes[0][0] < bounding_boxes[1][0] else 1
        rightmost_index = 1 - leftmost_index

        left_contour = brightened_contours[leftmost_index]
        right_contour = brightened_contours[rightmost_index]
        
        left_start_point = []
        left_end_point = []
        right_start_point = []
        right_end_point = []
        
        if left_contour is brightened_contour1:
            left_start_point = contour1_start
            left_end_point = contour1_end
            right_start_point = contour2_start
            right_end_point = contour2_end
        else:
            left_start_point = contour2_start
            left_end_point = contour2_end
            right_start_point = contour1_start
            right_end_point = contour1_end
        
        construct_ellipse_from_contour(img_with_line, left_contour, left_start_point, left_end_point)
        
        construct_ellipse_from_contour(img_with_line, right_contour, right_start_point, right_end_point, is_right=True)

        if contour1_start[1] < contour1_end[1]:
            contour1_start, contour1_end = contour1_end, contour1_start

        if contour2_start[1] < contour2_end[1]:
            contour2_start, contour2_end = contour2_end, contour2_start

        down_distance = pixels_to_micrometers(
            np.sqrt(np.sum((contour1_end - contour2_end) ** 2)))
        up_distance = pixels_to_micrometers(
            np.sqrt(np.sum((contour1_start - contour2_start) ** 2)))
        left_distance = pixels_to_micrometers(
            np.sqrt(np.sum((contour1_start - contour1_end) ** 2)))
        right_distance = pixels_to_micrometers(
            np.sqrt(np.sum((contour2_start - contour2_end) ** 2)))

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

    return img_with_line, results, values
  
def process_image_basic(img, index, correct_values=None):
    top_crop = 60
    bottom_crop = 70
    left_crop = 60
    right_crop = 60

    roi = img[top_crop:-bottom_crop, left_crop:-right_crop]

    return standard_process(roi, index, correct_values)
