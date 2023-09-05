import argparse
import logging
import os
# import shutil
from PIL import Image, ExifTags
from datetime import datetime
# import sys


def process_images_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # @todo generalize file types
            if filename.lower().endswith(('.jpg', '.jpeg')):
                image_path = os.path.join(root, filename)
                process_image(image_path)


def process_image(image_path):
    try:
        with Image.open(image_path) as image:
            exif_data = image.getexif()
            # file handle not used anymore; otherwise resulted in file access error when renmaing later
            image.close()
            # read exif data and use metadata for renaming image
            if exif_data is not None:
                for tag, datetime_value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag)
                    if tag_name == "DateTime":
                        # rename file here
                        rename_file(image_path, datetime_value)
                        # skip remaining tags
                        break
            else:
                logging.error(f'No "DateTime" found in exif data for {image_path}')
    except Exception as e:
        logging.error(f'Error while trying to access exif data for {image_path}: {e}')


def rename_file(file_path, datetime_value):
    file_path = os.path.normpath(file_path)
    file_path_directory = os.path.dirname(file_path)
    file_path_fileextensions = os.path.splitext(file_path)[1]

    # convert input string to datetime object
    input_datetime = datetime.strptime(datetime_value, "%Y:%m:%d %H:%M:%S")

    # target example 20190107_191352
    formatted_datetime = input_datetime.strftime("%Y%m%d_%H%M%S")

    # Specifynew file path
    new_file_path = os.path.join(file_path_directory, formatted_datetime + file_path_fileextensions)

    # rename file
    try:
        # check if file already exists, due to possible local hodgepodge
        if not os.path.exists(new_file_path):
            os.rename(file_path, new_file_path)
            print(f"File '{file_path}' renamed to '{new_file_path}'")
        else:
            logging.error(f'Skipped copying file, because it already exists from a previous conversion: {file_path}')

            # check option here
            counter = 1
            while os.path.exists(new_file_path):
                # Generate a new unique name by appending _n to the base name
                base_name, extension = os.path.splitext(new_file_path)
                new_file_path = f"{base_name}_{counter}{extension}"
                counter += 1

            os.rename(file_path, new_file_path)
            print(f"File '{file_path}' renamed to '{new_file_path}'")

    except FileNotFoundError as e:
        # print(f'Error while trying to access exif data for {file_path}: {e}')
        logging.error(f'Error while trying to access exif data for {file_path}: {e}')
    except Exception as e:
        # print(f'Error while trying to access exif data for {file_path}: {e}')
        logging.error(f'Error while trying to access exif data for {file_path}: {e}')


if __name__ == "__main__":
    # configure logger
    logging.basicConfig(filename='error.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description="Reads exif data from images and renames images"
                                                 " according to creation datetime.")
    parser.add_argument("--directory", required=True, help="Directory with images.")
    args = parser.parse_args()
    process_images_in_directory(args.directory)

