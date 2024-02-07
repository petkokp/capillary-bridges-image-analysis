from .calculate_percentage_error import calculate_percentage_error

def collect_results(index, up_distance, down_distance, left_distance, right_distance, correct_values):
  results = []
  
  down_error = calculate_percentage_error(down_distance, correct_values['down'][index -1])
        
  results.append({'Image': index, 'Type': 'Down', 'Error': f'{down_distance} µm, {down_error} % error' })
  
  right_error = calculate_percentage_error(right_distance, correct_values['right'][index -1])
        
  results.append({'Image': index, 'Type': 'Right', 'Error': f'{right_distance} µm, {right_error} % error' })
  
  left_error = calculate_percentage_error(left_distance, correct_values['left'][index -1])
  
  results.append({'Image': index, 'Type': 'Left', 'Error': f'{left_distance} µm, {left_error} % error' })
  
  up_error = calculate_percentage_error(up_distance, correct_values['up'][index -1])
  
  results.append({'Image': index, 'Type': 'Up', 'Error': f'{up_distance} µm, {up_error} % error' })
  
  return results