# Convert pixels to micrometers according to data in "./correct_values"
def pixels_to_micrometers(pixels):
    known_pixels = 1920
    known_micrometers = 3659.269
    micrometers = (pixels * known_micrometers) / known_pixels
    return round(micrometers, 2)