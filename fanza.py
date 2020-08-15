import os
import re
import requests
from lxml import html
from urllib.parse import urlencode
from PIL import Image
import shutil

import functions


def getcid(num):
    try:
        javinfo = functions.r_get(F'https://www.r18.com/common/search/searchword={num}/')
        lx = html.fromstring(javinfo.text)
        item_list = lx.xpath("//div[@class='main']//li[@data-tracking_id='dmmref']/@data-content_id")
        if len(item_list) == 1:
            cid = item_list[0].strip().lower()
            return cid
        else:
            print(F'Found multiple cid for {num}')
    except:
        print(F'Get cid for {num} failed!')


def getnum(cid):
    try:
        javinfo = functions.r_get(F'https://www.r18.com/videos/vod/movies/detail/-/id={cid}/')
        lx = html.fromstring(javinfo.text)
        num = lx.xpath("//div[@class='main']//dt[contains(text(),'DVD ID:')]/following-sibling::dd/text()")[0].strip().upper()
        return num
    except:
        print(F'Get num for {cid} failed!')


def getHinban(lx):
    result = lx.xpath("""//td[contains(text(),'品番：')]/following-sibling::td/text()""")[0].lower()
    return str(result)

def getTitle(lx):
    result = lx.xpath("""//h1[@id='title']/text()""")[0]
    return str(result)

def getRelease(lx):
    result = lx.xpath("""//td[contains(text(),'配信開始日：')]/following-sibling::td/text()""")[0]
    result = result.lstrip("\n").replace("/", "-")
    return str(result)

def getRuntime(lx):
    result = lx.xpath("""//td[contains(text(),'収録時間：')]/following-sibling::td/text()""")[0]
    result = re.search(r"\d+", str(result)).group()
    return str(result)

def getActor(lx):
    result = lx.xpath("""//td[contains(text(),'出演者：')]/following-sibling::td/span/a/text()""")
    # result = ','.join(result)
    return result

def getDirector(lx):
    try:
        result = lx.xpath("""//td[contains(text(),'監督：')]/following-sibling::td/a/text()""")[0]
    except:
        result = lx.xpath("""//td[contains(text(),'監督：')]/following-sibling::td/text()""")[0]
    return str(result)

def getSeries(lx):
    try:
        result = lx.xpath("""//td[contains(text(),'シリーズ：')]/following-sibling::td/a/text()""")[0]
    except:
        result = lx.xpath("""//td[contains(text(),'シリーズ：')]/following-sibling::td/text()""")[0]
    return str(result)

def getMaker(lx):
    result = lx.xpath("""//td[contains(text(),'メーカー：')]/following-sibling::td/a/text()""")[0]
    return str(result)

def getLabel(lx):
    try:
        result = lx.xpath("""//td[contains(text(),'レーベル：')]/following-sibling::td/a/text()""")[0]
    except:
        result = lx.xpath("""//td[contains(text(),'レーベル：')]/following-sibling::td/text()""")[0]
    return str(result)

def getGenre(lx):
    result = lx.xpath("""//td[contains(text(),'ジャンル：')]/following-sibling::td/a/text()""")
    # result = ','.join(result)
    return result

def getCover(lx, hinban):
    result = lx.xpath(F"""//a[@id='{hinban}']/@href""")[0]
    return str(result)

def getOutline(lx):
    result = lx.xpath(F"""//div[@class='mg-b20 lh4']/text()""")[0].strip()
    return str(result)


def scraper(videopath, dstpath):
    try:
        file_dir, file_name = os.path.split(videopath)
        name_main, name_ext = os.path.splitext(file_name)
        cid = getcid(name_main) if '-' in name_main else name_main

        fanza_url = F'https://www.dmm.co.jp/digital/videoa/-/detail/=/cid={cid}'
        dmm_url = 'https://www.dmm.co.jp/age_check/=/declared=yes/?' + urlencode({"rurl": fanza_url})

        HTMLdata = functions.r_get(dmm_url)
        lx = html.fromstring(HTMLdata.text)

        data = {
            "title": getTitle(lx),
            "release": getRelease(lx),
            "runtime": getRuntime(lx),
            "actor": getActor(lx),
            "director": getDirector(lx),
            "series": getSeries(lx),
            "maker": getMaker(lx),
            "label": getLabel(lx),
            "genre": getGenre(lx),
            "num": getnum(cid),
            "hinban": getHinban(lx),
            "outline": getOutline(lx),
            "website": HTMLdata.url,
        }

        data['cover'] = getCover(lx, data['hinban'])

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
    except:
        print(F'Failed: {videopath}')
        with open(R'E:\Project\jav\meta-scraper\log.txt', 'a', encoding='utf-8') as f:
            f.write(videopath)
        return
