import cv2
import numpy as np
import math

def construct_ellipse_from_contour(img, contour, start_point, end_point, is_right=False):
    sliced_end = np.where((contour == start_point).all(axis=1))
    sliced_start = np.where((contour == end_point).all(axis=1))
    
    if len(sliced_end[0]) == 0 or len(sliced_start[0]) == 0:
        print('returning')
        return
    
    start_index = sliced_start[0][0]
    end_index = sliced_end[0][0]
    
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

    # OpenCV ellipse requires atleast 5 points
    if len(sliced_contour) < 5:
        return

    # cv2.drawContours(img, [sliced_contour], -1, (255, 255, 255), 2)
    
    ellipse = cv2.fitEllipse(sliced_contour)
    
    (xc,yc),(d1,d2),angle = ellipse

    # draw ellipse in white
    cv2.ellipse(img, ellipse, (255, 255, 255), 3)

    # draw circle at center
    xc, yc = ellipse[0]
    cv2.circle(img, (int(xc),int(yc)), 10, (255, 255, 255), -1)

    # draw major axis line in red
    rmajor = max(d1,d2)/2
    if angle > 90:
        angle = angle - 90
    else:
        angle = angle + 90

    x1 = xc + math.cos(math.radians(angle))*rmajor
    y1 = yc + math.sin(math.radians(angle))*rmajor
    x2 = xc + math.cos(math.radians(angle+180))*rmajor
    y2 = yc + math.sin(math.radians(angle+180))*rmajor
    cv2.line(img, (int(x1),int(y1)), (int(x2),int(y2)), (0, 0, 255), 3)

    # draw minor axis line in blue
    rminor = min(d1,d2)/2
    if angle > 90:
        angle = angle - 90
    else:
        angle = angle + 90

    x1 = xc + math.cos(math.radians(angle))*rminor
    y1 = yc + math.sin(math.radians(angle))*rminor
    x2 = xc + math.cos(math.radians(angle+180))*rminor
    y2 = yc + math.sin(math.radians(angle+180))*rminor
    cv2.line(img, (int(x1),int(y1)), (int(x2),int(y2)), (255, 0, 0), 3)