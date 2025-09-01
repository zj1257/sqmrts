#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import base64
import math
import json
import requests
import hashlib
from Crypto.Cipher import AES

class Spider(Spider):
    def getName(self):
        return "爱看影视"
    def init(self,extend=""):
        pass
    def isVideoFormat(self,url):
        pass
    def manualVideoCheck(self):
        pass
    def homeContent(self,filter):
        result = {}
        cateManual = {
            "电影": "1",
            "剧集": "2",
            "综艺": "3",
            "动漫": "4",
            "美剧": "16",
            "日韩剧": "15",
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })

        result['class'] = classes
        if (filter):
            result['filters'] = self.config['filter']
        return result
    def homeVideoContent(self):
        url = 'https://ikan6.vip'
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
        rsp = self.fetch(url, headers=header)
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath(
            "//div[@class='module-items module-poster-items-base']/a")
        videos = []
        for a in aList:
            name = a.xpath('./@title')[0]
            pic = a.xpath("./div/div[@class='module-item-pic']/img/@data-original")[0]
            mark = a.xpath("./div/div[@class='module-item-douban']/text()")[0].replace("豆瓣:", "").replace("分", "")
            sid = a.xpath(
                "./@href")[0].replace("/", "").replace("voddetail", "")
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result = {
            'list': videos
        }
        return result

    def categoryContent(self,tid,pg,filter,extend):
        result = {}
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
        url = 'https://ikanys.tv/vodshow/{}--hits------{}---/'.format(tid,pg)
        session= self.verifyCode('show')
        if session:
            rsp = session.get(url, headers=header)
            html = self.html(rsp.text)
            aList = html.xpath("//div[@class='module']/a")
            videos = []
            numvL = len(aList)
            pgc = math.ceil(numvL/15)
            for a in aList:
                aid = a.xpath("./@href")[0]
                aid = self.regStr(reg=r'/voddetail/(.*?)/', src=aid)
                img = a.xpath(".//div[@class='module-item-pic']/img/@data-original")[0]
                name = a.xpath("./@title")[0]
                videos.append({
                    "vod_id": aid,
                    "vod_name": name,
                    "vod_pic": img,
                    "vod_remarks": ''
                })
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = pgc
            result['limit'] = numvL
            result['total'] = numvL
        return result

    def detailContent(self,array):
        aid = array[0]
        url = 'https://ikanys.tv/voddetail/{0}/'.format(aid)
        rsp = self.fetch(url)
        html = self.html(rsp.text)
        node = html.xpath("//div[@class='module-main']")[0]
        title = node.xpath(".//div[@class='module-info-heading']/h1/text()")[0]
        pic = html.xpath("//div[@class='module-item-pic']/img/@data-original")[0]
        vod = {
            "vod_id": aid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": '',
            "vod_year": '',
            "vod_area": '',
            "vod_remarks": '',
            "vod_actor": '',
            "vod_director": '',
            "vod_content": ''
        }
        playFrom = ''
        playfromList = html.xpath("//div[@class='module-tab-items-box hisSwiper']/div")
        for pL in playfromList:
            pL = pL.xpath("./@data-dropdown-value")[0].strip()
            playFrom = playFrom + '$$$' + pL
        urlList = html.xpath("//div[contains(@class,'module-list sort-list tab-list his-tab-list')]")
        playUrl = ''
        for uL in urlList:
            for playurl in uL.xpath(".//a"):
                purl = self.regStr(reg=r'/vodplay/(.*?)/', src=playurl.xpath("./@href")[0])
                name = playurl.xpath("./@title")[0]
                playUrl = playUrl + '{}${}#'.format(name, purl)
            playUrl = playUrl + '$$$'
        vod['vod_play_from'] = playFrom.strip('$$$')
        vod['vod_play_url'] = playUrl.strip('$$$')

        result = {
            'list': [
                vod
            ]
        }
        return result

    def verifyCode(self,tag):
        retry = 10
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        while retry:
            try:
                session = requests.session()
                img = session.get('https://ikanys.tv/index.php/verify/index.html?', headers=header).content
                code = session.post('https://api.nn.ci/ocr/b64/text', data=base64.b64encode(img).decode()).text
                'https://ikanys.tv/index.php/ajax/verify_check?type=show&verify=0072'
                res = session.post(url=f"https://ikanys.tv/index.php/ajax/verify_check?type={tag}&verify={code}", headers=header).json()
                if res["msg"] == "ok":
                    return session
            except Exception as e:
                print(e)
            finally:
                retry = retry - 1

    def searchContent(self,key,quick):
        result = {}
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        url = 'https://ikanys.tv/vodsearch/-------------/?wd={0}'.format(key)
        session = self.verifyCode('search')
        if session:
            rsp = session.get(url, headers=header)
            root = self.html(rsp.text)
            vodList = root.xpath("//div[@class='module-items module-card-items']/div")
            videos = []
            for vod in vodList:
                name = vod.xpath("./a/div/div/img/@alt")[0]
                pic = vod.xpath("./a/div/div/img/@data-original")[0]
                sid = vod.xpath("./a/@href")[0]
                sid = self.regStr(sid,"/voddetail/(\\S+)/")
                mark = vod.xpath("./a/div/div[@class='module-item-note']/text()")[0]
                videos.append({
                    "vod_id":sid,
                    "vod_name":name,
                    "vod_pic":pic,
                    "vod_remarks":mark
                })
            result = {
                    'list': videos
                }
        return result
    def parseCBC(self, enc, key, iv):
        keyBytes = key.encode("utf-8")
        ivBytes = iv.encode("utf-8")
        cipher = AES.new(keyBytes, AES.MODE_CBC, ivBytes)
        msg = cipher.decrypt(enc)
        paddingLen = msg[len(msg) - 1]
        return msg[0:-paddingLen]

    def playerContent(self,flag,id,vipFlags):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "Referer": "https://ikanys.tv/"
        }
        result = {}
        url = 'https://ikanys.tv/vodplay/{0}/'.format(id)
        rsp = self.fetch(url, headers=header)
        info = json.loads(self.regStr(reg=r'var player_aaaa=(.*?)</script>', src=self.cleanText(rsp.text)))
        parse = 0
        if info['url'].startswith('http'):
            purl = info['url']
        else:
            url = 'https://cms.ikanys.tv/ikanbfqmui/nicaibudaowozaina.php?url={}'.format(info['url'])
            r = requests.get(url, headers=header, verify=False)
            now_infos=[]
            now_infos.append(self.regStr(r.text, r'now_([0-9]*?)\"'))
            now_infos.append(self.regStr(r.text, r'now_([0-9A-Za-z]*[A-Za-z]+[0-9A-Za-z]*?)\"'))
            content_str = self.regStr(r.text,r'\"url\": \"(.*?)\"')
            posList = list(now_infos[0])
            secretsDict = {}
            for pos in range(len(posList)):
                secretsDict[posList[pos]] = now_infos[1][pos]
            posList.sort()
            secrets = ""
            for pos in posList:
                secrets += secretsDict[pos]
            secrets_data = '{}ikanysbfq66bielaizhanbian'.format(secrets).encode()
            secrets_md5 = hashlib.md5(secrets_data).hexdigest()
            iv = secrets_md5[:16]
            key = secrets_md5[-16:]
            purl = self.parseCBC(base64.b64decode(content_str), key, iv).decode()
        # 直接调用解析
        # else:
        #     parse = 1
        #     purl = url
        result["parse"] = parse
        result["playUrl"] = ''
        result["url"] = purl
        result["header"] = ''
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def localProxy(self,param):
        action = {
            'url':'',
            'header':'',
            'param':'',
            'type':'string',
            'after':''
        }
        return [200, "video/MP2T", action, ""]
