import os
import shutil

import JK
from lxml import html
from PIL import Image


def searchCid(num):
    try:
        javinfo = JK.web.rGET(F'https://www.tokyo-hot.com/product/?q={num}&lang=ja')
        lx = html.fromstring(javinfo.text)
        url = lx.xpath(F"//img[@title='{num}']/../@href")[0]
        cid = url.replace('product', '').replace('/', '')
        return F'https://www.tokyo-hot.com{url}?lang=ja', cid
    except:
        print(F'Get cid for {num} failed!')


def getTitle(lx):
    result = lx.xpath("""//div[@id='main']//h2/text()""")[0]
    return str(result)


def getRelease(lx):
    result = lx.xpath("""//dt[contains(text(),'配信開始日')]/following-sibling::dd[1]/text()""")[0]
    result = result.replace("/", "-")
    return str(result)


def getRuntime(lx):
    result = lx.xpath("""//dt[contains(text(),'収録時間')]/following-sibling::dd[1]/text()""")[0]
    h, m, s = result.split(':')
    mins = round(int(h) * 60 + int(m) + int(s) / 60)
    return str(mins)


def getActor(lx):
    result = lx.xpath("""//dt[contains(text(),'出演者')]/following-sibling::dd[1]/a/text()""")
    # result = ','.join(result)
    return result

# def getDirector(lx):
#     try:
#         result = lx.xpath("""//td[contains(text(),'監督：')]/following-sibling::td/a/text()""")[0]
#     except:
#         result = lx.xpath("""//td[contains(text(),'監督：')]/following-sibling::td/text()""")[0]
#     return str(result)


def getSeries(lx):
    # try:
    #     result = lx.xpath("""//dt[contains(text(),'シリーズ')]/following-sibling::dd[1]/a/text()""")[0]
    # except:
    #     result = lx.xpath("""//td[contains(text(),'シリーズ：')]/following-sibling::td/text()""")[0]
    result = lx.xpath("""//dt[contains(text(),'シリーズ')]/following-sibling::dd[1]/a/text()""")[0]
    return str(result)

# def getMaker(lx):
#     result = lx.xpath("""//td[contains(text(),'メーカー：')]/following-sibling::td/a/text()""")[0]
#     return str(result)


def getLabel(lx):
    # try:
    #     result = lx.xpath("""//td[contains(text(),'レーベル')]/following-sibling::td/a/text()""")[0]
    # except:
    #     result = lx.xpath("""//td[contains(text(),'レーベル：')]/following-sibling::td/text()""")[0]
    result = lx.xpath("""//dt[contains(text(),'レーベル')]/following-sibling::dd[1]/a/text()""")[0]
    return str(result)


def getGenre(lx):
    playContents = lx.xpath("""//dt[contains(text(),'プレイ内容')]/following-sibling::dd[1]/a/text()""")
    tags = lx.xpath("""//dt[contains(text(),'プレイ内容')]/following-sibling::dd[2]/a/text()""")
    for tag in tags:
        if tag not in playContents:
            playContents.append(tag)
    return playContents


def getCover(num, hinban):
    result = F'https://my.cdn.tokyo-hot.com/media/{hinban}/jacket/{num}.jpg'
    return str(result)


def getOutline(lx):
    result = lx.xpath(F"""//div[@class='sentence']/text()""")
    text = ''
    for i in result:
        text = F'{text}\n\n{i.strip()}'
    return str(text[2:])


def scraper(videopath, dstpath):
    # try:
    file_dir, file_name = os.path.split(videopath)
    name_main, name_ext = os.path.splitext(file_name)
    num = name_main

    tokyohot_url, cid = searchCid(num)

    HTMLdata = JK.web.rGET(tokyohot_url)
    lx = html.fromstring(HTMLdata.text)

    data = {
        "title": getTitle(lx),
        "release": getRelease(lx),
        "runtime": getRuntime(lx),
        "actor": getActor(lx),
        "director": '',
        "series": getSeries(lx),
        "maker": '',
        "label": getLabel(lx),
        "genre": getGenre(lx),
        "num": num,
        "hinban": cid,
        "outline": getOutline(lx),
        "website": HTMLdata.url,
    }

    data['cover'] = getCover(data['num'], data['hinban'])

    os.mkdir(F"""{dstpath}/[{data['num']}] ({data['release']})""")

    # download img
    IMGdata = JK.web.rGET(data['cover'])
    with open(F"""{dstpath}/[{data['num']}] ({data['release']})/{data['num']}-cover.jpg""", 'wb') as f:
        f.write(IMGdata.content)

    # cut poster
    cover = Image.open(F"""{dstpath}/[{data['num']}] ({data['release']})/{data['num']}-cover.jpg""")
    poster = cover.crop((cover.width / 1.9, 0, cover.width, cover.height))
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
    # except:
    #     print(F'Failed: {videopath}')
    #     with open(R'E:\Project\jav\meta-scraper\log.txt', 'a', encoding='utf-8') as f:
    #         f.write(videopath)
