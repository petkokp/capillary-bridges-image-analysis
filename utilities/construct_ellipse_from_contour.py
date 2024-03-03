import cv2
import numpy as np

def construct_ellipse_from_contour(img, contour, start_point, end_point, is_right=False):
    end_index = np.where((contour == start_point).all(axis=1))[0][0]
    start_index = np.where((contour == end_point).all(axis=1))[0][0]
    
    is_reverse = start_index > end_index

    sliced_contour = []

    if is_reverse:
        sliced_contour = contour[end_index:start_index]
    else:
        sliced_contour = contour[start_index: end_index]
    
    if len(sliced_contour) == 0: return
    
    line_edge = img.shape[1] if is_right else 0

    _, y_start = start_point
    _, y_end = end_point

    intersection_start = ()
    intersection_end = ()
    
    if is_reverse:
        if is_right:
            intersection_start = (line_edge, y_end)
            intersection_end = (line_edge, y_start)    
        else:
            intersection_start = (line_edge, y_start)
            intersection_end = (line_edge, y_end)
    else:
        intersection_start = (line_edge, y_start)
        intersection_end = (line_edge, y_end)

    sliced_contour = np.vstack((sliced_contour, [intersection_start, intersection_end]))

    # cv2.drawContours(img, [sliced_contour], -1, (255, 255, 255), 2)
    
    ellipse = cv2.fitEllipse(sliced_contour)
  
    cv2.ellipse(img, ellipse, (255, 255, 255), 3)
    return