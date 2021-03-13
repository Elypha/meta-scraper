import os
import re
from lxml import html
from urllib.parse import urlencode
from PIL import Image
import shutil

import functions



def scraper(videopath, dstpath):
    file_dir, file_name = os.path.split(videopath)
    name_main, name_ext = os.path.splitext(file_name)

    # 处理文件名，提取有效 name
    name = name_main

    # 根据 name 获取 hinban num
    if '-' in name:
        javinfo = functions.r_post(F'https://jp.jav321.com/search', data={"sn": name})
    else:
        javinfo = functions.r_get(F'https://jp.jav321.com/video/{name}')

    lx = html.fromstring(javinfo.text)
    info = lx.xpath("""//div[@class='col-md-9']//text()""")
    hinban = javinfo.url[28:]
    num = info[info.index('品番')+1][2:].upper()

    # 获取其余信息
    title = re.sub(r'\s*$', '', lx.xpath("""//div[@class='panel-heading']//h3/text()""")[0])
    release = info[info.index('配信開始日')+1][2:]
    runtime = info[info.index('収録時間')+1][2:].replace(' minutes', '')
    outline = lx.xpath("""//div[@class='col-md-12']//text()""")[2]
    cover = F'https://pics.dmm.co.jp/digital/video/{hinban}/{hinban}pl.jpg'
    maker = info[info.index('メーカー')+1:info.index('ジャンル')][1]

    try:
        series = info[info.index('シリーズ')+2]
    except:
        series = ''

    try:
        actors = []
        _actors1 = info[info.index('出演者')+1:info.index('メーカー')]
        _actors2 = []
        for i in _actors1:
            if '\xa0' in i:
                _actors2 = _actors2 + i.split('\xa0')
        for i in _actors2:
            actors.append(i.replace(':', '').strip())
        while '' in actors:
            actors.remove('')
    except:
        actors = []

    genre = []
    _genre = info[info.index('ジャンル')+1:info.index('品番')]
    for i in _genre:
        if i.strip() not in ['', ':']:
            genre.append(i.strip())

    data = {
        "title": title,
        "release": release,
        "runtime": runtime,
        "actor": actors,
        "director": '',
        "series": series,
        "maker": maker,
        "label": '',
        "genre": genre,
        "num": num,
        "hinban": hinban,
        "outline": outline,
        "website": javinfo.url,
        "cover": cover
    }

    os.mkdir(F"""{dstpath}/[{data['num']}] ({data['release']})""")

    # download img
    IMGdata = functions.r_get(data['cover'])
    with open(F"""{dstpath}/[{data['num']}] ({data['release']})/{data['num']}-cover.jpg""", 'wb') as f:
        f.write(IMGdata.content)

    # cut poster
    cover = Image.open(F"""{dstpath}/[{data['num']}] ({data['release']})/{data['num']}-cover.jpg""")
    poster = cover.crop((cover.width/1.9, 0, cover.width, cover.height))
    poster.save(F"""{dstpath}/[{data['num']}] ({data['release']})/{data['num']}-poster.jpg""")

    # write nfo
    with open(F"""{dstpath}/[{data['num']}] ({data['release']})/{data['num']}.nfo""", 'w', encoding='utf-8') as f:
        f.write((
            F"""<?xml version="1.0" encoding="UTF-8" ?>\n"""
            F"""<movie>\n"""
            F"""  <title>{data['title']}</title>\n"""
            F"""  <set>\n"""
            F"""    <name>{data['series']}</name>\n"""
            F"""  </set>\n"""
            F"""  <outline>{data['outline']}</outline>\n"""
            F"""  <plot>{data['outline']}</plot>\n"""
            F"""  <premiered>{data['release']}</premiered>\n"""
            F"""  <year>{data['release']:.4}</year>\n"""
            F"""  <runtime>{data['runtime']}</runtime>\n"""
            F"""  <num>{data['num']}</num>\n"""
            F"""  <hinban>{data['hinban']}</hinban>\n"""
            F"""  <director>{data['director']}</director>\n"""
            F"""  <maker>{data['maker']}</maker>\n"""
            F"""  <studio>{data['maker']}</studio>\n"""
            F"""  <label>{data['label']}</label>\n"""
            ))

        for actor in data['actor']:
            f.write((
                F"""  <actor>\n"""
                F"""    <name>{actor}</name>\n"""
                F"""  </actor>\n"""
            ))
        for genre in data['genre']:
            f.write((
                F"""  <genre>{genre}</genre>\n"""
            ))
        for genre in data['genre']:
            f.write((
                F"""  <tag>{genre}</tag>\n"""
            ))
        if data['series'] != '----':
            f.write((
                F"""  <tag>{data['series']}</tag>\n"""
            ))
        f.write((
            F"""  <cover>{data['num']}-cover.jpg</cover>\n"""
            F"""  <poster>{data['num']}-poster.jpg</poster>\n"""
            F"""  <thumb>{data['num']}-cover.jpg</thumb>\n"""
            F"""  <fanart>{data['num']}-cover.jpg</fanart>\n"""
            F"""  <website>{data['website']}</website>\n"""
            F"""</movie>\n"""
        ))

    shutil.move(videopath, F"""{dstpath}/[{data['num']}] ({data['release']})/{data['num']}{name_ext}""")

