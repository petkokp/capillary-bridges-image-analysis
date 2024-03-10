import cv2
import numpy as np
import math

def construct_ellipse_from_contour(img, contour, start_point, end_point, is_right=False):
    sliced_end = np.where((contour == start_point).all(axis=1))
    sliced_start = np.where((contour == end_point).all(axis=1))
    
    if len(sliced_end[0]) == 0 or len(sliced_start[0]) == 0:
        return
    
    start_index = sliced_start[0][0]
    end_index = sliced_end[0][0]
    
    is_reverse = start_index > end_index

    sliced_contour = []

    if is_reverse:
        sliced_contour = contour[end_index:start_index]
    else:
        sliced_contour = contour[start_index: end_index]
    
    if len(sliced_contour) == 0: return None, None
    
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

    # OpenCV ellipse requires atleast 5 points
    if len(sliced_contour) < 5:
        return None, None
    
    ellipse = cv2.fitEllipse(sliced_contour)
    
    (xc,yc),(d1,d2),angle = ellipse

    cv2.ellipse(img, ellipse, (255, 255, 255), 3)

    xc, yc = ellipse[0]
    cv2.circle(img, (int(xc),int(yc)), 10, (255, 255, 255), -1)

    rmajor = max(d1,d2)/2
    if angle > 90:
        angle = angle - 90
    else:
        angle = angle + 90

    x1_major = xc + math.cos(math.radians(angle))*rmajor
    y1_major = yc + math.sin(math.radians(angle))*rmajor
    x2_major = xc + math.cos(math.radians(angle+180))*rmajor
    y2_major = yc + math.sin(math.radians(angle+180))*rmajor
    cv2.line(img, (int(x1_major),int(y1_major)), (int(x2_major),int(y2_major)), (0, 0, 255), 3)

    rminor = min(d1,d2)/2
    if angle > 90:
        angle = angle - 90
    else:
        angle = angle + 90

    x1_minor = xc + math.cos(math.radians(angle))*rminor
    y1_minor = yc + math.sin(math.radians(angle))*rminor
    x2_minor = xc + math.cos(math.radians(angle+180))*rminor
    y2_minor = yc + math.sin(math.radians(angle+180))*rminor
    cv2.line(img, (int(x1_minor),int(y1_minor)), (int(x2_minor),int(y2_minor)), (255, 0, 0), 3)
    
    return ((x1_major, y1_major), (x2_major, y2_major)), ((x1_minor, y1_minor), (x2_minor, y2_minor))