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
            self.classname = extendDict['folders']
        except:
            self.classname = []
        try:
            self.is_vip = self.get_vip()
            self.log("是否VIP：", self.is_vip)
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
        result['class'] = []
        r = self.s.get('https://pan.quark.cn/account/info', timeout=10).json()
        if r['data']:
            nickname = r['data']['nickname']
            self.log(nickname)
            #fname = [self.type_name, self.fid]
            for i in self.classname:
                result['class'].append({"type_name": i["name"], "type_id": i["fid"], "type_flag": "1"})
            self.log(result)
            self.idList = {i["type_id"]:i["type_name"] for i in result['class']}
        else:
            result['class'] = [{"type_name": "无效cookie", "type_id": "error", "type_flag": "1"}]
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        videos = []
        pName = None
        if "folder" in tid:
            fid = json.loads(tid)
            tid = fid['folder']
            pName = fid['fileName']
        self.log(tid)
        params = {"shareId":"","folder":"","parentId":"","fileType":"","fileName":""}
        if tid == "error":
            return result
        # r = self.s.get(f'https://drive-pc.quark.cn/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid={tid}&_page={pg}&_size=100&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc', headers=self.headers_host,timeout=10)
        # data = r.json()
        # vodList = data["data"]['list']page = 1

        folderList,videoList,subtList = self.getAllFile(tid)
        if folderList != []:
            for folder in folderList:
                params['folder'] = folder["fid"]
                params['parentId'] = folder["pdir_fid"]
                params['fileType'] = "folder"
                params['fileName'] = folder['fileName']
                scrapeInfo = self.getscrape(folder["fid"])
                vod_pic = scrapeInfo["pic"] if scrapeInfo.get("pic") else folder['img']
                videos.append({
                    "vod_id": json.dumps(params, ensure_ascii=False),
                    "vod_name": folder['fileName'],
                    "vod_pic": vod_pic,
                    "vod_tag": "folder",
                    "style": {"type": "list"} if vod_pic==""  else  {"type": "rect","ratio": 0.75} ,
                    "vod_remarks": "文件夹"
                })

        if videoList != []:
            self.setCache(f"quarkPlayList_{params['parentId']}", videoList)
            self.setCache('quarkSubtList', subtList)
            for video in videoList:
                params['folder'] = video["fid"]
                params['parentId'] = video["pdir_fid"]
                params['fileType'] = "file"
                params['fileName'] = self.idList[tid] if pName is None else pName
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
        result = {
            'list': videos,
            'page': pg,
            'pagecount': 1,  # 设置一个较大的值
            'limit': 80,
            'total': 999999
        }
        # result['page'] = data['metadata']['_page']
        # result['pagecount'] = -1 * (-data['metadata']['_total'] // 100)
        # result['limit'] = 100
        # result['total'] = data['metadata']['_total']
        return result


    def detailContent(self, did):
        self.log(did)
        params = json.loads(did[0])
        result = {}
        pName = params['fileName'].split("：")[-1]
        fileType = params['fileType']
        if fileType == 'file':
            videoList = self.getCache(f"quarkPlayList_{params['parentId']}")
            subtList = self.getCache(f"quarkSubtList") if self.getCache(f"quarkSubtList") else []
            if not videoList:
                # return {'list': [], "msg": "无可播放资源"}
                folderList,videoList,subtList = self.getAllFile(params['parentId'])

            # try:
            #     videoList = sorted(fileList, key=lambda x: x['fileName'])
            # except:
            #     pass
            
            for video in videoList:
                subList = []
                # self.log(f"文件名:{video['fileName']}")
                for subt in subtList:
                    subName = splitext(subt['fileName'])[0]
                    # self.log(f"字幕名:{subName}")
                    score = self.match_score(splitext(video['fileName'])[0], subName)
                    # 过滤并排序
                    if score[0] < 9:  # 只保留有效匹配
                        subList.append(
                            {"dis": score, "subName": subName, "subFormat": splitext(subt['fileName'])[1], 'fid': subt['fid']})
                            # {"dis": 0, "subName": subName, "subFormat": splitext(sub['fileName'])[1], 'fid': sub['fid']})
                try:
                    subList = sorted(subList, key=lambda x: x['dis'][0]*10 + x['dis'][1])
                except:
                    pass
                if subList:
                    video['fid']=video['fid']+"@@@"+'+'.join(f"{i['fid']}" for i in subList)
            vod_play_url = '#'.join(f"{i['fileName']}${i['fid']}" for i in videoList)
            # 获取播放源列表
            play_from_tmp = ["夸克原画","夸克预览"]
            play_url = []
            # 使播放链接与播放源数量对应
            for _ in play_from_tmp:
                play_url.append(vod_play_url)
            scrapeInfo = self.getscrape(params['parentId'])
            videos = [{
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
            result['list'] = videos
            return result

    def searchContent(self, key, quick, pg="1"):
        params = {"shareId":"","folder":"","parentId":"","fileType":"file","fileName":""}
        videos = []
        r = self.s.get(f'https://drive-pc.quark.cn/1/clouddrive/file/search?pr=ucpro&fr=pc&uc_param_str=&q={key}&_page={pg}&_size=50&_fetch_total=1&_sort=file_type:desc,updated_at:desc&_is_hl=1', headers={'Referer': 'https://pan.quark.cn/', 'Host': 'drive-pc.quark.cn', 'Connection': 'Keep-Alive'},timeout=10)
        data = r.json()
        vodList = data["data"]["list"]
        for vod in vodList:
            scrapeInfo = self.getscrape(vod["fid"])
            params["folder"] = vod['fid']
            params["parentId"] = vod['pdir_fid']
            params["fileName"] = vod['file_name']
            videos.append({
                'vod_tag': "folder" if int(vod['file_type']) == 0 else "file",
                'vod_id': json.dumps(params, ensure_ascii=False),
                'vod_name': params["fileName"],
                'vod_pic': scrapeInfo["pic"] if scrapeInfo.get("pic") else self.vodPic,
                'vod_year': "",
                'vod_remarks': "我的夸克"
            })
        return {'list': videos,'page': pg}

    def playerContent(self, flag, file_id, vipFlags):     
        result = {}
        subs = []
        videoid = file_id.split("@@@")[0]
        subids=file_id.split("@@@")[1] if "@@@" in file_id else ""
        subids = subids.split("+") if subids != "" else []
        subtList = self.getCache(f"quarkSubtList") if self.getCache(f"quarkSubtList") else []
        if subids:
            for subt in subtList:
                for subid in subids:
                    if subt['fid'] == subid:
                        subName = splitext(subt['fileName'])[0]
                        subExt = splitext(subt['fileName'])[1]
                        if subExt == '.srt':
                            subFormat = 'application/x-subrip'
                        elif subExt == '.ass':
                            subFormat = 'application/x-subtitle-ass'
                        elif subExt == '.ssa':
                            subFormat = 'text/x-ssa'
                        else:
                            subFormat = 'text/plain'
                        subUrl = f'http://127.0.0.1:9978/proxy?do=py&type=sub&format={subFormat}&subid={subid}'
                        subs.append({'url': subUrl, 'name': subName, 'format': subFormat})
                        #[{'url': 'http://127.0.0.1:9978/proxy?do=py&format=application/x-subrip&type=sub&url=https://16158.kstore.space/subtitle.srt', 'name': '测试', 'format': 'application/x-subrip'}]
                    
        
        play_url = ""
        if "原画" in flag:
            play_url = self.get_download(videoid)
        else:
            play_url = self.get_live_transcoding(videoid)
        if not play_url:
            return {"parse": 0, "playUrl": "", "url": ""}
        header = self.s.headers
        header['Cookie'] = self.cookie
        header["Referer"] = "https://pan.quark.cn/"
        # 新增：play_url为列表时，处理所有偶数位url
        if isinstance(play_url, list):
            for i in range(1, len(play_url), 2):
                url_item = play_url[i]
                if isinstance(url_item, str) and url_item and ".m3u8" not in url_item:
                    play_url[i]=self.go_proxy_video(url_item, header)
            return {'parse': 0, 'url': play_url, 'header': header}
        if ".m3u8" not in play_url:
            play_url = self.go_proxy_video(play_url, header)
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = play_url
        result["header"] = header
        result["subs"] = subs
        return result
        

    def get_download(self, file_id):
        """ 获取下载地址 """
        data = {'fids': [file_id]}
        result = self.s.post("https://drive-pc.quark.cn/1/clouddrive/file/download?pr=ucpro&fr=pc&uc_param_str=", json=data, timeout=10)
        json_data = result.json()
        self.log(json_data)
        if json_data.get("data"):
            return json_data["data"][0]["download_url"]
        return None

    def get_live_transcoding(self, file_id):
        """ 获取实时转码地址 """
        data = {
            "fid": file_id,
            "resolutions": "normal,low,high,super,2k,4k",
            "supports": "fmp4"
        }
        r = self.s.post(f"https://drive-pc.quark.cn/1/clouddrive/file/v2/play?pr=ucpro&fr=pc", json=data, timeout=10)
        json_data = r.json()
        print(json_data)
        urls = []
        if json_data["data"] and json_data["data"]["video_list"]:
            for video in json_data["data"]["video_list"]:
                urls.append(video["resolution"])
                urls.append(video["video_info"]["url"])
            return urls
        return None

    def localProxy(self, params):
        if params["type"] == "image":
            url = params["url"]
            #r = self.s.get(url, allow_redirects=False)
            r = self.s.get(url)
            headers={}
            #headers['Location'] = r.headers['Location']
            return [200, "image/webp", r.content, headers] 
        if params['type'] == "sub":
            subid = params["subid"]
            format = params["format"]
            url = self.get_download(subid)
            header = self.s.headers
            header['Cookie'] = self.cookie
            header["Referer"] = "https://pan.quark.cn/"
            header["Location"] = url
            return [302, format, None, header] # 302重定向到url
        return None

    def go_proxy_video(self, url,header):
        """ go代理处理 """
        self.log(url)
        # return url
        url = url.encode('utf-8')
        downloadUrl = f'http://127.0.0.1:7777?url={quote(url)}&thread={self.thread}'
        return downloadUrl

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


    # 定义匹配优先级函数
    def match_score(self, video_stem, sub_name):
        # 完全匹配（无额外后缀）
        if sub_name == video_stem:
            return (0, 0)  # 最高优先级
        # 尝试匹配 "视频名.语言" 模式
        pattern = rf"^{re.escape(video_stem)}\.([a-zA-Z\-]*)$"
        match = re.match(pattern, sub_name)
        if match:
            lang = match.group(1).lower()
            # 中文优先于英文，其他靠后
            if 'zh' in lang or 'chi' in lang:
                return (1, 0)
            elif 'en' in lang or 'eng' in lang:
                return (1, 1)
            else:
                return (1, 2)
        # 其他情况（如包含额外字符）不匹配
        return (9, 9)
    
    
    def getAllFile(self, tid):
        pgs = 1
        vodList = []
        while True:
            r = self.s.get(f'https://drive-pc.quark.cn/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid={tid}&_page={pgs}&_size=100&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc', headers={'Referer': 'https://pan.quark.cn/', 'Host': 'drive-pc.quark.cn', 'Connection': 'Keep-Alive'},timeout=10)
            data = r.json()
            # self.log(str(data))
            time.sleep(0.05)
            vodList += data["data"]['list']
            pgs += 1
            if pgs > -1 * (-data['metadata']['_total'] // 100):
                break
        self.log("共循环次数："+str(pgs-1))
        subtList = []
        videoList = []
        folderList = []
        for vod in vodList:
            try:
                if vod['big_thumbnail'].startswith('http'):
                    imgUrl = vod['big_thumbnail']
                    img = f'{self.getProxyUrl()}&type=image&url={quote(imgUrl)}'
            except:
                img = self.vodPic
            if vod['dir']:
                folderList.append({'fid': vod["fid"], 'pdir_fid':vod["pdir_fid"],'fileName': vod['file_name'], "img": img, "remark": "文件夹"})
            else:
                if splitext(vod['file_name'])[1] in ['.mp4', '.mpg', '.mkv', '.ts', '.TS', '.avi', '.flv', '.rmvb','.mp3', '.flac', '.wav', '.wma', '.m4a', '.dff']:
                    size = self.getSize(vod['size'])
                    videoList.append({'fid': vod["fid"], 'pdir_fid':vod["pdir_fid"],'fileName': vod['file_name'], "img": img, "remark": size})
                elif splitext(vod['file_name'])[1] in ['.ass', '.ssa', '.srt']:
                    subtList.append({'fid': vod["fid"], 'fileName': vod['file_name']})
        return folderList,videoList,subtList