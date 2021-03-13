import os
import re
import shutil

from PIL import Image
from lxml import html
from urllib.parse import urlencode

import JK



def get_title(lx):
    try: # DMM-A/dmmc
        title = lx.xpath("""//h1[@id='title']/text()""")[0]
    except:
        title = '----'
    return title

def get_release(lx):
    try: # DMM-A/dmmc
        release = lx.xpath("""//td[contains(text(),'商品発売日：')]/following-sibling::td/text()""")[0]
    except:
        try: # DMM-A/dmmc
            release = lx.xpath("""//td[contains(text(),'配信開始日：')]/following-sibling::td/text()""")[0]
        except:
            release = ''
    if release == '----':
        release = ''
    return release.strip().replace("/", "-")

def get_runtime(lx):
    try: # DMM-A/dmmc
        runtime = lx.xpath("""//td[contains(text(),'収録時間：')]/following-sibling::td/text()""")[0]
        runtime = re.search(r"\d+", str(runtime)).group()
    except:
        runtime = ''
    if runtime == '----':
        runtime = ''
    return runtime

def get_actors(lx, html=''):
    try: # DMM-A
        actors = lx.xpath("""//td[contains(text(),'出演者：')]/following-sibling::td/span/a/text()""")
        if actors == []: # DMM-C
            actors = lx.xpath("""//td[contains(text(),'名前：')]/following-sibling::td//text()""")
        else:
            if '▼すべて表示する' in actors:
                actors_data = re.findall(r"url: '/digital/videoa/-/(.+?)',", html.text)
                actors_data = JK.web.rGET(F'https://www.dmm.co.jp/digital/videoa/-/{actors_data[0]}')
                actors = re.findall(r'>(.+?)<', actors_data.text)
    except:
        actors = []
    if actors == '----':
        actors = []
    return actors

def get_director(lx):
    try: # DMM-A
        director = lx.xpath("""//td[contains(text(),'監督：')]/following-sibling::td/a/text()""")[0]
    except:
        try:
            director = lx.xpath("""//td[contains(text(),'監督：')]/following-sibling::td/text()""")[0]
        except:
            director = ''
    if director == '----':
        director = ''
    return director

def get_series(lx):
    try: # DMM-A
        series = lx.xpath("""//td[contains(text(),'シリーズ：')]/following-sibling::td/a/text()""")[0]
    except:
        try:
            series = lx.xpath("""//td[contains(text(),'シリーズ：')]/following-sibling::td/text()""")[0]
        except:
            series = ''
    if series == '----':
        series = ''
    return series

def get_maker(lx):
    try: # DMM-A
        maker = lx.xpath("""//td[contains(text(),'メーカー：')]/following-sibling::td/a/text()""")[0]
    except:
        try:
            maker = lx.xpath("""//td[contains(text(),'メーカー：')]/following-sibling::td/text()""")[0]
        except:
            maker = ''
    if maker == '----':
        maker = ''
    return maker

def get_label(lx):
    try: # DMM-A
        label = lx.xpath("""//td[contains(text(),'レーベル：')]/following-sibling::td/a/text()""")[0]
    except:
        try:
            label = lx.xpath("""//td[contains(text(),'レーベル：')]/following-sibling::td/text()""")[0]
        except:
            label = ''
    if label == '----':
        label = ''
    return label

def get_genre(lx):
    try: # DMM-A
        genre = lx.xpath("""//td[contains(text(),'ジャンル：')]/following-sibling::td/a/text()""")
    except:
        try:
            genre = lx.xpath("""//td[contains(text(),'ジャンル：')]/following-sibling::td/text()""")
        except:
            genre = []
    if genre == '----':
        genre = []
    return genre

def get_outline(lx):
    try: # DMM-A
        outline = lx.xpath(F"""//div[@class='mg-b20 lh4']/text()""")[0].strip()
        if outline == '': # DMM-C
            outlineList = lx.xpath(F"""//div[@class='mg-b20 lh4']//text()""")
            outline = ''.join(outlineList)
            outline = outline.lstrip().rstrip()
    except:
        outline = ''
    if outline == '----':
        outline = ''
    return outline

def get_cover(lx):
    try: # DMM-A
        cover = lx.xpath(F"""//a[@name='package-image']/@href""")[0]
    except:
        try: # DMM-C
            cover = lx.xpath(F"""//div[@id='sample-video']/img/@src""")[0]
        except:
            cover = ''
    return cover



def scraper(videopath, dstpath, hinban='', num=''):
    file_dir, file_name = os.path.split(videopath)
    name_main, name_ext = os.path.splitext(file_name)

    # 处理文件名，提取有效 name
    name = name_main

    # 根据 name 从 jav321 获取 hinban num
    if hinban == '' and num == '':
        if '-' in name:
            html_jav321 = JK.web.rPOST(F'https://jp.jav321.com/search', data={"sn": name})
        else:
            html_jav321 = JK.web.rGET(F'https://jp.jav321.com/video/{name}')

        lx_jav321 = html.fromstring(html_jav321.text)
        jav321 = lx_jav321.xpath("""//div[@class='col-md-9']//text()""")

        hinban = html_jav321.url[28:]
        num = jav321[jav321.index('品番')+1][2:].upper() # jav321的品番其实是num

    dmma_url = F'https://www.dmm.co.jp/digital/videoa/-/detail/=/cid={hinban}'
    html_dmma = JK.web.rGET(dmma_url, cookies={"age_check_done": "1"})

    if '指定されたページが見つかりません' not in html_dmma.text:
        lx_dmma = html.fromstring(html_dmma.text)

        title = get_title(lx_dmma)
        release = get_release(lx_dmma)
        runtime = get_runtime(lx_dmma)
        actors = get_actors(lx_dmma, html_dmma)
        director = get_director(lx_dmma)
        series = get_series(lx_dmma)
        maker = get_maker(lx_dmma)
        label = get_label(lx_dmma)
        genre = get_genre(lx_dmma)
        outline = get_outline(lx_dmma)
        cover = get_cover(lx_dmma)
        website = html_dmma.url

    else:
        dmmc_url = F'https://www.dmm.co.jp/digital/videoc/-/detail/=/cid={hinban}'
        html_dmmc = JK.web.rGET(dmmc_url, cookies={"age_check_done": "1"})

        if '指定されたページが見つかりません' not in html_dmmc.text:
            lx_dmmc = html.fromstring(html_dmmc.text)

            title = get_title(lx_dmmc)
            release = get_release(lx_dmmc)
            runtime = get_runtime(lx_dmmc)
            actors = get_actors(lx_dmmc)
            director = ''
            series = ''
            maker = ''
            label = get_label(lx_dmmc)
            genre = get_genre(lx_dmmc)
            outline = get_outline(lx_dmmc)
            cover = get_cover(lx_dmmc)
            website = html_dmmc.url

        else:
            title = lx_jav321.xpath("""//div[@class='panel-heading']//h3/text()""")[0]
            title = re.sub(r'\s*$', '', title)
            release = jav321[jav321.index('配信開始日')+1][2:]
            runtime = jav321[jav321.index('収録時間')+1][2:].replace(' minutes', '')

            try:
                actors = []
                _actors1 = jav321[jav321.index('出演者')+1:jav321.index('メーカー')]
                _actors2 = []
                for i in _actors1:
                    if '\xa0' in i:
                        _actors2 = _actors2 + i.split('\xa0')
                for i in _actors2:
                    actors.append(i.replace(':', '').strip())
                while '' in actors:
                    actors.remove('')
            except:
                actors = ['']

            try:
                series = jav321[jav321.index('シリーズ')+2]
            except:
                series = ''

            maker = jav321[jav321.index('メーカー')+1:jav321.index('ジャンル')][1]

            genre = []
            _genre = jav321[jav321.index('ジャンル')+1:jav321.index('品番')]
            for i in _genre:
                if i.strip() not in ['', ':']:
                    genre.append(i.strip())

            outline = lx_jav321.xpath("""//div[@class='col-md-12']//text()""")[2]

            cover = F'https://pics.dmm.co.jp/digital/video/{hinban}/{hinban}pl.jpg'

            # javbus
            html_dmmc = JK.web.rGET(F'https://www.javbus.com/ja/{num}')
            lx_dmmc = html.fromstring(html_dmmc.text)
            _javbus = lx_dmmc.xpath("""//div[@class='col-md-3 info']//text()""")

            try:
                director = _javbus[_javbus.index('監督:')+2]
            except:
                director = ''

            try:
                label = _javbus[_javbus.index('レーベル:')+2]
            except:
                label = ''


    data = {
        "title": title,
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
        "website": website,
        "cover": cover
    }

    # make dir
    baseDir = F"{dstpath}/[{data['num']}][{data['hinban']}] ({data['release']})"
    os.mkdir(baseDir)

    # download cover
    IMGdata = JK.web.rGET(data['cover'])
    if len(IMGdata.content) < 10000:
        print(F"Get Cover ERROR! {data['num']}")
        quit()
    with open(F"{baseDir}/{data['num']}-cover.jpg", 'wb') as f:
        f.write(IMGdata.content)

    # cut poster
    cover = Image.open(F"{baseDir}/{data['num']}-cover.jpg")
    if 1.45 <= cover.width/cover.height <= 1.55:
        poster = cover.crop((cover.width/1.9, 0, cover.width, cover.height))
        poster.save(F"{baseDir}/{data['num']}-poster.jpg")
    else:
        shutil.copyfile(F"{baseDir}/{data['num']}-cover.jpg", F"{baseDir}/{data['num']}-poster.jpg")

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
            F"""  <hinban>{data['hinban']}</hinban>\n"""
            F"""  <director>{data['director']}</director>\n"""
            F"""  <maker>{data['maker']}</maker>\n"""
            F"""  <studio>{data['maker']}</studio>\n"""
            F"""  <label>{data['label']}</label>\n"""
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
        if data['series'] != '':
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