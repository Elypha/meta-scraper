import os
import re
import shutil

import JK
from lxml import html
from PIL import Image
from loguru import logger


root_dir = os.path.split(os.path.realpath(__file__))[0]

logger.add(RF"{root_dir}/log_scraper.log", encoding='utf8', level='INFO', backtrace=True, diagnose=True)

mgs_type = ''


@logger.catch()
def get_title(lx):
    _title = lx.xpath("""//h1[@class='tag']//text()""")[0].strip()
    _title = re.sub(r'^【.+?】', '', _title)
    _title = re.sub(r'【MGSだけのおまけ映像付き.+?】', '', _title)
    title = _title
    return title


@logger.catch()
def get_release(lx):
    release = lx.xpath("""//th[contains(text(),'配信開始日：')]/following-sibling::td/text()""")[0].strip()
    release = release.replace("/", "-")
    if re.match(r'\d\d\d\d-\d\d-\d\d', release):
        return release
    release = lx.xpath("""//th[contains(text(),'商品発売日：')]/following-sibling::td/text()""")[0].strip()
    release = release.replace("/", "-")
    if re.match(r'\d\d\d\d-\d\d-\d\d', release):
        return release


@logger.catch()
def get_runtime(lx):
    runtime = lx.xpath("""//th[contains(text(),'収録時間：')]/following-sibling::td/text()""")[0]
    runtime = re.search(r"\d+", str(runtime)).group()
    if re.match(r'\d+$', runtime):
        return runtime


@logger.catch()
def get_actors(lx):
    actors = lx.xpath("""//th[contains(text(),'出演：')]/following-sibling::td//text()""")
    actors = [i.strip() for i in actors]
    for blank in ['']:
        while blank in actors:
            actors.remove(blank)
    return actors


@logger.catch()
def get_series(lx):
    _series = lx.xpath("""//th[contains(text(),'シリーズ：')]/following-sibling::td//text()""")
    _series = [i.strip() for i in _series]
    for blank in ['', '----']:
        while blank in _series:
            _series.remove(blank)
    if len(_series) == 1:
        series = _series[0]
    elif len(_series) == 0:
        series = False
    return series


@logger.catch()
def get_maker(lx):
    _maker = lx.xpath("""//th[contains(text(),'メーカー：')]/following-sibling::td//text()""")
    _maker = [i.strip() for i in _maker]
    for blank in ['', '----']:
        while blank in _maker:
            _maker.remove(blank)
    if len(_maker) == 1:
        maker = _maker[0]
    elif len(_maker) == 0:
        maker = False
    return maker


@logger.catch()
def get_label(lx):
    _label = lx.xpath("""//th[contains(text(),'レーベル：')]/following-sibling::td//text()""")
    _label = [i.strip() for i in _label]
    for blank in ['', '----']:
        while blank in _label:
            _label.remove(blank)
    if len(_label) == 1:
        label = _label[0]
    elif len(_label) == 0:
        label = False
    return label


@logger.catch()
def get_genre(lx):
    _genre = lx.xpath("""//th[contains(text(),'ジャンル：')]/following-sibling::td//text()""")
    _genre = [i.strip() for i in _genre]
    for blank in ['', '----']:
        while blank in _genre:
            _genre.remove(blank)
    genre = _genre
    return genre


@logger.catch()
def get_outline(lx):
    _outline = lx.xpath("""//dl[@id='introduction']/dd//text()""")
    _outline = [i.strip() for i in _outline]
    for blank in ['', '…すべてを見る']:
        while blank in _outline:
            _outline.remove(blank)
    outline = '\n'.join(_outline)

    return outline


@logger.catch()
def get_cover(lx):
    cover = lx.xpath("""//img[@class='enlarge_image']/@src""")[0]
    if '/pf_o1_' in cover:
        cover = cover.replace('/pf_o1_', '/pf_e_')
    return cover


@logger.catch()
def get_poster(lx):
    cover = lx.xpath("""//a[@id="EnlargeImage"]/@href""")[0]
    return cover


@logger.catch()
def scraper(videopath, dstpath, num=''):
    _, file_name = os.path.split(videopath)
    name_main, name_ext = os.path.splitext(file_name)

    # 提取有效 name
    name = name_main

    num = name.upper()

    # 获取 MGS 页面
    html_mgs = JK.web.get(F'https://www.mgstage.com/product/product_detail/{name}/', cookies={'adc': '1', 'mgs_agef': '1'})
    if html_mgs.url == 'https://www.mgstage.com/':
        print(F'该作品可能已经下架: {name}')
        return
    lx_mgs = html.fromstring(html_mgs.text)

    data = {
        "title": get_title(lx_mgs),
        "release": get_release(lx_mgs),
        "runtime": get_runtime(lx_mgs),
        "actor": get_actors(lx_mgs),
        "series": get_series(lx_mgs),
        "maker": get_maker(lx_mgs),
        "label": get_label(lx_mgs),
        "genre": get_genre(lx_mgs),
        "num": num,
        "outline": get_outline(lx_mgs),
        "website": html_mgs.url,
        "cover": get_cover(lx_mgs),
        "poster": get_poster(lx_mgs),
    }

    # make dir
    baseDir = F"{dstpath}/[{data['num']}] ({data['release']})"
    os.mkdir(baseDir)

    # download cover
    IMGdata = JK.web.get(data['cover'])
    if len(IMGdata.content) < 10000:
        print(F"Cover file size too small: {data['num']}")
        quit()
    with open(F"{baseDir}/{data['num']}-cover.jpg", 'wb') as f:
        f.write(IMGdata.content)

    # download poster
    IMGdata = JK.web.get(data['poster'])
    if len(IMGdata.content) < 10000:
        print(F"Cover file size too small: {data['num']}")
        quit()
    with open(F"{baseDir}/{data['num']}-poster.jpg", 'wb') as f:
        f.write(IMGdata.content)

    # # cut poster
    # cover = Image.open(F"{baseDir}/{data['num']}-cover.jpg")
    # if 1.45 <= cover.width / cover.height <= 1.55:
    #     poster = cover.crop((cover.width / 1.9, 0, cover.width, cover.height))
    #     poster.save(F"{baseDir}/{data['num']}-poster.png")
    # else:
    #     shutil.copyfile(F"{baseDir}/{data['num']}-cover.jpg", F"{baseDir}/{data['num']}-poster.jpg")

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
        f.write((
            F"""  <cover>{data['num']}-cover.jpg</cover>\n"""
            F"""  <poster>{data['num']}-poster.jpg</poster>\n"""
            F"""  <thumb>{data['num']}-cover.jpg</thumb>\n"""
            F"""  <fanart>{data['num']}-cover.jpg</fanart>\n"""
            F"""  <website>{data['website']}</website>\n"""
            F"""</movie>\n"""
        ))

    shutil.move(videopath, F"{baseDir}/{data['num']}{name_ext}")
