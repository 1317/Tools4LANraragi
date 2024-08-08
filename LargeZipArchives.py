import os
import zipfile

dir = r'path/to/LANraragi/content/'
image_infos = []


def count_files_in_zip(zip_file_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # get the list of all files in the zip archive
        files = zip_ref.namelist()

        # filter the list to get only images
        images = [file for file in files if file.lower().endswith(
            image_extensions)]

        # return a tuple of the number of all files and the number of images
        return [len(zip_ref.namelist()), len(images)]


# walk through all zip files in the directory
for root, dirs, files in os.walk(dir):
    for file in files:
        if file.endswith('.zip'):
            try:
                # get the number of files in the zip
                file_path = os.path.join(root, file)
                # print(count_files_in_zip(file_path))

                # get the size of the zip file, in MB
                file_size = os.path.getsize(file_path) / 1024 / 1024

                # calculate the average size per image
                num_files, num_images = count_files_in_zip(file_path)
                avg_size_per_image = file_size / num_images

                # threshold for the average size per image
                threshold = 5  # MB

                # if the average size per image is greater than the threshold
                if avg_size_per_image >= threshold:
                    # print(f'{file_size:.2f} MB - {num_files:>3d} files - {num_images:>3d} images - {avg_size_per_image:.2f} MB/img -> {file}')
                    image_infos.append({"FileSize": file_size, "NumFiles": num_files, "NumImages": num_images,
                                       "AvgSizePerImage": avg_size_per_image, "FileName": file})
            except Exception as e:
                print(f'Error processing {file_path}: {e}')
                continue

# sort the list by the average size per image
image_infos.sort(key=lambda x: x['AvgSizePerImage'], reverse=True)
# print the list
for info in image_infos:
    print(f'{info["FileSize"]:8.2f} MB - {info["NumFiles"]:>3d} files - {info["NumImages"]:>3d} images - {info["AvgSizePerImage"]:5.2f} MB/img -> {info["FileName"]}')
