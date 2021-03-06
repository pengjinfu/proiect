"""
抓取豆瓣top260电影
库： aitohttp + asyncio
"""
import os
import asyncio
import aiohttp
from lxml import etree
import json
import re
import pymysql

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.170'
}

db = pymysql.connect(host="localhost",port =3306, user="root",password="302811",database="gaokao",charset="utf8" )
cursor = db.cursor()

async def getUrl(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url = url, headers = headers) as resp:
            if resp.status == 200 :
                html = await resp.text()
                print(html)
                print(resp.status)
                Etree = etree.HTML(html)
                urls  = Etree.xpath('//tr/td/a/@href')
                print(len(urls))
                for url in urls:
                    await asyncio.sleep(2)
                    await getUrlResult(url = url)


async  def getUrlResult(url = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            html = await resp.text()
            Etree = etree.HTML(html)

            times= Etree.xpath("//tr/td[1]/strong/text()")



            length = len(times)
            for i in range(3,13):
                try:
                    nianfen = Etree.xpath("//tr[{}]//td[1]/strong/text()".format(i))[0]
                    difang = Etree.xpath('//h1[@class = "xqy_core_tit"]/text()'.format(i))[0]  # 所在区域
                    difang = getDifang(difang)  # 获取所在区域
                    YibenWenke = Etree.xpath("//tr[{}]//td[2]/text()".format(i))[0]     #一本文科
                    YibenLike = Etree.xpath("//tr[{}]//td[3]/text()".format(i))[0]      #一本理科
                    ErbenWenke = Etree.xpath("//tr[{}]//td[4]/text()".format(i))[0]     #二本文科
                    ErbenLke = Etree.xpath("//tr[{}]//td[5]/text()".format(i))[0]       #二本理科
                    Grade ={}
                    yiben = {
                        "文科":YibenWenke,
                        "理科":YibenLike,
                    }
                    erben = {
                        "文科":ErbenWenke,
                        "理科":ErbenLke
                    }
                    Grade = {
                        "区域":difang,
                        "年份":nianfen,
                        "一本":yiben,
                        "二本":erben
                    }

                    # with open('result.json', 'a') as f:
                    #     json.dump(Grade, f, indent=4)
                    #     f.write(',\n')
                    db = pymysql.connect(host="localhost", port=3306, user="root", password="302811", database="gaokao",
                                         charset="utf8")
                    cursor = db.cursor()
                    sql = 'insert into fenshu VALUES ("%s","%s","%s","%s","%s","%s")'%(difang,nianfen,ErbenWenke,YibenLike,ErbenWenke,ErbenLke)
                    print(sql)
                    try:
                        cursor.execute(sql)
                        # 提交到数据库执行"
                        db.commit()
                    except BaseException as E:
                        print(E)
                        db.rollback()
                    cursor.close()
                    db.close()
                except BaseException as E:
                    print(E)






def getDifang(match):
    partter = r"历年(.*?)高考录取分数线"
    re_match = re.match(partter, match).group(1)
    return re_match

def main():
    url = "https://news.koolearn.com/20180823/1162540.html"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(getUrl(url))

if __name__ == '__main__':
    main()