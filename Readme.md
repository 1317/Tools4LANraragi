# Tools4LANraragi

> Some tools for [LANraragi](https://github.com/Difegue/LANraragi)  

## `DoABackup.py`

*You do backups, right?* 
Some how I cannot just do a backup of the LANraragi database via the webpage. So I wrote this script to backup LANraragi database using APIs. 


## `ResizeAndCompressZip.py`

Some zip archives takes too much storage space for they store high quality `jpg` / `png` images. But it's way too much for mobile reading. This script can be used to resize the images (to 2400px, by default) and compress the images in the novel image format `WebP` without sacrificing too much quality, which is expected to save up to 90% space. **(Make sure you have a backup of the original zip archive before excuting!!)**

## `LargeZipArchives.py`

This script is used together with `ResizeAndCompressZip.py` to help you find the large zip archives that need to be processed. The averaged image size of the zip archive is calculated and the archives with size larger than the threshold (per image, default is 10MB) will be listed.  