import telegram
import database as db
import lockmanage as lock
from telegram import InputMediaVideo, InputMediaPhoto

MAIN_CONFIG = db.read("config")
CONFIG = db.read("sub_config")
DB = db.read("sub_data")
MEDIAS = {} # 暂存组图片或视频数据

post_type = {"real":"保留",  "anonymous":"匿名" }

def contribute_close(bot, query):
    reply = query.message.reply_to_message
    root = DB[str(CONFIG['Group_ID']) + ':' + str(reply.message_id)]
    root['Closed'] = True
    root['Editor_ID'] = query.from_user.name
    
    msg = "审核未通过\n投稿人：{0}\n来源：{1}\n审核人：{2}".format(root['Sender_Name'], post_type[root['Type']], query.from_user.name)    
    query.edit_message_text(text=msg)
    bot.send_message(chat_id=root['Sender_ID'], text="您的稿件未通过审核", reply_to_message_id=root['Original_MsgID'])
    db.save("sub_data", DB, True)
    if reply.media_group_id: MEDIAS.pop(reply.media_group_id)


def contribute_post(bot, query, ptype, cid):
    reply = query.message.reply_to_message
    if reply.media_group_id:
        if not reply.media_group_id in MEDIAS.keys(): return
        bot.send_media_group(chat_id=cid, media=MEDIAS[reply.media_group_id])
        MEDIAS.pop(reply.media_group_id)
    else:
        if ptype == "real":
            bot.forward_message(chat_id=cid, from_chat_id=CONFIG['Group_ID'], message_id=reply.message_id)
        else: 
            if reply.audio:
                bot.send_audio(chat_id=cid, audio=reply.audio, caption=reply.caption)
            elif reply.document:
                bot.send_document(chat_id=cid, document=reply.document, caption=reply.caption)
            elif reply.voice:
                bot.send_voice(chat_id=cid, voice=reply.voice, caption=reply.caption)
            elif reply.video:
                bot.send_video(chat_id=cid, video=reply.video, caption=reply.caption)
            elif reply.photo:
                bot.send_photo(chat_id=cid, photo=reply.photo[0], caption=reply.caption)
            else:
                reply.send_message(chat_id=cid, text=reply.text_markdown, parse_mode=telegram.ParseMode.MARKDOWN)
        
    root = DB[str(CONFIG['Group_ID']) + ':' + str(reply.message_id)]
    root['Posted'] = True
    root['Channel_ID'] = cid
    root['Editor_ID'] = query.from_user.name
    
    msg = "已采纳\n投稿人：{0}\n来源：{1}\n审核人：{2}".format(root['Sender_Name'], post_type[root['Type']], query.from_user.name) 
    query.edit_message_text(text=msg)
    bot.send_message(chat_id=root['Sender_ID'], text="您的稿件已过审，感谢您对我们的支持", reply_to_message_id=root['Original_MsgID'])
    db.save("sub_data", DB, True)


def process_command(update, context):
    if update.message.from_user.id != MAIN_CONFIG['Admin']: return
        
    command = update.message.text[1:].replace(MAIN_CONFIG['Username'], '').lower()
    args = command.split(" ")
    if args[0] == 'setsubgroup':
        CONFIG['Group_ID'] = update.message.chat_id
        db.save("sub_config", CONFIG)
        update.message.reply_text(text="已设置本群为审稿群")
        return
    elif args[0] == 'setsubchannel' and len(args) == 3:
        CONFIG['Publish_Channel'][args[1]] = args[2]
        db.save("sub_config", CONFIG)
        update.message.reply_text(text=args[2] + "已设置为发布频道")
        return


def process_msg(update, context):
    if not update.message.video and not update.message.photo: return  # 只接收图片和视频投稿
    
    if lock.user_check(update.message.from_user.id): return  # 检查用户锁避免和批量转发冲突
    if update.message.media_group_id:  # 用于一组图片和视频转发
        if update.message.media_group_id not in MEDIAS.keys(): MEDIAS[update.message.media_group_id] = []
        if update.message.video: MEDIAS[update.message.media_group_id].append(InputMediaVideo(update.message.video, caption=update.message.caption))
        if update.message.photo: MEDIAS[update.message.media_group_id].append(InputMediaPhoto(media=update.message.photo[len(update.message.photo) - 1], caption=update.message.caption))
        if len(MEDIAS[update.message.media_group_id]) > 1: return
        
    if update.message.from_user.id == update.message.chat_id:
        if update.message.forward_from or update.message.forward_from_chat:
            if update.message.forward_from_chat or update.message.forward_from.id:
                markup = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("是", callback_data='contribute:anonymous')], 
                                                        [telegram.InlineKeyboardButton("取消投稿", callback_data='contribute:cancel')]])
                update.message.reply_text(text="即将完成投稿...\n⁠转发的消息将不保留消息来源，是否继续投稿？)", reply_markup=markup, reply_to_message_id=update.message.message_id)
        else:
            markup = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("是" , callback_data='contribute:real'),
                                                     telegram.InlineKeyboardButton("否", callback_data='contribute:anonymous')],
                                                    [telegram.InlineKeyboardButton("取消投稿", callback_data='contribute:cancel')]])     
            update.message.reply_text(text="即将完成投稿...\n⁠您是否想要保留消息来源(保留消息发送者用户名)", reply_markup=markup, reply_to_message_id=update.message.message_id)

          
def process_callback(update, context):
    query = update.callback_query
    cmds = query.data.split(":")
    if cmds[0] != 'contribute': return
    
    if cmds[1] == 'receive' and query.message.chat_id == CONFIG['Group_ID']:
        contribute_post(context.bot, query, cmds[2], cmds[3])
        return
    elif cmds[1] == 'close' and query.message.chat_id == CONFIG['Group_ID']:
        contribute_close(context.bot, query)
        return    
    elif cmds[1] == 'cancel':
        query.edit_message_text(text="已取消投稿")
        return
    elif cmds[1] == 'real' or cmds[1] == 'anonymous':
        query.edit_message_text(text="感谢您的投稿，稍后会通知您结果") 
        if query.message.reply_to_message.media_group_id:
            if not query.message.reply_to_message.media_group_id in MEDIAS.keys(): return
            fwd_group_msg = context.bot.send_media_group(chat_id=CONFIG['Group_ID'], media=MEDIAS[query.message.reply_to_message.media_group_id])
            if not fwd_group_msg: return
            MEDIAS.pop(query.message.reply_to_message.media_group_id) 
            fwd_msg = fwd_group_msg[0] 
            for group_msg in fwd_group_msg:
                if group_msg.media_group_id not in MEDIAS.keys():  MEDIAS[group_msg.media_group_id] = []
                caption = None
                if cmds[1] == 'real' and not MEDIAS[group_msg.media_group_id]: 
                    caption = group_msg.caption + " Forwarded from " + query.message.reply_to_message.from_user.name if group_msg.caption else "Forwarded from " + query.message.reply_to_message.from_user.name
                if group_msg.video: MEDIAS[group_msg.media_group_id].append(InputMediaVideo(group_msg.video, caption=caption))
                if group_msg.photo: MEDIAS[group_msg.media_group_id].append(InputMediaPhoto(group_msg.photo[0], caption=caption))
        else: fwd_msg = context.bot.forward_message(chat_id=CONFIG['Group_ID'], from_chat_id=query.message.chat_id, message_id=query.message.reply_to_message.message_id)
            
        root = DB[str(CONFIG['Group_ID']) + ':' + str(fwd_msg.message_id)] = {}
        root['Posted'] = False
        root['Sender_Name'] = query.message.reply_to_message.from_user.name
        root['Sender_ID'] = query.message.reply_to_message.from_user.id
        root['Original_MsgID'] = query.message.reply_to_message.message_id
        root['Media_Group_ID'] = query.message.reply_to_message.media_group_id
        root['Channel_ID'] = ""
        root['Type'] = cmds[1]

        msg = "新投稿\n投稿人：{0}\n来源：{1}".format(query.message.reply_to_message.from_user.name, post_type[cmds[1]]) 
        buttons = []
        for key in CONFIG['Publish_Channel'].keys():
            buttons.append(telegram.InlineKeyboardButton("采纳[" + CONFIG['Publish_Channel'][key] + "]", callback_data="contribute:receive:{0}:{1}".format(cmds[1], key)))
        markup = telegram.InlineKeyboardMarkup([buttons, [telegram.InlineKeyboardButton("审核不通过", callback_data='contribute:close')]])
        try:
            context.bot.send_message(chat_id=CONFIG['Group_ID'], text=msg, reply_to_message_id=fwd_msg.message_id, reply_markup=markup) 
        finally: 
            db.save("sub_data", DB, True)
        
