import random as rng
import time
import numpy as np
import cv2
import sys

np.set_printoptions(threshold=sys.maxsize)


def pixels_to_micrometers(pixels):
    known_pixels = 1920
    known_micrometers = 3659.269
    micrometers = (pixels * known_micrometers) / known_pixels
    return round(micrometers, 2)


def calculate_percentage_error(experimental_value, theoretical_value):
    return round(np.mean(np.abs((theoretical_value - experimental_value) / theoretical_value)) * 100, 2)


def brighten(image):
    # convert to LAB and extract L  channel
    LAB = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    L = LAB[:, :, 0]
    # threshold L channel with triangle method
    value, thresh = cv2.threshold(L, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # threshold with adjusted value
    value = value + 10
    thresh = cv2.threshold(L, value, 255, cv2.THRESH_BINARY)[1]
    # invert threshold and make 3 channels
    thresh = 255 - thresh
    thresh = cv2.merge([thresh, thresh, thresh])
    gain = 2.5
    blue = cv2.multiply(image[:, :, 0], gain)
    green = cv2.multiply(image[:, :, 1], gain)
    red = cv2.multiply(image[:, :, 2], gain)
    img_bright = cv2.merge([blue, green, red])
    # blend original and brightened using thresh as mask
    return np.where(thresh == 255, img_bright, image)


def calculate_neck_properties(contour1, contour2):
    # Calculate the pairwise Euclidean distances between all points in the two contours
    distances = np.linalg.norm(contour1[:, None] - contour2, axis=-1)
    
    if distances is None:
      return None, None, None

    # Find the indices of the minimum distance in the distance matrix
    i, j = np.unravel_index(np.argmin(distances), distances.shape)

    # Get the nearest points
    nearest_points = (tuple(contour1[i]), tuple(contour2[j]))

    left_contour_rightmost_point = nearest_points[0]
    right_contour_leftmost_point = nearest_points[1]

    return pixels_to_micrometers(distances[i, j]), left_contour_rightmost_point, right_contour_leftmost_point


def collect_results(index, up_distance, down_distance, left_distance, right_distance, correct_values):
    results = []

    down_error = calculate_percentage_error(
        down_distance, correct_values['down'][index - 1])

    results.append({'Image': index, 'Type': 'Down',
                   'Error': f'{down_distance} µm, {down_error} % error'})

    right_error = calculate_percentage_error(
        right_distance, correct_values['right'][index - 1])

    results.append({'Image': index, 'Type': 'Right',
                   'Error': f'{right_distance} µm, {right_error} % error'})

    left_error = calculate_percentage_error(
        left_distance, correct_values['left'][index - 1])

    results.append({'Image': index, 'Type': 'Left',
                   'Error': f'{left_distance} µm, {left_error} % error'})

    up_error = calculate_percentage_error(
        up_distance, correct_values['up'][index - 1])

    results.append({'Image': index, 'Type': 'Up',
                   'Error': f'{up_distance} µm, {up_error} % error'})

    return results


def calculate_farthest_points(defects, contour):
    contour_farthest_points = [[0, 0], [0, 0]]
    max_distances = [0, 0]

    if defects is None: return contour_farthest_points 

    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        far = tuple(contour[f])
        distance = d / 256  # Scale the distance
        if distance > max_distances[0]:
            max_distances[1] = max_distances[0]
            contour_farthest_points[1] = contour_farthest_points[0]
            max_distances[0] = distance
            contour_farthest_points[0] = far
        elif distance > max_distances[1]:
            max_distances[1] = distance
            contour_farthest_points[1] = far

    return contour_farthest_points


rng.seed(12345)


def process_image(img, index, correct_values=None):
    top_crop = 60
    bottom_crop = 70
    left_crop = 60
    right_crop = 60

    roi = img[top_crop:-bottom_crop, left_crop:-right_crop]

    brightened_image = brighten(roi)

    standard_imgray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    brightened_imgray = cv2.cvtColor(brightened_image, cv2.COLOR_BGR2GRAY)

    _, standard_thresh = cv2.threshold(
        standard_imgray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    _, brightened_thresh = cv2.threshold(
        brightened_imgray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    brightened_contours, hierarchy = cv2.findContours(
        brightened_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    standard_contours, hierarchy = cv2.findContours(
        standard_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    standard_filtered_contours = sorted(
        standard_contours, key=lambda x: cv2.contourArea(x), reverse=True)[:2]

    brightened_filtered_contours = sorted(
        brightened_contours, key=lambda x: cv2.contourArea(x), reverse=True)[:2]

    img_with_line = roi.copy()

    standard_contour1 = np.vstack(standard_filtered_contours[0])
    standard_contour2 = np.vstack(standard_filtered_contours[1])

    if brightened_filtered_contours:
        brightened_contour2 = np.vstack(brightened_filtered_contours[1])
    else:
        return None, None

    brightened_contour1 = np.vstack(brightened_filtered_contours[0])
    brightened_contour2 = np.vstack(brightened_filtered_contours[1])

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

    return img_with_line, results, values


def access_webcam(CAM_INDEX):
    count = 0

    cap = cv2.VideoCapture(CAM_INDEX)

    prev_frame_time = 0

    new_frame_time = 0

    while True:
        ret, frame = cap.read()

        if frame is not None:
            img, results, values = process_image(frame, count + 1)

            font = cv2.FONT_HERSHEY_SIMPLEX
            new_frame_time = time.time()

            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time

            fps = int(fps)

            print('fps: ', fps)
            fps = str(fps)

            if img is not None:
                print(values)
                cv2.imshow('Webcam Feed', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


WEB_CAM = 0
USB_CAM = 1

access_webcam(WEB_CAM)
