import telegram
import database as db
import lockmanage as lock
import time
from telegram import InputMediaVideo, InputMediaPhoto
from telegram.ext import CallbackContext

CONFIG = db.read("config")

MEDIAS = {}  # 暂存组图片或视频数据
media_group_id = 0
job = None


def forward_post(context: CallbackContext):
    args = context.job.context.split(":")
    for key in MEDIAS.keys():
        if len(MEDIAS[key]) > 1 and len(MEDIAS[key]) < 11: 
            try:
                context.bot.send_media_group(chat_id=args[0], media=MEDIAS[key])
            except telegram.error: 
                break
            else: 
                MEDIAS.pop(key)
                context.bot.send_message(args[1], text=str(key) + "已经发送，剩余：" + str(len(MEDIAS)))
                break
        else:  MEDIAS[key].pop(0)


def process_command(update, context):
    if update.message.from_user.id != CONFIG['Admin']: return
    
    global job, media_group_id
    command = update.message.text[1:].replace(CONFIG['Username'], '').lower()
    args = command.split("@")
    if args[0] == 'batchstart' and len(args) == 2:
        if lock.user_lock(update.message.from_user.id):
            media_group_id = (int(round(time.time() * 1000)))
            channel_id = '@' + args[1]
            chat_id = str(update.message.chat_id)
            job = context.job_queue.run_repeating(forward_post, 20, context=channel_id + ':' + chat_id, name = chat_id)
            update.message.reply_text(text="已开启批量转发至" + channel_id)
        else: update.message.reply_text(text="批量转发开启失败") 
        return
    if args[0] == 'batchstop' :
        if job: job.schedule_removal()
        lock.user_unlock(update.message.from_user.id) 
        update.message.reply_text(text="已关闭批量转发")
        return


def process_msg(update, context):
    if not update.message.video and not update.message.photo: return  # 只接收图片和视频投稿
    
    global  media_group_id    
    if media_group_id:  # 用于一组图片和视频转发
        caption = None
        if media_group_id not in MEDIAS.keys(): 
            MEDIAS[media_group_id] = []
            caption = "✨转发到三个群截图私聊 " + CONFIG["Username"] + " 观看全集完整版"
        if len(MEDIAS[media_group_id]) < 10: 
            if update.message.video: MEDIAS[media_group_id].append(InputMediaVideo(update.message.video, caption=caption))
            if update.message.photo: MEDIAS[media_group_id].append(InputMediaPhoto(media=update.message.photo[len(update.message.photo) - 1], caption=caption))
        else: media_group_id = (int(round(time.time() * 1000)))

          
def process_callback(update, context):
    return 
            
