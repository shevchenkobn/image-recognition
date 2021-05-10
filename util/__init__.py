import os


def change_filename_dir(filepath, new_dir):
    file_name = os.path.basename(filepath)
    return os.path.join(new_dir, file_name)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
