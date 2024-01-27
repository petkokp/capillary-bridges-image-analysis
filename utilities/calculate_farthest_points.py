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