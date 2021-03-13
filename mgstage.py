import os
import re
import shutil

from PIL import Image
from lxml import html

import JK



def scraper(videopath, dstpath, num=''):
    file_dir, file_name = os.path.split(videopath)
    name_main, name_ext = os.path.splitext(file_name)

    # 处理文件名，提取有效 name
    name = name_main

    num = name

    # 获取 MGS 页面
    html_1 = JK.web.rGET(F'https://www.mgstage.com/product/product_detail/{name}/', cookies={'adc': '1'})
    lx_1 = html.fromstring(html_1.text)

    # 无效页面的 handle

    # title
    _title = lx_1.xpath("""//h1[@class='tag']//text()""")[0].strip()
    try:
        MGS_tag = re.search(r'【MGSだけのおまけ映像付き.+分】', _title).group()
        title = _title.replace(MGS_tag, '') + F' {MGS_tag}'
    except:
        title = _title

    # data matrix
    _data_raw = lx_1.xpath("""//div[@class='detail_data']/table[2]//text()""")
    _data = []
    for i in _data_raw:
        if not re.match(r'^[\s\n]*$',i):
            _data.append(i.strip())

    # release
    try:
        release = _data[_data.index('配信開始日：')+1].replace('/', '-')
    except:
        release = _data[_data.index('商品発売日：')+1].replace('/', '-')

    # runtime
    _runtime = _data[_data.index('収録時間：')+1]
    runtime = re.search(r"\d+", str(_runtime)).group()

    # actors
    try:
        actors = _data[_data.index('出演：')+1:_data.index('メーカー：')]
    except:
        actors = []

    # series
    series = _data[_data.index('シリーズ：')+1]

    # maker
    maker = _data[_data.index('メーカー：')+1]

    # label
    label = _data[_data.index('レーベル：')+1]

    # genre
    genre = _data[_data.index('ジャンル：')+1:_data.index('対応デバイス：')]

    # outline
    _outline = lx_1.xpath("""//dl[@id='introduction']/dd//text()""")
    outline = ''
    for i in _outline:
        if not re.match(r'^[\s\n]*$',i) and not '…すべてを見る' in i:
            outline = outline + i + '\n\n'

    outline = outline[:-2]

    # cover
    cover = lx_1.xpath(F"""//img[@class='enlarge_image']/@src""")[0].replace('/pf_o1_', '/pb_e_')

    data = {
        "title": title.replace('&', '/'),
        "release": release,
        "runtime": runtime,
        "actor": actors,
        "series": series.replace('&', '/'),
        "maker": maker.replace('&', '/'),
        "label": label.replace('&', '/'),
        "genre": genre,
        "num": num,
        "outline": outline.replace('&', '/'),
        "website": html_1.url,
        "cover": cover
    }

    # make dir
    baseDir = F"{dstpath}/[{data['num']}] ({data['release']})"
    os.mkdir(baseDir)

    # download cover
    IMGdata = JK.web.rGET(data['cover'])
    with open(F"{baseDir}/{data['num']}-cover.jpg", 'wb') as f:
        f.write(IMGdata.content)

    # cut poster
    cover = Image.open(F"{baseDir}/{data['num']}-cover.jpg")
    poster = cover.crop((cover.width/1.9, 0, cover.width, cover.height))
    poster.save(F"{baseDir}/{data['num']}-poster.jpg")

    # write nfo
    with open(F"{baseDir}/{data['num']}.nfo", 'w', encoding='utf-8') as f:
        f.write((
            F"""<?xml version="1.0" encoding="UTF-8" ?>\n"""
            F"""<movie>\n"""
            F"""  <title>{data['title']} [{data['num']}]</title>\n"""
            F"""  <set>\n"""
            F"""    <name>{data['series']}</name>\n"""
            F"""  </set>\n"""
            F"""  <outline>{data['outline']}</outline>\n"""
            F"""  <plot>{data['outline']}</plot>\n"""
            F"""  <premiered>{data['release']}</premiered>\n"""
            F"""  <year>{data['release']:.4}</year>\n"""
            F"""  <runtime>{data['runtime']}</runtime>\n"""
            F"""  <num>{data['num']}</num>\n"""
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

    shutil.move(videopath, F"{baseDir}/{data['num']}{name_ext}")
