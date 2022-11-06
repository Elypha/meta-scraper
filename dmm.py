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

dmm_type = ''


@logger.catch()
def get_title(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc', 'dvd']:
        title = lx.xpath("""//h1[@id='title']/text()""")[0]
    return title


@logger.catch()
def get_release(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc']:
        release = lx.xpath("""//td[contains(text(),'配信開始日：')]/following-sibling::td/text()""")[0].strip()
        release = release.replace("/", "-")
        if re.match(r'\d\d\d\d-\d\d-\d\d', release):
            return release
        release = lx.xpath("""//td[contains(text(),'商品発売日：')]/following-sibling::td/text()""")[0].strip()
        release = release.replace("/", "-")
        if re.match(r'\d\d\d\d-\d\d-\d\d', release):
            return release
    if dmm_type in ['dvd']:
        release = lx.xpath("""//td[contains(text(),'発売日：')]/following-sibling::td/text()""")[0].strip()
        release = release.replace("/", "-")
        if re.match(r'\d\d\d\d-\d\d-\d\d', release):
            return release


@logger.catch()
def get_runtime(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc', 'dvd']:
        runtime = lx.xpath("""//td[contains(text(),'収録時間：')]/following-sibling::td/text()""")[0]
        runtime = re.search(r"\d+", str(runtime)).group()
        if re.match(r'\d+$', runtime):
            return runtime


@logger.catch()
def get_actors(lx, dmm_type, html_dmm=False):
    if dmm_type in ['videoa']:
        actors = lx.xpath("""//td[contains(text(),'出演者：')]/following-sibling::td/span/a/text()""")
        if '▼すべて表示する' in actors:
            actors_data = re.findall(r"url: '/digital/videoa/-/(.+?)',", html_dmm.text)
            actors_data = JK.web.get(F'https://www.dmm.co.jp/digital/videoa/-/{actors_data[0]}')
            actors = re.findall(r'>(.+?)<', actors_data.text)
    if dmm_type in ['videoc']:
        actors = lx.xpath("""//td[contains(text(),'名前：')]/following-sibling::td//text()""")
    if dmm_type in ['dvd']:
        actors = lx.xpath("""//td[contains(text(),'出演者：')]/following-sibling::td//text()""")
    actors = [i.strip() for i in actors]
    for blank in ['', '----']:
        while blank in actors:
            actors.remove(blank)
    return actors


@logger.catch()
def get_director(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc', 'dvd']:
        _director = lx.xpath("""//td[contains(text(),'監督：')]/following-sibling::td//text()""")
    _director = [i.strip() for i in _director]
    for blank in ['', '----']:
        while blank in _director:
            _director.remove(blank)
        director = _director
    return director


@logger.catch()
def get_series(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc', 'dvd']:
        _series = lx.xpath("""//td[contains(text(),'シリーズ：')]/following-sibling::td//text()""")
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
def get_maker(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc', 'dvd']:
        _maker = lx.xpath("""//td[contains(text(),'メーカー：')]/following-sibling::td//text()""")
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
def get_label(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc', 'dvd']:
        _label = lx.xpath("""//td[contains(text(),'レーベル：')]/following-sibling::td//text()""")
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
def get_genre(lx, dmm_type):
    if dmm_type in ['videoa', 'videoc', 'dvd']:
        _genre = lx.xpath("""//td[contains(text(),'ジャンル：')]/following-sibling::td//text()""")
    _genre = [i.strip() for i in _genre]
    for blank in ['', '----']:
        while blank in _genre:
            _genre.remove(blank)
    genre = _genre
    return genre


@logger.catch()
def get_outline(lx, dmm_type):
    if dmm_type in ['videoa']:
        outline = lx.xpath("""//div[@class='mg-b20 lh4']/text()""")[0].strip()
    if dmm_type in ['videoc']:
        outlineList = lx.xpath("""//div[@class='mg-b20 lh4']//text()""")
        outlineList = [i.strip() for i in outlineList]
        outline = '\n'.join(outlineList)
        outline = outline.strip()
    if dmm_type in ['dvd']:
        outline = lx.xpath("""//p[@class='mg-b20']/text()""")[0].strip()
    return outline


@logger.catch()
def get_cover(lx, dmm_type):
    if dmm_type in ['videoa', 'dvd']:
        cover = lx.xpath("""//a[@name='package-image']/@href""")[0]
    if dmm_type in ['videoc']:
        cover = lx.xpath("""//div[@id='sample-video']/img/@src""")[0]
    return cover


@logger.catch()
def get_dmm(URL_cid):
    # dmm videoa
    url = F'https://www.dmm.co.jp/digital/videoa/-/detail/=/cid={URL_cid}/'
    html_dmm = JK.web.get(url, cookies={"age_check_done": "1"})
    if 200 <= html_dmm.status_code <= 299:
        return (html_dmm, 'videoa')
    # dmm videoc
    url = F'https://www.dmm.co.jp/digital/videoc/-/detail/=/cid={URL_cid}/'
    html_dmm = JK.web.get(url, cookies={"age_check_done": "1"})
    if 200 <= html_dmm.status_code <= 299:
        return (html_dmm, 'videoc')
    # dmm dvd
    url = F'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid={URL_cid}/'
    html_dmm = JK.web.get(url, cookies={"age_check_done": "1"})
    if 200 <= html_dmm.status_code <= 299:
        return (html_dmm, 'dvd')
    # ERROR
    print(F'该作品可能已经下架: {URL_cid}')
    return False, False


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
    # 否则根据 name 从 jav321 获取 hinban num
    else:
        if '-' in name:
            html_jav321 = JK.web.post('https://jp.jav321.com/search', data={"sn": name}, headers=headers_jav321, cookies=cookies_jav321)
        else:
            html_jav321 = JK.web.get(F'https://jp.jav321.com/video/{name}', headers=headers_jav321, cookies=cookies_jav321)

        lx_jav321 = html.fromstring(html_jav321.text)
        jav321 = lx_jav321.xpath("""//div[@class='col-md-9']//text()""")

        hinban = html_jav321.url[28:]
        num = jav321[jav321.index('品番') + 1][2:].upper()  # jav321的品番其实是num

    URL_cid = hinban
    html_dmm, dmm_type = get_dmm(URL_cid)
    if not html_dmm:
        return
    lx_dmm = html.fromstring(html_dmm.text)

    data = {
        "title": get_title(lx_dmm, dmm_type),
        "release": get_release(lx_dmm, dmm_type),
        "runtime": get_runtime(lx_dmm, dmm_type),
        "actor": get_actors(lx_dmm, dmm_type, html_dmm),
        "director": get_director(lx_dmm, dmm_type),
        "series": get_series(lx_dmm, dmm_type),
        "maker": get_maker(lx_dmm, dmm_type),
        "label": get_label(lx_dmm, dmm_type),
        "genre": get_genre(lx_dmm, dmm_type),
        "num": num,
        "hinban": hinban,
        "outline": get_outline(lx_dmm, dmm_type),
        "cover": get_cover(lx_dmm, dmm_type),
        "website": html_dmm.url,
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
        for director in data['director']:
            f.write((
                F"""  <director>{director.strip()}</director>\n"""
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
            F"""  <poster>{data['num']}-poster.png</poster>\n"""
            F"""  <thumb>{data['num']}-cover.jpg</thumb>\n"""
            F"""  <fanart>{data['num']}-cover.jpg</fanart>\n"""
            F"""  <website>{data['website']}</website>\n"""
            F"""</movie>\n"""
        ))

    shutil.move(videopath, F"{baseDir}/{data['num']}{name_ext}")
