import json

def extract_numeric_error(error_str):
    return float(error_str.split(', ')[1].split(' ')[0])

def process_data(data):
    type_errors = {}

    for sublist in data:
        for entry in sublist:
            type_name = entry['Type']
            error_value = extract_numeric_error(entry['Error'])
            type_errors.setdefault(type_name, []).append(error_value)

    return type_errors

def calculate_average_errors(type_errors):
    average_errors = {}
    for type_name, errors in type_errors.items():
        average_error = sum(errors) / len(errors)
        average_errors[type_name] = average_error

    return average_errors

def compare_experiment_errors(experiment_data):
    all_type_errors = [process_data(data) for data in experiment_data]
    average_errors_per_experiment = [calculate_average_errors(type_errors) for type_errors in all_type_errors]

    return average_errors_per_experiment

def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

INDEX_TO_MODEL = {
    0: 'NAIVE',
    1: 'SAM',
}

def compare_models():
  try:
    naive = read_json('NAIVE_values.json')
  except:
    print('Could not compare models. Error with NAIVE_values.json')
    return
    
  try:
    sam = read_json('SAM_values.json')
  except:
    print('Could not compare models. Error with SAM_values.json')
    return

  experiment_data = [
      naive,
      sam
  ]

  average_errors_per_experiment = compare_experiment_errors(experiment_data)

  for i, average_errors in enumerate(average_errors_per_experiment):
      print(f"{INDEX_TO_MODEL[i]} experiment:")

      for type_name, average_error in average_errors.items():
          print(f"  Average error for {type_name}: {average_error:.2f} %")
