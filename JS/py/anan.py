#coding=utf-8
#!/usr/bin/python
import io
import re
import json
import time
from datetime import datetime
import requests
from sys import path
from os.path import splitext
from urllib.parse import urlparse, quote, unquote

path.append('..')
from base.spider import Spider

class Spider(Spider):

    def init(self, extend=""):
        self.vodPic = ""
        self.headers_host = {
            "Referer": "https://pan.quark.cn/",
            "Content-Type": "application/json",
            "Host": "drive-pc.quark.cn"
        }
        self.s = requests.Session()
        self.s.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/3.0.1 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch'
        }
        try:
            extendDict = json.loads(extend)
        except:
            extendDict = extend
        if 'cookie' in extendDict:
            cookies_str = extendDict['cookie'] 
            if type(cookies_str) == str and cookies_str.startswith('http'):
                cookies_str = self.fetch(cookies_str, timeout=10).text.strip()
            cookies_dict = dict([l.split("=", 1) for l in cookies_str.split("; ")])
            if cookies_dict:
                cookies = requests.utils.cookiejar_from_dict(cookies_dict)
                self.s.cookies.update(cookies)
        #self.fid = str(extendDict['fid'] if 'fid' in extendDict else "0")
        try:
            scrape_str = str(extendDict['scrape'] if 'scrape' in extendDict else "")
            scrape_str = self.fetch(scrape_str, timeout=10).text.strip()
            self.scrape_json = json.loads(scrape_str)
        except:
            self.scrape_json = {"scrape": []}
        try:
            self.type_name = extendDict['name']+"专属"
        except:
            self.type_name = "安安专属"
        try:
            self.classname = extendDict['folders']
        except:
            self.classname = []
        try:
            self.is_vip = self.get_vip()
            print("是否VIP：", self.is_vip)
        except:
            pass
        newcookies = requests.utils.dict_from_cookiejar(self.s.cookies)
        self.cookie = ''
        for name, value in newcookies.items():
            self.cookie += '{0}={1};'.format(name, value)
        self.cookie = self.cookie[:-1]
        if 'thread' in extendDict:
            self.thread = str(extendDict['thread'])
        else:
            self.thread = '10'
        # 下面为B站视频处理
        self.b = requests.Session()
        self.b.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
            "Referer": "https://www.bilibili.com"
        }
        if 'bili_cookie' in extendDict:
            cookies_str = extendDict['bili_cookie']
            if type(cookies_str) == str and cookies_str.startswith('http'):
                cookies_str = self.fetch(cookies_str, timeout=10).text.strip()
            cookies_dict = dict([l.split("=", 1) for l in cookies_str.split("; ")])
            if cookies_dict:
                cookies = requests.utils.cookiejar_from_dict(cookies_dict)
                self.b.cookies.update(cookies)
        

    def getscrape(self, fid):
        for i in self.scrape_json["scrape"]:
            if fid == i['folder']:
                if i['imgurl'] == "":
                    return self.vodPic
                elif i['imgurl'].startswith('http'):
                    return {'pic': i['imgurl']}
                else:
                    return eval(i['imgurl'])
        return {}

    def get_vip(self):
        """ 检查是否是 VIP 用户 """
        result = self.s.get("https://drive-pc.quark.cn/1/clouddrive/member?pr=ucpro&fr=pc&uc_param_str=&fetch_subscribe=true&_ch=home&fetch_identity=true", headers=self.headers_host, timeout=10)
        data = result.json()
        return "VIP" in data["data"]["member_type"]
    def getName(self):
        return "quark"

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        result = {}
        result['filters'] = {}
        r = self.s.get('https://pan.quark.cn/account/info', timeout=10).json()
        if r['data']:
            nickname = r['data']['nickname']
            print(nickname)
            #fname = [self.type_name, self.fid]
        else:
            fname = ["登录失败！请正确配置夸克Cookie。","error"]
        result['class'] = [{"type_name": self.type_name, "type_id": "65b3da4439d04e29b467dd507cfc01f5", "type_flag": "1"}]
        if self.b.cookies:
            result['class'].append({"type_name": "B站收藏", "type_id": "fav&&&1722080014", "type_flag": "1"})
        for i in self.classname:
            result['class'].append({"type_name": i["name"], "type_id": i["fid"], "type_flag": "1"})
        self.log(result)
        self.fid_name={i["type_id"]:i["type_name"] for i in result['class']}
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        page = int(pg)
        result = {}
        videos = []
        pagecount = page
        if tid == "收藏夹":
            userid = self.getUserid()
            if userid is None:
                return {}, 1
            url = f'http://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={userid}&jsonp=jsonp'
            r = self.b.get(url, timeout=5)
            data = json.loads(self.cleanText(r.text))
            vodList = data['data']['list']
            pagecount = page
            for vod in vodList:
                vid = vod['id']
                title = vod['title'].strip()
                remark = vod['media_count']
                img = 'https://api-lmteam.koyeb.app/files/shoucang.png'
                videos.append({
                    "vod_id": f'fav&&&{vid}',
                    "vod_name": title,
                    "vod_pic": img,
                    "vod_tag": 'folder',
                    "style": {
                        "type": "rect",
                        "ratio": 0.75
                    },
                    "vod_remarks": remark
                })
            lenvideos = len(videos)
            result['list'] = videos
            result['page'] = page
            result['pagecount'] = pagecount
            result['limit'] = lenvideos
            result['total'] = lenvideos
            return result
        elif tid.startswith('fav&&&'):
            tid = tid[6:]
            url = f'http://api.bilibili.com/x/v3/fav/resource/list?media_id={tid}&pn={page}&ps=20&platform=web&type=0'
            r = self.b.get(url, timeout=5)
            data = json.loads(self.cleanText(r.text))
            if data['data']['has_more']:
                pagecount = page + 1
            else:
                pagecount = page
            vodList = data['data']['medias']
            for vod in vodList:
                vid = str(vod['id']).strip()
                title = self.removeHtmlTags(vod['title']).replace("&quot;", '"')
                img = vod['cover'].strip()
                remark = time.strftime('%H:%M:%S', time.gmtime(vod['duration']))
                if remark.startswith('00:'):
                    remark = remark[3:]
                videos.append({
                    "vod_id": vid,
                    "vod_name": title,
                    "vod_pic": img,
                    "style": {
                        "type": "rect",
                        "ratio": 0.75
                    },
                    "vod_remarks": remark
                })
            lenvideos = len(videos)
            result['list'] = videos
            result['page'] = page
            result['pagecount'] = pagecount
            result['limit'] = lenvideos
            result['total'] = lenvideos
            return result
        # 以上为对B站收藏夹的处理
        self.log(tid)
        pName = None
        if "folder" in tid:
            fid = json.loads(tid)
            tid = fid['folder']
            pName = fid['fileName']
        params = {"shareId":"","folder":"","parentId":"","fileType":"","fileName":""}
        if tid == "error":
            return result
        r = self.s.get(f'https://drive-pc.quark.cn/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid={tid}&_page={pg}&_size=100&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc', headers=self.headers_host,timeout=10)
        data = r.json()
        vodList = data["data"]['list']
        videoList = []
        for vod in vodList:
            try:
                if vod['big_thumbnail'].startswith('http'):
                    imgUrl = vod['big_thumbnail']
                    img = f'{self.getProxyUrl()}&type=image&url={quote(imgUrl)}'
            except:
                img = self.vodPic
            if vod['dir']:
                params['folder'] = vod["fid"]
                params['parentId'] = vod["pdir_fid"]
                params['fileType'] = "folder"
                params['fileName'] = vod['file_name']
                scrapeInfo = self.getscrape(vod["fid"])
                videos.append({
                    "vod_id": json.dumps(params, ensure_ascii=False),
                    "vod_name": vod['file_name'],
                    "vod_pic": scrapeInfo["pic"] if scrapeInfo.get("pic") else img,
                    "vod_tag": "folder",
                    "style": {
                        "type": "rect",
                        "ratio": 0.75
                    },
                    "vod_remarks": "文件夹"
                })
            else:
                if splitext(vod['file_name'])[1] in ['.mp4', '.mpg', '.mkv', '.ts', '.TS', '.avi', '.flv', '.rmvb','.mp3', '.flac', '.wav', '.wma', '.dff']:
                    size = self.getSize(vod['size'])
                    videoList.append({'fid': vod["fid"], 'pdir_fid':vod["pdir_fid"],'fileName': vod['file_name'], "img": img, "remark": size})
                # elif splitext(vod['file_name'])[1] in ['.ass', '.ssa', '.srt']:
                # 	subtList.append(vod['file_name'])
        if videoList != []:
            for video in videoList:
                params['folder'] = video["fid"]
                params['parentId'] = video["pdir_fid"]
                params['fileType'] = "file"
                params['fileName'] = self.fid_name[tid] if pName is None else pName
                videos.append({
                    "vod_id": json.dumps(params, ensure_ascii=False),
                    "vod_name": video['fileName'],
                    "vod_pic": video['img'],
                    "vod_tag": 'file',
                    "style": {
                        "type": "rect",
                        "ratio": 1.33
                    },
                    "vod_remarks": video['remark']
                })

        result['list'] = videos
        result['page'] = data['metadata']['_page']
        result['pagecount'] = -1 * (-data['metadata']['_total'] // 100)
        result['limit'] = 100
        result['total'] = data['metadata']['_total']
        return result


    def detailContent(self, did):
        if 'folder' in did[0]:
            params = json.loads(did[0])
            result = {}
            pName = params['fileName'].split("：")[-1]
            fileType = params['fileType']
            if fileType == 'playList':
                pass
            elif fileType == 'file':
                tid = params['parentId']
                print(tid)
                # 暂缓处理第二页内容
                pg = 1
                vodList = []
                while True:
                    r = self.s.get(f'https://drive-pc.quark.cn/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid={tid}&_page={pg}&_size=100&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc', headers={'Referer': 'https://pan.quark.cn/', 'Host': 'drive-pc.quark.cn', 'Connection': 'Keep-Alive'},timeout=10)
                    data = r.json()
                    self.log(str(data))
                    time.sleep(0.05)
                    vodList += data["data"]['list']
                    pg += 1
                    if pg > -1 * (-data['metadata']['_total'] // 100):
                        break
                videoList = []
                for vod in vodList:
                    if not vod['dir']:
                        if splitext(vod['file_name'])[1] in ['.mp4', '.mpg', '.mkv', '.ts', '.TS', '.avi', '.flv', '.rmvb','.mp3', '.flac', '.wav', '.wma', '.dff']:
                            videoList.append({'fid': vod["fid"],'fileName': vod['file_name'].rsplit('.', 1)[0]})
                vod_play_url = '#'.join(f"{i['fileName']}${i['fid']}" for i in videoList)
                # 获取播放源列表
                play_from_tmp = ["夸克原画","夸克预览"]
                play_url = []
                # 使播放链接与播放源数量对应
                for _ in play_from_tmp:
                    play_url.append(vod_play_url)
                scrapeInfo = self.getscrape(params['parentId'])
                video = [{
                "vod_id": params['folder'],#文件id
                "vod_name": pName,#上层文件夹名字
                "vod_pic": scrapeInfo["pic"] if scrapeInfo.get("pic") else self.vodPic,#上层文件夹图片
                "type_name": "夸克云盘",
                "vod_year": scrapeInfo["year"] if scrapeInfo.get("year") else "",
                "vod_area": scrapeInfo["countries"] if scrapeInfo.get("countries") else "",
                "vod_remarks": scrapeInfo["remark"] if scrapeInfo.get("remark") else "",
                "vod_actor": scrapeInfo["actors"] if scrapeInfo.get("actors") else "",
                "vod_director": scrapeInfo["directors"] if scrapeInfo.get("directors") else "",
                "vod_content": scrapeInfo["content"] if scrapeInfo.get("content") else "",
                # 播放源 多个用$$$分隔
                "vod_play_from": "$$$".join(play_from_tmp), 
                # 播放列表 注意分隔符 分别是 多个源$$$分隔，源中的剧集用#分隔，剧集的名称和地址用$分隔
                "vod_play_url": "$$$".join(play_url)
                }]
                result['list'] = video
                return result
        else:
            aid = did[0]
            url = f"https://api.bilibili.com/x/web-interface/view?aid={aid}"
            r = self.b.get(url, timeout=10)
            data = json.loads(self.cleanText(r.text))
            if "staff" in data['data']:
                director = ''
                for staff in data['data']['staff']:
                    director += staff['name']
            else:
                director = data['data']['owner']['name']
            vod = {
                "vod_id": aid,
                "vod_name": self.removeHtmlTags(data['data']['title']),
                "vod_pic": data['data']['pic'],
                "type_name": data['data']['tname'],
                "vod_year": datetime.fromtimestamp(data['data']['pubdate']).strftime('%Y-%m-%d %H:%M:%S'),
                "vod_content": data['data']['desc'].replace('\xa0', ' ').replace('\n\n', '\n').strip(),
                "vod_director": director
            }
            videoList = data['data']['pages']
            playUrl = ''
            for video in videoList:
                remark = time.strftime('%H:%M:%S', time.gmtime(video['duration']))
                name = self.removeHtmlTags(video['part']).strip().replace("#", "-").replace('$', '*')
                if remark.startswith('00:'):
                    remark = remark[3:]
                playUrl = playUrl + f"[{remark}]/{name}${aid}_{video['cid']}#"
            vod['vod_play_from'] = 'B站视频'
            vod['vod_play_url'] = playUrl.strip('#')
            result = {
                'list': [
                    vod
                ]
            }
            return result

    def searchContent(self, key, quick, pg="1"):
        pass

    def playerContent(self, flag, file_id, vipFlags):
        if flag == 'B站视频':
            result = {}
            pid = file_id
            if pid.startswith('bvid&&&'):
                url = "https://api.bilibili.com/x/web-interface/view?bvid={}".format(pid[7:])
                r = self.b.get(url, timeout=10)
                data = r.json()['data']
                aid = data['aid']
                cid = data['cid']
            elif "_" in pid:
                idList = pid.split("_")
                aid = idList[0]
                cid = idList[1]
            url = 'https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=120&fnval=4048&fnver=0&fourk=1'.format(aid, cid)
            cookiesDict, _, _ = self.getCookie()
            cookies = quote(json.dumps(cookiesDict))
            result["parse"] = 0
            result["playUrl"] = ''
            result["url"] = f'http://127.0.0.1:9978/proxy?do=py&type=mpd&cookies={cookies}&url={quote(url)}&aid={aid}&cid={cid}&thread={self.thread}'
            result["header"] = self.b.headers
            result['danmaku'] = 'https://api.bilibili.com/x/v1/dm/list.so?oid={}'.format(cid)
            result["format"] = 'application/dash+xml'
            return result
        if False:#'可可' in self.type_name:
            proxy_url = f'http://127.0.0.1:9978/proxy?do=pan&site=quark&shareId=&fileId={file_id}&fileToken='
            header = self.s.headers
            header['Cookie'] = self.cookie
            header["Referer"] = "https://pan.quark.cn/"
            return {'parse': 0, 'url': proxy_url, 'header': header}
        play_url = ""
        if "原画" in flag:
            play_url = self.get_download(file_id)
        else:
            play_url = self.get_live_transcoding(file_id, flag)
        if not play_url:
            return {"parse": 0, "playUrl": "", "url": ""}
        header = self.s.headers
        header['Cookie'] = self.cookie
        header["Referer"] = "https://pan.quark.cn/"
        if ".m3u8" in play_url:
            return self.get_m3u8(play_url, header)
        go_url = self.go_proxy_video(play_url, header)
        return {'parse': 0, 'url': go_url, 'header': header}
        

    def get_download(self, file_id):
        """ 获取下载地址 """
        data = {'fids': [file_id]}
        result = self.s.post("https://drive-pc.quark.cn/1/clouddrive/file/download?pr=ucpro&fr=pc&uc_param_str=", json=data, timeout=10)
        json_data = result.json()
        if json_data.get("data"):
            return json_data["data"][0]["download_url"]
        return None

    def get_live_transcoding(self, file_id,  flag):
        """ 获取实时转码地址 """
        data = {
            "fid": file_id,
            "resolutions": "normal,low,high,super,2k,4k",
            "supports": "fmp4"
        }
        r = self.s.post(f"https://drive-pc.quark.cn/1/clouddrive/file/v2/play?pr=ucpro&fr=pc", json=data, timeout=10)
        json_data = r.json()
        if json_data["data"] and json_data["data"]["video_list"]:
            for video in json_data["data"]["video_list"]:
                if video["resolution"] == json_data["data"]["default_resolution"]:
                    return video["video_info"]["url"]
        return None

    def localProxy(self, params):
        if params["type"] == "image":
            url = params["url"]
            #r = self.s.get(url, allow_redirects=False)
            r = self.s.get(url)
            headers={}
            #headers['Location'] = r.headers['Location']
            return [200, "image/webp", r.content, headers] # 302重定向到url
        if params['type'] == "mpd":
            return self.proxyMpd(params)
        if params['type'] == "media":
            return self.proxyMedia(params)
        return None

    def go_proxy_video(self, url,header):
        """ go代理处理 """
        self.log(url)
        url = url.encode('utf-8')
        downloadUrl = f'http://127.0.0.1:7777?url={quote(url)}&thread={self.thread}'
        return downloadUrl

    def get_m3u8(self, url, header):
        """ M3U8 代理处理 """
        r = self.s.get(url, headers=header, timeout=10)
        m3u8_arr = r.text.split("\n")
        list_m3u8 = []
        site = url.rsplit("/", 1)[0] + "/"
        media_id = 0

        for one_line in m3u8_arr:
            this_one = one_line
            if ".ts" in one_line:
                """ 构造代理视频 URL """
                video_url = site + this_one
                encoded_url = self.e64(video_url)
                encoded_header = self.e64(json.dumps(header))
                this_one = f"{self.getProxyUrl()}&type=video&url={encoded_url}&header={encoded_header}"
                media_id += 1
            list_m3u8.append(this_one)
        m3u8_str = "\n".join(list_m3u8)
        content_type = r.headers["Content-Type"]
        return [r.status_code, content_type, io.BytesIO(m3u8_str.encode("utf-8")), r.headers]

    def get_play_format_list(self):
        """ 获取支持的播放格式列表 """
        return ["4K", "超清", "高清", "普画"] if self.is_vip else ["普画"]

    def get_play_format_quark_list(self):
        """ 获取夸克内部播放格式列表 """
        return ["4k", "2k", "super", "high", "normal", "low"] if self.is_vip else ["low"]
    def getSize(self, size):
        if size > 1024 * 1024 * 1024 * 1024.0:
            fs = "TB"
            sz = round(size / (1024 * 1024 * 1024 * 1024.0), 2)
        elif size > 1024 * 1024 * 1024.0:
            fs = "GB"
            sz = round(size / (1024 * 1024 * 1024.0), 2)
        elif size > 1024 * 1024.0:
            fs = "MB"
            sz = round(size / (1024 * 1024.0), 2)
        elif size > 1024.0:
            fs = "KB"
            sz = round(size / (1024.0), 2)
        else:
            fs = "KB"
            sz = round(size / (1024.0), 2)
        return str(sz) + fs

# 以下为BiliBiliVd所需函数
    def proxyMpd(self, params):
        content, durlinfos, mediaType = self.getDash(params)
        if mediaType == 'mpd':
            return [200, "application/dash+xml", content]
        else:
            url = ''
            urlList = [content] + durlinfos['durl'][0]['backup_url'] if 'backup_url' in durlinfos['durl'][0] and durlinfos['durl'][0]['backup_url'] else [content]
            for url in urlList:
                if 'mcdn.bilivideo.cn' not in url:
                    break
            header = self.b.headers.copy()
            if 'range' in params:
                header['Range'] = params['range']
            if '127.0.0.1:7777' in url:
                header["Location"] = url
                return [302, "video/MP2T", None, header]
            r = requests.get(url, headers=header, stream=True)
            return [206, "application/octet-stream", r.content]

    def proxyMedia(self, params, forceRefresh=False):
        _, dashinfos, _ = self.getDash(params)
        if 'videoid' in params:
            videoid = int(params['videoid'])
            dashinfo = dashinfos['video'][videoid]
        elif 'audioid' in params:
            audioid = int(params['audioid'])
            dashinfo = dashinfos['audio'][audioid]
        else:
            return [404, "text/plain", ""]
        url = ''
        urlList = [dashinfo['baseUrl']] + dashinfo['backupUrl'] if 'backupUrl' in dashinfo and dashinfo['backupUrl'] else [dashinfo['baseUrl']]
        for url in urlList:
            if 'mcdn.bilivideo.cn' not in url:
                break
        if url == "":
            return [404, "text/plain", ""]
        header = self.b.headers.copy()
        if 'range' in params:
            header['Range'] = params['range']
        r = requests.get(url, headers=header, stream=True)
        return [206, "application/octet-stream", r.content]

    def getDash(self, params, forceRefresh=False):
        aid = params['aid']
        cid = params['cid']
        url = unquote(params['url'])
        key = f'bilivdmpdcache_{aid}_{cid}'
        if forceRefresh:
            self.delCache(key)
        else:
            data = self.getCache(key)
            if data:
                return data['content'], data['dashinfos'], data['type']
        r = self.b.get(url,timeout=5)
        data = json.loads(self.cleanText(r.text))
        if data['code'] != 0:
            return '', {}, ''
        if not 'dash' in data['data']:
            purl = data['data']['durl'][0]['url']
            try:
                expiresAt = int(re.search(r'deadline=(\d+)', purl).group(1)) - 60
            except:
                expiresAt = int(time.time()) + 600
            if int(self.thread) > 0:
                purl = f'http://127.0.0.1:7777?url={quote(purl)}&thread={self.thread}'
            self.setCache(key, {'content': purl, 'type': 'mp4', 'dashinfos':  data['data'], 'expiresAt': expiresAt})
            return purl,  data['data'], 'mp4'
        cookiesDict, _, _ = self.getCookie()
        cookies = quote(json.dumps(cookiesDict))
        dashinfos = data['data']['dash']
        duration = dashinfos['duration']
        minBufferTime = dashinfos['minBufferTime']
        videoinfo = ''
        videoid = 0
        deadlineList = []
        for video in dashinfos['video']:
            try:
                deadline = int(re.search(r'deadline=(\d+)', video['baseUrl']).group(1))
            except:
                deadline = int(time.time()) + 600
            deadlineList.append(deadline)
            codecs = video['codecs']
            bandwidth = video['bandwidth']
            frameRate = video['frameRate']
            height = video['height']
            width = video['width']
            void = video['id']
            vidparams = params.copy()
            vidparams['videoid'] = videoid
            baseUrl = f'http://127.0.0.1:9978/proxy?do=py&type=media&cookies={quote(json.dumps(cookies))}&url={quote(url)}&aid={aid}&cid={cid}&videoid={videoid}'
            videoinfo = videoinfo + f"""          <Representation bandwidth="{bandwidth}" codecs="{codecs}" frameRate="{frameRate}" height="{height}" id="{void}" width="{width}">
            <BaseURL>{baseUrl}</BaseURL>
            <SegmentBase indexRange="{video['SegmentBase']['indexRange']}">
            <Initialization range="{video['SegmentBase']['Initialization']}"/>
            </SegmentBase>
          </Representation>\n"""
            videoid += 1
        audioinfo = ''
        audioid = 0
        # audioList = sorted(dashinfos['audio'], key=lambda x: x['bandwidth'], reverse=True)
        for audio in dashinfos['audio']:
            try:
                deadline = int(re.search(r'deadline=(\d+)', audio['baseUrl']).group(1))
            except:
                deadline = int(time.time()) + 600
            deadlineList.append(deadline)
            bandwidth = audio['bandwidth']
            codecs = audio['codecs']
            aoid = audio['id']
            aidparams = params.copy()
            aidparams['audioid'] = audioid
            baseUrl = f'http://127.0.0.1:9978/proxy?do=py&type=media&cookies={quote(json.dumps(cookies))}&url={quote(url)}&aid={aid}&cid={cid}&audioid={audioid}'
            audioinfo = audioinfo + f"""          <Representation audioSamplingRate="44100" bandwidth="{bandwidth}" codecs="{codecs}" id="{aoid}">
            <BaseURL>{baseUrl}</BaseURL>
            <SegmentBase indexRange="{audio['SegmentBase']['indexRange']}">
            <Initialization range="{audio['SegmentBase']['Initialization']}"/>
            </SegmentBase>
          </Representation>\n"""
            audioid += 1
        mpd = f"""<?xml version="1.0" encoding="UTF-8"?>
    <MPD xmlns="urn:mpeg:dash:schema:mpd:2011" profiles="urn:mpeg:dash:profile:isoff-on-demand:2011" type="static" mediaPresentationDuration="PT{duration}S" minBufferTime="PT{minBufferTime}S">
      <Period>
        <AdaptationSet mimeType="video/mp4" startWithSAP="1" scanType="progressive" segmentAlignment="true">
          {videoinfo.strip()}
        </AdaptationSet>
        <AdaptationSet mimeType="audio/mp4" startWithSAP="1" segmentAlignment="true" lang="und">
          {audioinfo.strip()}
        </AdaptationSet>
      </Period>
    </MPD>"""
        expiresAt = min(deadlineList) - 60
        self.setCache(key, {'type': 'mpd', 'content': mpd.replace('&', '&amp;'), 'dashinfos': dashinfos, 'expiresAt': expiresAt})
        return mpd.replace('&', '&amp;'), dashinfos, 'mpd'

    def getCookie(self):
        cookies = requests.utils.dict_from_cookiejar(self.b.cookies)
        bblogin = self.getCache('bblogin')
        if bblogin:
            imgKey = bblogin['imgKey']
            subKey = bblogin['subKey']
            return cookies, imgKey, subKey
        r = self.b.get("http://api.bilibili.com/x/web-interface/nav",timeout=10)
        data = json.loads(r.text)
        code = data["code"]
        if code == 0:
            imgKey = data['data']['wbi_img']['img_url'].rsplit('/', 1)[1].split('.')[0]
            subKey = data['data']['wbi_img']['sub_url'].rsplit('/', 1)[1].split('.')[0]
            self.setCache('bblogin', {'imgKey': imgKey, 'subKey': subKey, 'expiresAt': int(time.time()) + 1200})
            return cookies, imgKey, subKey
        r = self.fetch("https://www.bilibili.com/", headers=self.b.headers, timeout=5)
        cookies = r.cookies.get_dict()
        imgKey = ''
        subKey = ''
        return cookies, imgKey, subKey

    def getUserid(self):
        # 获取自己的userid(cookies拥有者)
        url = 'http://api.bilibili.com/x/space/myinfo'
        r = self.b.get(url, timeout=5)
        data = json.loads(self.cleanText(r.text))
        if data['code'] == 0:
            return data['data']['mid']

    def removeHtmlTags(self, src):
        from re import sub, compile
        clean = compile('<.*?>')
        return sub(clean, '', src)

