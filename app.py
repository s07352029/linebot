from flask import Flask, request, abort

import urllib.request, json
import requests
from bs4 import BeautifulSoup

import os
import sys
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

ACCESS_TOKEN= os.environ['ACCESS_TOKEN']
SECRET= os.environ['CHANNEL_SECRET']

# Channel Access Token
line_bot_api = LineBotApi(ACCESS_TOKEN)
# Channel Secret
handler = WebhookHandler(SECRET)

pm_site = {}

@app.route("/")
def hello_world():
    return "hello world!"


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg=event.message.text
    if '右轉' in msg or '左轉' in msg:
        message=TextSendMessage(text='收到(≧ω≦)')
        line_bot_api.reply_message(event.reply_token,message)
    elif '出發' in msg or '開始' in msg or '開始記錄' in msg:
        message=TextSendMessage(text='已開始記錄(๑✧∀✧๑)')
        line_bot_api.reply_message(event.reply_token,message)
    elif '到達' in msg or '停止' in msg or '停止記錄' in msg:
        message=TextSendMessage(text='已停止記錄(๑>ᴗ<๑)')
        line_bot_api.reply_message(event.reply_token,message)
    else:
        message=TextSendMessage(text='請要繼續支持鄧紫棋唷<3')
        line_bot_api.reply_message(event.reply_token,message)

def find_bookls(kw):
    with open("ESLITE.json",'r') as load_f:
        load_dict = json.load(load_f)
    x = load_dict['items']
    ans = ()
    for i in x:
        #if i['title'] == "title":
        if i['title'].find(str(kw))== -1:
            pass
#             print("")
        else:
            ans= (i['title']+i['link'])
#             print (i['title'], i['link'])
    return ans

def loadPMJson():
    with urllib.request.urlopen("http://opendata2.epa.gov.tw/AQX.json") as url:
        data = json.loads(url.read().decode())
        for ele in data:
            pm_site[ele['SiteName']] = ele['PM2.5']

def getCls(cls_prefix):
    ret_cls = []
    urlstr = 'https://course.thu.edu.tw/search-result/107/1/'
    postfix = '/all/all'
    
    qry_cls = urlstr + cls_prefix + postfix
    
    resp = requests.get(qry_cls)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')
    clsrooms = soup.select('table.aqua_table tbody tr')
    for cls in clsrooms:
        cls_info = cls.find_all('td')[1]
        cls_name = cls_info.text.strip()
        sub_url = 'https://course.thu.edu.tw' + cls_info.find('a')['href']
        ret_cls.append(cls_name + " " + sub_url)
        break
#         ret_cls = ret_cls + sub_url + "\n"

    return ret_cls
        
            
import os
if __name__ == "__main__":
    # load PM2.5 records
    #loadPMJson()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
