import os
import re
import shutil
from io import BytesIO

import JK
from lxml import html
from PIL import Image
from loguru import logger


root_dir = os.path.split(os.path.realpath(__file__))[0]

headers_jav321 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Host': 'jp.jav321.com',
    'Origin': 'https://jp.jav321.com',
    'Referer': 'https://jp.jav321.com/'
}

cookies_jav321 = {
    'is_loyal': '1'
}

logger.add(RF"{root_dir}/log_scraper.log", encoding='utf8', level='INFO', backtrace=True, diagnose=True)


@logger.catch()
def get_title(lx):
    title = lx.xpath("""//div[@class='panel-heading']//h3/text()""")[0].strip()
    return title


@logger.catch()
def scraper(videopath, dstpath):
    global dmm_type

    _, file_name = os.path.split(videopath)
    name_main, name_ext = os.path.splitext(file_name)

    # 提取有效 name
    name = name_main

    # 检测手动模式
    if name_main.startswith('#'):
        num, hinban = name_main[1:].split('#')
    # 否则根据 name 获取 hinban num
    else:
        if '-' in name:
            html_jav321 = JK.web.post('https://jp.jav321.com/search', data={"sn": name}, headers=headers_jav321, cookies=cookies_jav321)
            lx_jav321 = html.fromstring(html_jav321.text)
            jav321 = lx_jav321.xpath("""//div[@class='col-md-9']//text()""")
            num = name.upper()
            hinban = html_jav321.url[28:]
        else:
            html_jav321 = JK.web.get(F'https://jp.jav321.com/video/{name}', headers=headers_jav321, cookies=cookies_jav321)
            lx_jav321 = html.fromstring(html_jav321.text)
            jav321 = lx_jav321.xpath("""//div[@class='col-md-9']//text()""")
            num = jav321[jav321.index('品番') + 1][2:].upper()  # jav321的品番其实是num
            hinban = name

    html_javbus = JK.web.get(F'https://www.javbus.com/ja/{num}')
    lx_javbus = html.fromstring(html_javbus.text)

    # 抓取属性
    release = lx_javbus.xpath("""//span[contains(text(),'発売日:')]/../text()""")[0].strip()
    runtime = lx_javbus.xpath("""//span[contains(text(),'収録時間:')]/../text()""")[0].strip()[:-1]
    actors = lx_javbus.xpath("""//span[contains(text(),'出演者')]/../following-sibling::*[2]//text()""")
    actors = [i.strip() for i in actors]
    for blank in ['', ':']:
        while blank in actors:
            actors.remove(blank)
    director = lx_javbus.xpath("""//span[contains(text(),'監督:')]/following-sibling::*[1]/text()""")
    if len(director) == 1:
        director = director[0].strip()
    series = lx_javbus.xpath("""//span[contains(text(),'シリーズ:')]/following-sibling::*[1]/text()""")
    if len(series) == 1:
        series = series[0].strip()
    maker = lx_javbus.xpath("""//span[contains(text(),'メーカー:')]/following-sibling::*[1]/text()""")[0].strip()
    label = lx_javbus.xpath("""//span[contains(text(),'レーベル:')]/following-sibling::*[1]/text()""")[0].strip()
    genre = lx_javbus.xpath("""//p/span[@class='genre']//label//text()""")[0].strip()
    outline = lx_jav321.xpath("""//div[@class='panel-body']//div[@class='col-md-12']/text()""")[0].strip()
    cover = lx_jav321.xpath("""//div[@class='col-xs-12 col-md-12']//img/@src""")[0].strip()

    data = {
        "title": get_title(lx_jav321),
        "release": release,
        "runtime": runtime,
        "actor": actors,
        "director": director,
        "series": series,
        "maker": maker,
        "label": label,
        "genre": genre,
        "num": num,
        "hinban": hinban,
        "outline": outline,
        "cover": cover,
        "website": html_jav321.url,
    }

    # make dir
    baseDir = F"{dstpath}/[{data['num']}][{data['hinban']}] ({data['release']})"
    os.mkdir(baseDir)

    # download cover
    IMGdata = JK.web.get(data['cover'])
    if len(IMGdata.content) < 10000:
        print(F"Cover file size too small: {data['num']}")
        quit()
    with open(F"{baseDir}/{data['num']}-cover.jpg", 'wb') as f:
        f.write(IMGdata.content)

    # cut poster
    cover = Image.open(F"{baseDir}/{data['num']}-cover.jpg")
    if 1.45 <= cover.width / cover.height <= 1.55:
        poster = cover.crop((cover.width / 1.9, 0, cover.width, cover.height))
        poster.save(F"{baseDir}/{data['num']}-poster.png")
    else:
        try:
            # https://pics.dmm.co.jp/digital/video/1stars00347/1stars00347pl.jpg イメージ封面大图
            # https://pics.dmm.co.jp/digital/video/1stars00347/1stars00347jp-1.jpg サンプル画像#1
            poster = JK.web.get(F"https://pics.dmm.co.jp/digital/video/{data['hinban']}/{data['hinban']}jp-1.jpg")
            if poster.status_code != 200 or len(poster.content) < 10000:
                print(F"[{data['num']}] イメージ Cover 不符合标准，获取サンプル画像#1失败")
                raise Exception
            RAM_poster = BytesIO()
            RAM_poster.write(poster.content)
            poster = Image.open(RAM_poster)
            if 1.37 <= poster.height / poster.width <= 1.47:
                poster.save(F"{baseDir}/{data['num']}-poster.jpg")
            else:
                print(F"[{data['num']}] イメージ Cover 不符合标准，获取サンプル画像#1成功，サンプル画像#1尺寸不符合要求")
                raise Exception
        except:
            shutil.copyfile(F"{baseDir}/{data['num']}-cover.jpg", F"{baseDir}/{data['num']}-poster.jpg")

    # write nfo
    with open(F"{baseDir}/{data['num']}.nfo", 'w', encoding='utf-8') as f:
        f.write((
            F"""<?xml version="1.0" encoding="UTF-8" ?>\n"""
            F"""<movie>\n"""
            F"""  <title>{data['title']} [{data['num']}]</title>\n"""
            F"""  <outline>{data['outline']}</outline>\n"""
            F"""  <plot>{data['outline']}</plot>\n"""
            F"""  <year>{data['release']:.4}</year>\n"""
            F"""  <premiered>{data['release']}</premiered>\n"""
            F"""  <runtime>{data['runtime']}</runtime>\n"""
            F"""  <num>{data['num']}</num>\n"""
            F"""  <hinban>{data['hinban']}</hinban>\n"""
        ))
        for actor in data['actor']:
            f.write((
                F"""  <actor>\n"""
                F"""    <name>{actor.strip()}</name>\n"""
                F"""  </actor>\n"""
            ))
        for genre in data['genre']:
            f.write((
                F"""  <genre>{genre.strip()}</genre>\n"""
            ))
        for genre in data['genre']:
            f.write((
                F"""  <tag>{genre.strip()}</tag>\n"""
            ))
        if data['series']:
            f.write((
                F"""  <set>\n"""
                F"""    <name>{data['series']}</name>\n"""
                F"""  </set>\n"""
                F"""  <tag>{data['series']}</tag>\n"""
                F"""  <genre>{data['series']}</genre>\n"""
            ))
        if data['maker']:
            f.write((
                F"""  <maker>{data['maker']}</maker>\n"""
                F"""  <studio>{data['maker']}</studio>\n"""
            ))
        if data['label']:
            f.write((
                F"""  <label>{data['label']}</label>\n"""
            ))
        if data['director']:
            f.write((
                F"""  <director>{data['director']}</director>\n"""
            ))
        f.write((
            F"""  <cover>{data['num']}-cover.jpg</cover>\n"""
            F"""  <poster>{data['num']}-poster.png</poster>\n"""
            F"""  <thumb>{data['num']}-cover.jpg</thumb>\n"""
            F"""  <fanart>{data['num']}-cover.jpg</fanart>\n"""
            F"""  <website>{data['website']}</website>\n"""
            F"""</movie>\n"""
        ))

    shutil.move(videopath, F"{baseDir}/{data['num']}{name_ext}")
