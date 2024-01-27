import os

def create_dir(path):
  exists = os.path.exists(path)
  if not exists:
    os.makedirs(path)