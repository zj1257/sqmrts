# coding=utf-8
# !/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
from requests import session, utils
import time


class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "哔哩"

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        result = {}
        if len(self.cookies) <= 0:
            self.getCookie()
        cateManual = {
            "奥特曼": "pgc奥特曼+中配",
            "注安实务": "注安化工实务",
            "注安管理": "注安管理"
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
        tid = '昆虫小世界'
        return self.categoryContent(tid, 1, False, {})


    cookies = ''
    login = False
    def getCookie(self):
        try:
            cookies_str = self.fetch("https://pan.shangui.cc/f/wQeATg/cookies.txt").text
            # cookies_str = ""
            cookies_dic = dict([co.strip().split('=') for co in cookies_str.split(';')])
            rsp = session()
            cookies_jar = utils.cookiejar_from_dict(cookies_dic)
            rsp.cookies = cookies_jar
            content = self.fetch("http://api.bilibili.com/x/web-interface/nav", cookies=rsp.cookies)
            res = json.loads(content.text)
        except:
            res = {}
            res["code"] = 404
        if res["code"] == 0:
            self.login = True
            self.cookies = rsp.cookies
        else:
            rsp = self.fetch("https://www.bilibili.com/")
            self.cookies = rsp.cookies
            self.login = False
        return rsp.cookies

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        if tid.startswith("pgc"):
            tid = tid[3:]
            url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=media_bangumi&keyword={0}&page={1}'.format(tid, pg)  # 番剧搜索
            if len(self.cookies) <= 0:
                self.getCookie()
            rsp = self.fetch(url, cookies=self.cookies)
            content = rsp.text
            jo = json.loads(content)
            rs = jo['data']
            if rs['numResults'] == 0:
                url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=media_ft&keyword={0}&page={1}'.format(tid, pg)  # 影视搜索
                rspRetry = self.fetch(url, cookies=self.cookies)
                content = rspRetry.text
            jo = json.loads(content)
            videos = []
            vodList = jo['data']['result']
            for vod in vodList:
                aid = str(vod['season_id']).strip()
                title = vod['title'].strip().replace("<em class=\"keyword\">", "").replace("</em>", "")
                img = vod['eps'][0]['cover'].strip()
                remark = vod['index_show']
                videos.append({
                    "vod_id": 'pgc'+aid,
                    "vod_name": title,
                    "vod_pic": img,
                    "vod_remarks": remark
                })
        else:
            url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}&page={1}'.format(tid, pg)
            if len(self.cookies) <= 0:
                self.getCookie()
            rsp = self.fetch(url, cookies=self.cookies)
            content = rsp.text
            jo = json.loads(content)
            videos = []
            vodList = jo['data']['result']
            for vod in vodList:
                aid = str(vod['aid']).strip()
                title = vod['title'].replace("<em class=\"keyword\">", "").replace("</em>", "").replace("&quot;", '"')
                img = 'https:' + vod['pic'].strip()
                remark = str(vod['duration']).strip()
                videos.append({
                    "vod_id": aid,
                    "vod_name": title,
                    "vod_pic": img,
                    "vod_remarks": remark
                })
        result['list'] = videos
        result['page'] = jo['data']['page']
        result['pagecount'] = jo['data']['numPages']
        result['limit'] = 5
        result['total'] = 999999
        return result

    def cleanSpace(self, str):
        return str.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')

    def detailContent(self, array):
        aid = array[0]
        if aid.startswith("pgc"):
            aid = aid[3:]
            url = "http://api.bilibili.com/pgc/view/web/season?season_id={0}".format(aid)
            rsp = self.fetch(url,headers=self.header)
            jRoot = json.loads(rsp.text)
            jo = jRoot['result']
            id = jo['season_id']
            title = jo['title']
            pic = jo['cover']
            areas = jo['areas'][0]['name']
            typeName = jo['share_sub_title']
            dec = jo['evaluate']
            remark = jo['new_ep']['desc']
            vod = {
                "vod_id":id,
                "vod_name":title,
                "vod_pic":pic,
                "type_name":typeName,
                "vod_year":"",
                "vod_area":areas,
                "vod_remarks":remark,
                "vod_actor":"",
                "vod_director":"",
                "vod_content":dec
            }
            ja = jo['episodes']
            playUrl = ''
            for tmpJo in ja:
                eid = tmpJo['id']
                cid = tmpJo['cid']
                part = tmpJo['title'].replace("#", "-")
                playUrl = playUrl + '{0}$pgc{1}_{2}#'.format(part, eid, cid)

            vod['vod_play_from'] = 'B站影视'
        else:
            url = "https://api.bilibili.com/x/web-interface/view?aid={0}".format(aid)
            rsp = self.fetch(url, headers=self.header)
            jRoot = json.loads(rsp.text)
            jo = jRoot['data']
            title = jo['title'].replace("<em class=\"keyword\">", "").replace("</em>", "")
            pic = jo['pic']
            desc = jo['desc']
            timeStamp = jo['pubdate']
            timeArray = time.localtime(timeStamp)
            year = str(time.strftime("%Y", timeArray))
            dire = jo['owner']['name']
            typeName = jo['tname']
            remark = str(jo['duration']).strip()
            vod = {
                "vod_id": aid,
                "vod_name": title,
                "vod_pic": pic,
                "type_name": typeName,
                "vod_year": year,
                "vod_area": "",
                "vod_remarks": remark,
                "vod_actor": "",
                "vod_director": dire,
                "vod_content": desc
            }
            ja = jo['pages']
            playUrl = ''
            for tmpJo in ja:
                cid = tmpJo['cid']
                part = tmpJo['part'].replace("#", "-")
                playUrl = playUrl + '{0}${1}_{2}#'.format(part, aid, cid)

            vod['vod_play_from'] = 'B站视频'
        vod['vod_play_url'] = playUrl

        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        header = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}'.format(key)
        if len(self.cookies) <= 0:
            self.getCookie()
        rsp = self.fetch(url, cookies=self.cookies,headers=header)
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] != 0:
            rspRetry = self.fetch(url, cookies=self.getCookie())
            content = rspRetry.text
        jo = json.loads(content)
        videos = []
        vodList = jo['data']['result']
        for vod in vodList:
            aid = str(vod['aid']).strip()
            title = vod['title'].replace("<em class=\"keyword\">", "").replace("</em>", "").replace("&quot;", '"')
            img = 'https:' + vod['pic'].strip()
            remark = str(vod['duration']).strip()
            videos.append({
                "vod_id": aid,
                "vod_name": title,
                "vod_pic": img,
                "vod_remarks": remark
            })
        result = {
            'list': videos
        }
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        ispgc = False
        if id.startswith("pgc"):
            ispgc = True
            id = id[3:]
        ids = id.split("_")
        header = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        if ispgc:
            url = 'https://api.bilibili.com/pgc/player/web/playurl?qn=116&ep_id={0}&cid={1}'.format(ids[0],ids[1])
        else:
            url = 'https://api.bilibili.com:443/x/player/playurl?avid={0}&cid={1}&qn=120&fnval=0&128=128&fourk=1'.format(ids[0], ids[1])
        if len(self.cookies) <= 0:
            self.getCookie()
        rsp = self.fetch(url, cookies=self.cookies, headers=header)
        jRoot = json.loads(rsp.text)
        if jRoot['message'] != 'success' and ispgc:
            url = ''
        else:
            if ispgc:
                jo = jRoot['result']
            else:
                jo = jRoot['data']
            ja = jo['durl']

            maxSize = -1
            position = -1
            for i in range(len(ja)):
                tmpJo = ja[i]
                if maxSize < int(tmpJo['size']):
                    maxSize = int(tmpJo['size'])
                    position = i

            url = ''
            if len(ja) > 0:
                if position == -1:
                    position = 0
                url = ja[position]['url']

        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        if ispgc:
            result["contentType"] = 'video/x-flv'
        else:
            result["contentType"] = 'video/mp4'
        return result

    config = {
        "player": {},
        "filter": {"收藏夹": [{"key": "order","name": "排序","value": [{"n": "收藏时间","v": "mtime"},{"n": "播放量","v": "view"},{"n": "投稿时间","v": "pubtime"}]},{"key": "mlid","name": "收藏夹分区","value": []}],"频道":[{"key":"cid","name":"分类","value":[{'n': '搞笑', 'v': 1833}, {'n': '美食', 'v': 20215}, {'n': '鬼畜', 'v': 68}, {'n': '天官赐福', 'v': 2544632}, {'n': '英雄联盟', 'v': 9222}, {'n': '美妆', 'v': 832569}, {'n': '必剪创作', 'v': 15775524}, {'n': '单机游戏', 'v': 17683}, {'n': '搞笑', 'v': 1833}, {'n': '科普', 'v': 5417}, {'n': '影视剪辑', 'v': 318570}, {'n': 'vlog', 'v': 2511282}, {'n': '声优', 'v': 1645}, {'n': '动漫杂谈', 'v': 530918}, {'n': 'COSPLAY', 'v': 88}, {'n': '漫展', 'v': 22551}, {'n': 'MAD', 'v': 281}, {'n': '手书', 'v': 608}, {'n': '英雄联盟', 'v': 9222}, {'n': '王者荣耀', 'v': 1404375}, {'n': '单机游戏', 'v': 17683}, {'n': '我的世界', 'v': 47988}, {'n': '守望先锋', 'v': 926988}, {'n': '恐怖游戏', 'v': 17941}, {'n': '英雄联盟', 'v': 9222}, {'n': '王者荣耀', 'v': 1404375}, {'n': '守望先锋', 'v': 926988}, {'n': '炉石传说', 'v': 318756}, {'n': 'DOTA2', 'v': 47034}, {'n': 'CS:GO', 'v': 99842}, {'n': '鬼畜', 'v': 68}, {'n': '鬼畜调教', 'v': 497221}, {'n': '诸葛亮', 'v': 51330}, {'n': '二次元鬼畜', 'v': 29415}, {'n': '王司徒', 'v': 987568}, {'n': '万恶之源', 'v': 21}, {'n': '美妆', 'v': 832569}, {'n': '服饰', 'v': 313718}, {'n': '减肥', 'v': 20805}, {'n': '穿搭', 'v': 1139735}, {'n': '发型', 'v': 13896}, {'n': '化妆教程', 'v': 261355}, {'n': '电音', 'v': 14426}, {'n': '欧美音乐', 'v': 17034}, {'n': '中文翻唱', 'v': 8043}, {'n': '洛天依', 'v': 8564}, {'n': '翻唱', 'v': 386}, {'n': '日文翻唱', 'v': 85689}, {'n': '科普', 'v': 5417}, {'n': '技术宅', 'v': 368}, {'n': '历史', 'v': 221}, {'n': '科学', 'v': 1364}, {'n': '人文', 'v': 40737}, {'n': '科幻', 'v': 5251}, {'n': '手机', 'v': 7007}, {'n': '手机评测', 'v': 143751}, {'n': '电脑', 'v': 1339}, {'n': '摄影', 'v': 25450}, {'n': '笔记本', 'v': 1338}, {'n': '装机', 'v': 413678}, {'n': '课堂教育', 'v': 3233375}, {'n': '公开课', 'v': 31864}, {'n': '演讲', 'v': 2739}, {'n': 'PS教程', 'v': 335752}, {'n': '编程', 'v': 28784}, {'n': '英语学习', 'v': 360005}, {'n': '喵星人', 'v': 1562}, {'n': '萌宠', 'v': 6943}, {'n': '汪星人', 'v': 9955}, {'n': '大熊猫', 'v': 22919}, {'n': '柴犬', 'v': 30239}, {'n': '吱星人', 'v': 6947}, {'n': '美食', 'v': 20215}, {'n': '甜点', 'v': 35505}, {'n': '吃货', 'v': 6942}, {'n': '厨艺', 'v': 239855}, {'n': '烘焙', 'v': 218245}, {'n': '街头美食', 'v': 1139423}, {'n': 'A.I.Channel', 'v': 3232987}, {'n': '虚拟UP主', 'v': 4429874}, {'n': '神楽めあ', 'v': 7562902}, {'n': '白上吹雪', 'v': 7355391}, {'n': '彩虹社', 'v': 1099778}, {'n': 'hololive', 'v': 8751822}, {'n': 'EXO', 'v': 191032}, {'n': '防弹少年团', 'v': 536395}, {'n': '肖战', 'v': 1450880}, {'n': '王一博', 'v': 902215}, {'n': '易烊千玺', 'v': 15186}, {'n': 'BLACKPINK', 'v': 1749296}, {'n': '宅舞', 'v': 9500}, {'n': '街舞', 'v': 5574}, {'n': '舞蹈教学', 'v': 157087}, {'n': '明星舞蹈', 'v': 6012204}, {'n': '韩舞', 'v': 159571}, {'n': '古典舞', 'v': 161247}, {'n': '旅游', 'v': 6572}, {'n': '绘画', 'v': 2800}, {'n': '手工', 'v': 11265}, {'n': 'vlog', 'v': 2511282}, {'n': 'DIY', 'v': 3620}, {'n': '手绘', 'v': 1210}, {'n': '综艺', 'v': 11687}, {'n': '国家宝藏', 'v': 105286}, {'n': '脱口秀', 'v': 4346}, {'n': '日本综艺', 'v': 81265}, {'n': '国内综艺', 'v': 641033}, {'n': '人类观察', 'v': 282453}, {'n': '影评', 'v': 111377}, {'n': '电影解说', 'v': 1161117}, {'n': '影视混剪', 'v': 882598}, {'n': '影视剪辑', 'v': 318570}, {'n': '漫威', 'v': 138600}, {'n': '超级英雄', 'v': 13881}, {'n': '影视混剪', 'v': 882598}, {'n': '影视剪辑', 'v': 318570}, {'n': '诸葛亮', 'v': 51330}, {'n': '韩剧', 'v': 53056}, {'n': '王司徒', 'v': 987568}, {'n': '泰剧', 'v': 179103}, {'n': '郭德纲', 'v': 8892}, {'n': '相声', 'v': 5783}, {'n': '张云雷', 'v': 1093613}, {'n': '秦霄贤', 'v': 3327368}, {'n': '孟鹤堂', 'v': 1482612}, {'n': '岳云鹏', 'v': 24467}, {'n': '假面骑士', 'v': 2069}, {'n': '特摄', 'v': 2947}, {'n': '奥特曼', 'v': 963}, {'n': '迪迦奥特曼', 'v': 13784}, {'n': '超级战队', 'v': 32881}, {'n': '铠甲勇士', 'v': 11564}, {'n': '健身', 'v': 4344}, {'n': '篮球', 'v': 1265}, {'n': '体育', 'v': 41103}, {'n': '帕梅拉', 'v': 257412}, {'n': '极限运动', 'v': 8876}, {'n': '足球', 'v': 584}, {'n': '星海', 'v': 178862}, {'n': '张召忠', 'v': 116480}, {'n': '航母', 'v': 57834}, {'n': '航天', 'v': 81618}, {'n': '导弹', 'v': 14958}, {'n': '战斗机', 'v': 24304}]}]}
    }
    header = {}

    def localProxy(self, param):
        return [200, "video/MP2T", action, ""]
