from PIL import Image
import os
from datetime import datetime
import zipfile
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import shutil
import subprocess
import argparse

img_exts = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif')
video_exts = ('.mp4', '.mov')
exts = img_exts + video_exts

# ANSI escape codes for colors and styles


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def convert_video_to_webp(input_video_path, output_image_path, fps=15, size="854:480"):
    # 使用ffmpeg将视频转换为WebP格式
    # command:  ffmpeg -i .\input.mp4 -vcodec libwebp -loop 0 -preset default -lossless 1 -filter:v fps=fps=15  -s 854:480  output.webp -y
    r = subprocess.run(["ffmpeg", "-i", input_video_path, "-vcodec", "libwebp", "-loop", "0", "-preset", "default", "-lossless", "0",
                       "-filter:v", f"fps=fps={fps}", "-s", size, output_image_path, "-y"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    if r.returncode != 0:
        print(
            f"{Colors.FAIL}Failed to convert video to WebP: {r.stderr.decode('utf-8')}{Colors.ENDC}")
        return

    # 保留源文件的修改日期
    mtime = os.path.getmtime(input_video_path)
    os.utime(output_image_path, (mtime, mtime))


def resize_and_compress_image(input_image_path, output_image_path, method=6, short_side=2400, quality=80, gif_quality=80, gif_method=4):
    with Image.open(input_image_path) as img:
        # 获取原始尺寸
        width, height = img.size

        # 检查是否需要调整尺寸
        if min(width, height) < short_side:
            # 如果短边小于目标尺寸，则不需要调整尺寸
            new_width, new_height = width, height
        else:
            # 根据短边确定新的宽度和高度
            if width > height:
                new_width = int((short_side / height) * width)
                new_height = short_side
            else:
                new_height = int((short_side / width) * height)
                new_width = short_side

        # 如果需要调整尺寸则调整
        if (width, height) != (new_width, new_height):
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        else:
            resized_img = img

        # 将图像保存为WebP格式
        # resized_img.save(output_image_path, "WEBP", quality=quality,
        #                  optimize=True, method=6)
        # if the image is GIF, pass more args to save as animated webp
        if img.format == 'GIF':
            resized_img.save(output_image_path, "WEBP", quality=gif_quality,
                             save_all=True, method=gif_method, allow_mixed=True)
        else:
            resized_img.save(output_image_path, "WEBP", quality=quality,
                             optimize=True, method=method)

        # 保留源文件的修改日期
        mtime = os.path.getmtime(input_image_path)
        os.utime(output_image_path, (mtime, mtime))


def process_media(file, temp_dir):
    if file.lower().endswith(exts):
        # 生成新的文件名
        new_file = os.path.join(temp_dir, os.path.splitext(file)[0] + ".webp")
        # print(f"Processing {file} to {new_file}")

        if file.lower().endswith(video_exts):
            # 如果是视频文件则转换为WebP格式
            convert_video_to_webp(
                os.path.join(temp_dir, file),
                new_file,
                fps=presets["video"]["fps"],
                size=presets["video"]["size"])
            return new_file, file
        elif file.lower().endswith(img_exts):
            # 压缩并调整图片大小
            resize_and_compress_image(
                os.path.join(temp_dir, file),
                new_file,
                quality=presets["image"]["quality"],
                method=presets["image"]["method"],
                short_side=presets["image"]["short_side"],
                gif_quality=presets["image"]["gif_quality"],
                gif_method=presets["image"]["gif_method"]
            )

        return new_file, file

    return None, file


def extract_zip_files(zip_file_path, temp_dir):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # 遍历ZIP文件中的所有成员
        for member in zip_ref.infolist():
            # 提取文件到指定目录
            zip_ref.extract(member, temp_dir)

            # 获取ZIP文件中文件的原始修改时间
            mod_time = member.date_time  # UTC时间

            # 将时间元组转换为datetime对象
            mod_time = datetime(*mod_time)

            # 设置输出文件的修改时间为ZIP文件中的时间
            extracted_path = os.path.join(temp_dir, member.filename)
            os.utime(extracted_path, (mod_time.timestamp(), mod_time.timestamp()))


def delete_temp_dir(temp_dir):
    try:
        # 检查临时文件夹是否存在
        if os.path.exists(temp_dir):
            # 删除临时文件夹及其内容
            shutil.rmtree(temp_dir)
            print(
                f"{Colors.OKBLUE}Temporary directory '{temp_dir}' has been deleted.{Colors.ENDC}")
    except Exception as e:
        print(
            f"{Colors.FAIL}Failed to delete temporary directory '{temp_dir}': {e}{Colors.ENDC}")


def compress_images_in_zip(zip_file_path, output_zip_path, temp_dir, max_workers=8):

    # 解压ZIP文件到临时目录
    extract_zip_files(zip_file_path, temp_dir)

    # 获取所有文件的列表
    files = []
    for root, _, filenames in os.walk(temp_dir):
        for filename in filenames:
            files.append(os.path.join(root, filename))

    # 使用多线程处理图像
    processed_files = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务给线程池
        futures = [executor.submit(process_media, file, temp_dir)
                   for file in files if file.lower().endswith(exts)]

        # 创建一个进度条
        progress_bar = tqdm(total=len(futures),
                            desc="  Processing Images", unit="image")

        # 收集结果
        for future in futures:
            new_file, original_file = future.result()
            if new_file:
                processed_files.append((new_file, original_file))
                progress_bar.update(1)  # 更新进度条

        progress_bar.close()  # 关闭进度条

    # 创建一个新的ZIP文件来存储压缩后的图像
    try:
        # check if the output zip file already exists, if so, ask for overwrite
        if os.path.exists(output_zip_path):
            print(
                f"{Colors.WARNING}The output ZIP file '{output_zip_path}' already exists.{Colors.ENDC}")
            overwrite = input("Do you want to overwrite it? (y/n): ")
            if overwrite.lower() != 'y':
                print(
                    f"{Colors.FAIL}The output ZIP file has not been overwritten.{Colors.ENDC}")
                return
            else:
                print(
                    f"{Colors.WARNING}The output ZIP file will be overwritten.{Colors.ENDC}")
                os.remove(output_zip_path)

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            # 处理压缩后的图片
            for new_file, original_file in processed_files:
                new_zip.write(
                    new_file, arcname=os.path.relpath(new_file, temp_dir))
                os.remove(new_file)

            # 处理非图片文件
            for file in files:
                if not any(file.endswith(ext) for ext in exts):
                    new_zip.write(
                        file, arcname=os.path.relpath(file, temp_dir))
    except Exception as e:
        print(f"{Colors.FAIL}Failed to create ZIP file{Colors.ENDC}")

    # 清理临时目录
    for file in files:
        os.remove(os.path.join(temp_dir, file))


def process_zip_files(input_zip_dir, output_zip_dir, max_workers=8):
    # 获取输入目录下的所有ZIP文件
    zip_files = [f for f in os.listdir(input_zip_dir) if f.endswith('.zip')]

    # 临时目录
    temp_dir = os.path.join(output_zip_dir, 'tmp')

    for zip_file in zip_files:
        print(f"{Colors.HEADER}{Colors.BOLD}Processing: {zip_file}{Colors.ENDC}")

        input_zip_path = os.path.join(input_zip_dir, zip_file)
        # the name of output zip is "filename + (SHORT_SIDEx).zip"
        output_zip_path = os.path.join(output_zip_dir,
                                       os.path.splitext(zip_file)[0]
                                       + f" ({presets['image']['short_side']}x).zip")

        original_zip_size = os.path.getsize(input_zip_path)

        # 创建输出目录
        os.makedirs(output_zip_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)

        # 压缩图片并创建新的ZIP文件
        compress_images_in_zip(
            input_zip_path, output_zip_path, temp_dir, max_workers=max_workers)

        # 计算压缩后ZIP文件的大小
        compressed_zip_size = os.path.getsize(output_zip_path)

        # 计算压缩率
        compression_rate = compressed_zip_size / \
            original_zip_size * 100 if original_zip_size > 0 else 0

        print(
            f"  {Colors.OKCYAN}Result: {original_zip_size/1024/1024:8.2f} MB -> {compressed_zip_size/1024/1024:8.2f} MB  ({compression_rate:.1f}%){Colors.ENDC}\n")

    delete_temp_dir(temp_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process and compress images in ZIP files.')
    parser.add_argument('-i', '--input-dir', type=str, default=os.path.join(os.getcwd(), "input"),
                        help='The directory containing the input ZIP files (default: ./input).')
    parser.add_argument('-o', '--output-dir', type=str, default=os.path.join(os.getcwd(), "output"),
                        help='The directory where the output ZIP files will be saved (default: ./output).')

    parser.add_argument('-q', '--quality', type=int, default=80, metavar='IMAGE_QUALITY',
                        help='The quality of the compressed images (default: 80).')
    parser.add_argument('-m', '--method', type=int, default=6, metavar='IMAGE_METHOD',
                        help='The compression method for images (default: 6).')
    parser.add_argument('-s', '--short-side', type=int, default=2400,
                        help='The length of the shorter side of the image (px) (default: 2400).')

    parser.add_argument('-Q', '--gif-quality', type=int, default=80,
                        help='The quality of the compressed GIF images (default: 80).')
    parser.add_argument('-M', '--gif-method', type=int, default=4,
                        help='The compression method for GIF images (default: 4).')

    parser.add_argument('-f', '--fps', type=int, default=15,
                        help='The frame rate of the output WebP video (default: 15).')
    parser.add_argument('-v', '--video-size', type=str, default='640:360',
                        help='The size of the output WebP video (default: 640:360).')

    parser.add_argument('-w', '--max-workers', type=int, default=8,
                        help='The maximum number of workers to use (default: 8).')

    args = parser.parse_args()

    # print the arguments
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(
        f"[Images] Quality: {args.quality}, Method: {args.method}, Short Side: {args.short_side}x")
    print(f"[GIFs]   Quality: {args.gif_quality}, Method: {args.gif_method}")
    print(f"[Video]  FPS: {args.fps}, Size: {args.video_size}")
    print(f"Max Workers: {args.max_workers}\n")

    presets = {
        "image": {"quality": args.quality, "method": args.method, "short_side": args.short_side,
                  "gif_quality": args.gif_quality, "gif_method": args.gif_method},
        "video": {"fps": args.fps, "size": args.video_size}
    }

    process_zip_files(args.input_dir,
                      args.output_dir, args.max_workers)
