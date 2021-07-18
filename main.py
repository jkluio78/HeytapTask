# -*- coding: utf-8 -*-
# @Time    : 2021/7/14
# @Author  : hwkxk(丶大K丶)
# @Email   : k@hwkxk.cn

import requests,json,time,logging,traceback,os,random,notify,datetime,configparser

#用户登录全局变量
client = None
session = None
#日志基础配置
# 创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# 创建一个handler，用于写入日志文件
# w 模式会记住上次日志记录的位置
fh = logging.FileHandler('/tmp/log.txt', mode='a', encoding='utf-8')
fh.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(fh)
# 创建一个handler，输出到控制台
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("[%(asctime)s]:%(levelname)s:%(message)s"))
logger.addHandler(ch)

#读取用户配置信息
def readConfig():
    try:
        #用户配置信息
        global userconfig
        userconfig = configparser.ConfigParser()
        path ="./config.ini"
        userconfig.read(path,encoding="utf-8")
        return userconfig
    except Exception as e:
        print(traceback.format_exc())
        logging.error('1.请检查是否在目录下建立了config.ini')

#获取个人信息，判断登录状态
def get_infouser(HT_cookies,HT_UA):
    flag = False
    global session
    session = requests.Session()
    headers = {
        'Host': 'www.heytap.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': HT_UA,
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'cookie': HT_cookies
    }
    response = session.get('https://www.heytap.com/cn/oapi/users/web/member/info', headers=headers)
    response.encoding='utf-8'
    try:
        result = response.json()
        if result['code'] == 200:
            logger.info('=== 欢太商城任务 ===')
            logger.info('【登录成功】: ' + result['data']['realName'])
            flag = True
        else:
            logger.info('【登录失败】: ' + result['errorMessage'])
    except Exception as e:
        print(traceback.format_exc())
        logger.error('【登录】: 发生错误，原因为: ' + str(e))
    if flag:
        return session
    else:
        return False

#任务中心列表，获取任务及任务状态
def taskCenter():
    headers = {
    'Host': 'store.oppo.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'User-Agent': HT_UserAgent,
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'gzip, deflate, br',
    'cookie': HT_cookies,
    'referer':'https://store.oppo.com/cn/app/taskCenter/index'
    }
    res1 = client.get('https://store.oppo.com/cn/oapi/credits/web/credits/show', headers=headers)
    res1 = res1.json()
    return res1
        

#每日签到
#位置: APP → 我的 → 签到
def daySign_task():
    try:
        dated = time.strftime("%Y-%m-%d")
        headers = {
        'Host': 'store.oppo.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': HT_UserAgent,
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'cookie': HT_cookies,
        'referer':'https://store.oppo.com/cn/app/taskCenter/index'
        }
        res = taskCenter()
        res = res['data']['userReportInfoForm']['gifts']
        for data in res:
            if data['date'] == dated:
                qd = data
        if qd['today'] == False:
            data = "amount=" + str(qd['credits'])
            res1 = client.post('https://store.oppo.com/cn/oapi/credits/web/report/immediately', headers=headers,data=data)
            res1 = res1.json()
            if res1['code'] == 200:
                logger.info('【每日签到成功】: ' + res1['data']['message'])
            else:
                logger.info('【每日签到失败】: ' + res1)
        else:
            print(str(qd['credits']),str(qd['type']),str(qd['gift']))
            if len(qd['type']) == 0:
                data = "amount=" + str(qd['credits'])
            else:
                data = "amount=" + str(qd['credits']) + "&type=" + str(qd['type']) + "&gift=" + str(qd['gift'])
            res1 = client.post('https://store.oppo.com/cn/oapi/credits/web/report/immediately',  headers=headers,data=data)
            res1 = res1.json()
            if res1['code'] == 200:
                logger.info('【每日签到成功】: ' + res1['data']['message'])
            else:
                logger.info('【每日签到失败】')
        time.sleep(1)
    except Exception as e:
        print(traceback.format_exc())
        logging.error('【每日签到】: 错误，原因为: ' + str(e))



#浏览商品 10个sku +20 分
#位置: APP → 我的 → 签到 → 每日任务 → 浏览商品
def daily_viewgoods():
    try:
        headers = {
        'clientPackage': 'com.oppo.store',
        'Host': 'msec.opposhop.cn',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': 'okhttp/3.12.12.200sp1',
        'Accept-Encoding': 'gzip',
        'cookie': HT_cookies,
        }
        res = taskCenter()
        res = res['data']['everydayList']
        for data in res:
            if data['name'] == '浏览商品':
                qd = data
        if qd['completeStatus'] == 0:
            shopList = client.get('https://msec.opposhop.cn/goods/v1/SeckillRound/goods/3016?pageSize=12&currentPage=1')
            res = shopList.json()
            if res['meta']['code'] == 200:
                for skuinfo in res['detail']:
                    skuid = skuinfo['skuid']
                    print('正在浏览商品ID：', skuid)
                    client.get('https://msec.opposhop.cn/goods/v1/info/sku?skuId='+ str(skuid), headers=headers)
                    time.sleep(5)
                res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
                if res2 == True:
                    logger.info('【每日浏览商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
                else:
                    logger.info('【每日浏览商品】: ' + "领取积分奖励出错！")
            else:
                logger.info('【每日浏览商品】: ' + '错误，获取商品列表失败')
        elif qd['completeStatus'] == 1:
            res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
            if res2 == True:
                logger.info('【每日浏览商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                logger.info('【每日浏览商品】: ' + '领取积分奖励出错！')
    except Exception as e:
        print(traceback.format_exc())
        logging.error('【每日浏览任务】: 错误，原因为: ' + str(e))

def daily_sharegoods():
    try:
        headers = {
        'clientPackage': 'com.oppo.store',
        'Host': 'msec.opposhop.cn',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': 'okhttp/3.12.12.200sp1',
        'Accept-Encoding': 'gzip',
        'cookie': HT_cookies,
        }
        daySignList = taskCenter()
        res = daySignList
        res = res['data']['everydayList']
        for data in res:
            if data['name'] == '分享商品到微信':
                qd = data
        if qd['completeStatus'] == 0:
            count = qd['readCount']
            endcount = qd['times']
            while (count <= endcount):
                client.get('https://msec.opposhop.cn/users/vi/creditsTask/pushTask?marking=daily_sharegoods', headers=headers)
                count += 1
            res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
            if res2 == True:
                logger.info('【每日分享商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                logger.info('【每日分享商品】: ' + '领取积分奖励出错！')
        elif qd['completeStatus'] == 1:
            res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
            if res2 == True:
                logger.info('【每日分享商品】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                logger.info('【每日分享商品】: ' + '领取积分奖励出错！')
    except Exception as e:
        print(traceback.format_exc())
        logging.error('【每日分享商品】: 错误，原因为: ' + str(e))

def daily_viewpush():
    try:
        headers = {
        'clientPackage': 'com.oppo.store',
        'Host': 'msec.opposhop.cn',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'User-Agent': 'okhttp/3.12.12.200sp1',
        'Accept-Encoding': 'gzip',
        'cookie': HT_cookies,
        }
        daySignList = taskCenter()
        res = daySignList
        res = res['data']['everydayList']
        for data in res:
            if data['name'] == '点推送消息':
                qd = data
        if qd['completeStatus'] == 0:
            count = qd['readCount']
            endcount = qd['times']
            while (count <= endcount):
                client.get('https://msec.opposhop.cn/users/vi/creditsTask/pushTask?marking=daily_viewpush', headers=headers)
                count += 1
            res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
            if res2 == True:
                logger.info('【每日点推送】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                logger.info('【每日点推送】: ' + '领取积分奖励出错！')
        elif qd['completeStatus'] == 1:
            res2 = cashingCredits(qd['marking'],qd['type'],qd['credits'])
            if res2 == True:
                logger.info('【每日点推送】: ' + '任务完成！积分领取+' + str(qd['credits']))
            else:
                logger.info('【每日点推送】: ' + '领取积分奖励出错！')
    except Exception as e:
        print(traceback.format_exc())
        logging.error('【每日推送消息】: 错误，原因为: ' + str(e))


#执行完成任务领取奖励
def cashingCredits(info_marking,info_type,info_credits):
    headers = {
    'Host': 'store.oppo.com',
    'clientPackage': 'com.oppo.store',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'User-Agent': HT_UserAgent,
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'gzip, deflate, br',
    'cookie': HT_cookies,
    'Origin': 'https://store.oppo.com',
    'X-Requested-With': 'com.oppo.store',
    'referer':'https://store.oppo.com/cn/app/taskCenter/index?us=gerenzhongxin&um=hudongleyuan&uc=renwuzhongxin'
    }

    data = "marking=" + str(info_marking) + "&type=" + str(info_type) + "&amount=" + str(info_credits)
    res = client.post('https://store.oppo.com/cn/oapi/credits/web/credits/cashingCredits', data=data, headers=headers)
    res = res.json()
    if res['code'] == 200:
        return True
    else:
        return False

#活动平台抽奖通用接口
def lottery(datas):
    headers = {
    'clientPackage': 'com.oppo.store',
    'Accept': 'application/json, text/plain, */*;q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Connection': 'keep-alive',
    'User-Agent': HT_UserAgent,
    'Accept-Encoding': 'gzip, deflate',
    'cookie': HT_cookies,
    'Origin': 'https://hd.oppo.com',
    'X-Requested-With': 'XMLHttpRequest',
    }
    res = client.post('https://hd.oppo.com/platform/lottery', data=datas, headers=headers)
    res = res.json()
    return res

#天天积分翻倍活动 - 长期 最多3次
def tiantianjifen_lottery():
    dated = int(time.time())
    endtime = time.mktime(time.strptime("2020-1-1 23:59:59", '%Y-%m-%d %H:%M:%S'))#设置活动结束日期
    if dated < endtime :
        x=1
        while x <= 3:
            data = "aid=675&lid=1289&mobile=&authcode=&captcha=&isCheck=0&source_type=501&s_channel=oppo_appstore&sku=&spu="
            res = lottery(data)
            print(res)
            goods_name = res['data']['goods_name']
            logger.info('【天天积分翻倍活动】第'+ str(x) +'次，获得:'+ str(goods_name))
            x += 1
            time.sleep(5)
    else:
        logger.info('【天天积分翻倍活动已结束，不再执行】')

#
#—————短期活动任务↓———————
#

#超级会员日 瓜分1亿积分转盘抽奖2021.7.12-2021.7.18  每日1次
def vipdate_lottery():
    dated = int(time.time())
    endtime = time.mktime(time.strptime("2021-7-18 23:59:59", '%Y-%m-%d %H:%M:%S'))#设置活动结束日期
    if dated < endtime :
        data = "aid=1589&lid=1486&mobile=&authcode=&captcha=&isCheck=0&source_type=501&s_channel=oppo_appstore&sku=&spu="
        res = lottery(data)
        print(res)
        msg = res['msg']
        goods_name = res['data']['goods_name']
        logger.info('【瓜分1亿转盘抽奖活动】获得:'+ str(goods_name))
    else:
        logger.info('【瓜分1亿转盘抽奖活动已结束，不再执行】')

#智能生活0元抽奖-宠粉转盘
def zhinengshenghuo_lottery():
    dated = int(time.time())
    endtime = time.mktime(time.strptime("2022-1-1 23:59:59", '%Y-%m-%d %H:%M:%S')) #设置活动结束日期
    if dated < endtime :
        x=1
        while x <= 5:
            data = "aid=1270&lid=1431&mobile=&authcode=&captcha=&isCheck=0&source_type=501&s_channel=oppo_appstore&sku=&spu="
            res = lottery(data)
            print(res)
            goods_name = res['data']['goods_name']
            logger.info('【智能生活转盘】第'+ str(x) +'次，获得:'+str(goods_name))
            x += 1
            time.sleep(5)
    else:
        logger.info('【智能生活0元抽奖活动已结束，不再执行】')

#reakme宠粉计划-幸运抽奖-转盘
def reakme_lottery():
    dated = int(time.time())
    endtime = time.mktime(time.strptime("2022-1-1 23:59:59", '%Y-%m-%d %H:%M:%S')) #设置活动结束日期
    if dated < endtime :
        data = "aid=1182&lid=1429&mobile=&authcode=&captcha=&isCheck=0&source_type=501&s_channel=oppo_appstore&sku=&spu="
        res = lottery(data)
        goods_name = res['data']['goods_name']
        logger.info('【reakme宠粉计划转盘】获得:'+ str(goods_name))
        time.sleep(3)
    else:
        logger.info('【reakme宠粉计划活动已结束，不再执行】')


#腾讯云函数入口
def main_handler(event, context):
    
    users = readConfig()
    #清空上一个用户的日志记录
    open('/tmp/log.txt',mode='w',encoding='utf-8')
    global client
    global HT_cookies
    global HT_UserAgent
    sleeptime = 10
    try:        
        if (users.has_option("config", "sleeptime")):
            sleeptime = users.getint("config","sleeptime")
    except Exception as e:
        print(traceback.format_exc())
        logging.error(' 错误，原因为: ' + str(e))
    logger.info('=== 欢太商城任务 ===')
    x=0
    while x <= 9:
        HT_cookies = ""
        HT_UserAgent = ""
        client = False
        if (x == 0):
            HT_cookies = users.get("config","cookies")
            HT_UserAgent = users.get("config","User-Agent")
        else:
            if (users.has_option("config", "cookies"+str(x))):
                HT_cookies = users.get("config","cookies"+str(x))
            else:
                break
            if (users.has_option("config", "User-Agent"+str(x))):
                HT_UserAgent = users.get("config","User-Agent"+str(x))
            
        if (HT_cookies == ""):
            break
        if (HT_UserAgent == ""):
            HT_UserAgent = users.get("config","User-Agent")
        # print(HT_cookies,HT_UserAgent)
        logger.info('【第'+str(x+1)+'个账号开始签到】')
        client = get_infouser(HT_cookies,HT_UserAgent)

        if client != False:
            daySign_task() #执行每日签到
            daily_viewgoods() #执行每日商品浏览任务
            daily_sharegoods() #执行每日商品分享任务
            daily_viewpush() #执行每日点推送任务
            tiantianjifen_lottery() #天天积分翻倍
            vipdate_lottery() #超级会员日转盘
            zhinengshenghuo_lottery() #智能生活-0元抽奖-宠粉转盘
            reakme_lottery() #reakme宠粉计划 转盘
        else:
            logger.info("账号[cookies"+str(x+1)+"]登录失败，换下一个账号")
            x += 1
            continue
        x += 1
        logger.info(str(sleeptime)+"秒后换下一个账号签到")
        time.sleep(sleeptime)


    if users.has_option("dingding", 'dingtalkWebhook'):
        notify.sendDing(users.get("dingding","dingtalkWebhook")) #钉钉推送日记          
    if users.has_option("telegramBot", 'tgToken'):
        notify.sendTg(users.get("telegramBot","tgToken"),users.get("telegramBot","tgUserId")) #TG机器人推送日记
    if users.has_option("pushplus", 'pushplusToken'):
        notify.sendPushplus(users.get("pushplus","pushplusToken")) #push+ 推送日记
    if users.has_option("enterpriseWechat", 'id'):
        notify.sendWechat(users.get("enterpriseWechat","id"),users.get("enterpriseWechat","secret"),users.get("enterpriseWechat","agentld")) #企业微信通知
    #if users.has_option("IFTTT", 'apiKey'):
      #  notify.sendIFTTT(users.get("IFTTT","apiKey"),users.get("IFTTT","eventName")) #IFTTT 推送日记
    if users.has_option("Bark", 'Barkkey'):
        notify.sendBark(users.get("Bark","Barkkey"),users.get("Bark","Barksave")) #Bark推送助手
    
#主函数入口
if __name__ == "__main__":
    main_handler(event=None, context=None)

