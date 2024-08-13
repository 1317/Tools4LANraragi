# Tools4LANraragi

> Some tools for [LANraragi](https://github.com/Difegue/LANraragi)  

## `DoABackup.py`

*You do backups, right?* 
Some how I cannot just do a backup of the LANraragi database via the webpage. So I wrote this script to backup LANraragi database using APIs. 


## `ResizeAndCompressZip.py`

Some zip archives takes too much storage space for they store high quality `jpg` / `png` images. But it's way too much for mobile reading. This script can be used to resize the images (to 2400px, by default) and compress the images in the novel image format `WebP` without sacrificing too much quality, which is expected to save up to 90% space. **(Make sure you have a backup of the original zip archive before excuting!!)**

Supported process:
- Resize and compress static images(`jpg`, `png`, etc.) to `WebP` format.
- Compress animated images(`gif`) to `WebP` format.
- Convert short videos(`mp4`, etc.) to `WebP` format (so you can watch them directly in the reader).

Usage:
```shell
ResizeAndCompressZip.py [-h] [-i INPUT_DIR] [-o OUTPUT_DIR] [-q IMAGE_QUALITY] [-m IMAGE_METHOD]
                               [-s SHORT_SIDE] [-Q GIF_QUALITY] [-M GIF_METHOD] [-f FPS] [-v VIDEO_SIZE]
                               [-w MAX_WORKERS]

Process and compress images in ZIP files.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input-dir INPUT_DIR
                        The directory containing the input ZIP files (default: ./input).
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        The directory where the output ZIP files will be saved (default: ./output).
  -q IMAGE_QUALITY, --quality IMAGE_QUALITY
                        The quality of the compressed images (default: 80).
  -m IMAGE_METHOD, --method IMAGE_METHOD
                        The compression method for images (default: 6).
  -s SHORT_SIDE, --short-side SHORT_SIDE
                        The length of the shorter side of the image (px) (default: 2400).
  -Q GIF_QUALITY, --gif-quality GIF_QUALITY
                        The quality of the compressed GIF images (default: 80).
  -M GIF_METHOD, --gif-method GIF_METHOD
                        The compression method for GIF images (default: 4).
  -f FPS, --fps FPS     The frame rate of the output WebP video (default: 15).
  -v VIDEO_SIZE, --video-size VIDEO_SIZE
                        The size of the output WebP video (default: 640:360).
  -w MAX_WORKERS, --max-workers MAX_WORKERS
                        The maximum number of workers to use (default: 8).
```

## `LargeZipArchives.py`

This script is used together with `ResizeAndCompressZip.py` to help you find the large zip archives that need to be processed. The averaged image size of the zip archive is calculated and the archives with size larger than the threshold (per image, 5MB by default) will be listed.  