def extract_sequence_name_from_path(path: str):
  return path.split('/')[1].split('.')[0]