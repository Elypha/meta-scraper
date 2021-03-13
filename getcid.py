import os
import re
from lxml import html
from urllib.parse import urlencode
from PIL import Image
import shutil

import functions

from multiprocessing import Pool

import sys
sys.path.append(R'E:\Project\Python')

import JK



def reportToFile(video, report_file):
    video = video.replace('\\', '/')
    file_dir, file_name = os.path.split(video)
    name_main, name_ext = os.path.splitext(file_name)

    # 处理文件名，提取有效 name
    name = name_main

    javinfo = functions.r_post(F'https://jp.jav321.com/search', data={"sn": name})
    hinban = javinfo.url[28:]
    newName = F'{file_dir}/{hinban}{name_ext}'
    with open(report_file, 'a', encoding='utf8') as f:
        f.write(F"{video}?{newName}\n")


if __name__ == '__main__':
    # config
    rename = 1
    root_raw = R'I:\0'
    report_file = R'E:\Project\jav\meta-scraper\getcid_result.txt'

    # pre
    root_raw = root_raw.replace('\\', '/')
    videos = JK.file.findall(root_raw, ['mp4', 'mkv', 'wmv'])

    print(F'Find {len(videos)} files.\n\n')

    # main
    if rename == 1:
        with open(report_file, 'r', encoding='utf8') as f:
            reports = f.read()
        reports = reports.split('\n')
        while '' in reports:
            reports.remove('')
        for report in reports:
            video, newName = report.split('?')
            shutil.move(video, newName)
    else:
        with open(report_file, 'w', encoding='utf8') as f:
            f.truncate()

        p = Pool(24)

        for video in videos:
            p.apply_async(reportToFile, args=(video, report_file))

        p.close()
        p.join()

        with open(report_file, 'r', encoding='utf8') as f:
            reports = f.read()

        reports = reports.split('\n')
        while '' in reports:
            reports.remove('')
        reports.sort()

        with open(report_file, 'w', encoding='utf8') as f:
            f.seek(0)
            f.truncate()
            f.write('\n'.join(reports))
