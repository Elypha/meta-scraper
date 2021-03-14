import os
import re
import shutil

from PIL import Image
from lxml import html

import JK



def get_title(lx):
    try: # DVD/配信
        _title = lx.xpath("""//h1[@class='tag']//text()""")[0].strip()
        try:
            MGS_tag = re.search(r'【MGSだけのおまけ映像付き.+分】', _title).group()
            title = _title.replace(MGS_tag, '') + F' {MGS_tag}'
        except:
            title = _title
    except:
        title = '----'
    return title

def get_release(lx):
    try: # DVD/配信
        release = lx.xpath("""//th[contains(text(),'商品発売日：')]/following-sibling::td/text()""")[0].strip()
        if not re.match(r'\d', release):
            raise Exception
    except:
        try:
            release = lx.xpath("""//th[contains(text(),'配信開始日：')]/following-sibling::td/text()""")[0].strip()
            if not re.match(r'\d', release):
                raise Exception
        except:
            release = ''
    return release.replace("/", "-")

def get_runtime(lx):
    try: # DVD/配信
        runtime = lx.xpath("""//th[contains(text(),'収録時間：')]/following-sibling::td/text()""")[0]
        runtime = re.search(r"\d+", str(runtime)).group()
        if not re.match(r'\d', runtime):
            raise Exception
    except:
        runtime = ''
    return runtime

def get_actors(lx):
    try: # DVD/配信
        _actors = lx.xpath("""//th[contains(text(),'出演：')]/following-sibling::td//text()""")
        actors = []
        for i in _actors:
            if i.strip() != '':
                actors.append(i.strip())
    except:
        actors = []
    return actors

def get_series(lx):
    try: # DVD/配信
        _series = lx.xpath("""//th[contains(text(),'シリーズ：')]/following-sibling::td//text()""")
        for i in _series:
            if i.strip() != '':
                return i.strip()
        return ''
    except:
        return ''

def get_maker(lx):
    try: # DVD/配信
        _maker = lx.xpath("""//th[contains(text(),'メーカー：')]/following-sibling::td//text()""")
        for i in _maker:
            if i.strip() != '':
                return i.strip()
        return ''
    except:
        return ''

def get_label(lx):
    try: # DVD/配信
        _label = lx.xpath("""//th[contains(text(),'レーベル：')]/following-sibling::td//text()""")
        for i in _label:
            if i.strip() != '':
                return i.strip()
        return ''
    except:
        return ''

def get_genre(lx):
    try: # DVD/配信
        _genre = lx.xpath("""//th[contains(text(),'ジャンル：')]/following-sibling::td//text()""")
        genre = []
        for i in _genre:
            if i.strip() != '':
                genre.append(i.strip())
    except:
        genre = []
    return genre

def get_outline(lx):
    try: # DVD/配信
        _outline = lx.xpath("""//dl[@id='introduction']/dd//text()""")
        outline = ''
        for i in _outline:
            if not re.match(r'^[\s\n]*$',i) and not '…すべてを見る' in i:
                outline = outline + i + '\n\n'

        outline = outline[:-2]
    except:
        outline = ''
    return outline

def get_cover(lx):
    try: # DVD/配信
        cover = lx.xpath(F"""//img[@class='enlarge_image']/@src""")[0]
        if '/pf_o1_' in cover:
            cover = cover.replace('/pf_o1_', '/pb_e_')
        elif '/pb_p_' in cover:
            cover = cover.replace('/pb_p_', '/pb_e_')
    except:
        cover = ''
    return cover


def scraper(videopath, dstpath, num=''):
    file_dir, file_name = os.path.split(videopath)
    name_main, name_ext = os.path.splitext(file_name)

    # 处理文件名，提取有效 name
    name = name_main

    num = name

    # 获取 MGS 页面
    html_mgs = JK.web.rGET(F'https://www.mgstage.com/product/product_detail/{name}/', cookies={'adc': '1'})
    lx_mgs = html.fromstring(html_mgs.text)

    # 无效页面的 handle
    title = get_title(lx_mgs)
    release = get_release(lx_mgs)
    runtime = get_runtime(lx_mgs)
    actors = get_actors(lx_mgs)
    series = get_series(lx_mgs)
    maker = get_maker(lx_mgs)
    label = get_label(lx_mgs)
    genre = get_genre(lx_mgs)
    outline = get_outline(lx_mgs)
    cover = get_cover(lx_mgs)

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
        "website": html_mgs.url,
        "cover": cover
    }

    # make dir
    baseDir = F"{dstpath}/[{data['num']}] ({data['release']})"
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
