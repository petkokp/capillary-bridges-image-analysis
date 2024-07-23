def pixels_to_micrometers(pixels, conversion_scale):
    BASLER_CAMERA_KNOWN_PIXELS = 800
    micrometers = (pixels * conversion_scale) / BASLER_CAMERA_KNOWN_PIXELS
    return round(micrometers, 2)