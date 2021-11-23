import requests
import json
import random

data = {
    "reqType":0,
    "perception": {
        "inputText": {
            "text": ""
        }
    },
    "userInfo": {
        "apiKey": "",
        "userId": ""
    }
}

#图灵API key 需要官网申请 可以多个key随机使用
apikey = ["1", "2", "3", "4","5"]

apiurl = 'http://openapi.turingapi.com/openapi/api/v2'    


def GetChatText(text, uid):
    resp = ''
    if text: 
        data["perception"]["inputText"]["text"] = text.replace(' ', ',')
        data["userInfo"]["userId"] = uid
        data["userInfo"]["apiKey"] = apikey[random.randint(1, 4)]
        response = requests.post(apiurl, data=json.dumps(data)).json()
        for result in response['results']:  
            resp += result['values']['text']
    return resp


def process_command(update, context):
    return

    
def process_msg(update, context):
    if update.message.chat.type == 'group' and update.message.text.startswith(context.bot.name): 
        text = GetChatText(update.message.text.replace(context.bot.name, '').lstrip(), str(update.message.from_user.id))
    elif update.message.chat.type == 'private' :
        text = GetChatText(update.message.text, str(update.message.chat.id))
    if text: update.message.reply_text(text)
    
    
def process_callback(update, context):
    return         
