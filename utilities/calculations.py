def calculate_base(up_distance, down_distance):
  return (up_distance + down_distance) / 2

def calculate_height(left_distance, right_distance):
  return (left_distance + right_distance) / 2

def calculate_x(base, neck_distance):
  return base / neck_distance

def calculate_y(height, neck):
  return height / neck
