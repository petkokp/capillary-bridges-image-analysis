import numpy as np
from .pixels_to_micrometers import pixels_to_micrometers

def calculate_neck_properties(contour1, contour2):
    # Calculate the pairwise Euclidean distances between all points in the two contours
    distances = np.linalg.norm(contour1[:, None] - contour2, axis=-1)

    # Find the indices of the minimum distance in the distance matrix
    i, j = np.unravel_index(np.argmin(distances), distances.shape)

    # Get the nearest points
    nearest_points = tuple(contour1[i]), tuple(contour2[j])

    left_contour_rightmost_point, right_contour_leftmost_point = nearest_points

    return pixels_to_micrometers(np.min(distances)), left_contour_rightmost_point, right_contour_leftmost_point
