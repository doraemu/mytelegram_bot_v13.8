# mytelegram_bot_v13.8
Python Telegram bot for Telegram API 13.8.1

安装  
pip install python-telegram-bot  
pip install requests  

修改配置文件  
{  
	"Admin": 0,     #管理员ID  
	"Token": "",    #机器人Token  
	"ID": 0,        #机器人ID 启动后会自动填加  
	"Username": "", #机器人用户名 启动后会自动填加  
	"Modules": {  
		"batchforward": "批量转发模块",  
		"contribute": "投稿模块",  
		"aichat": "AI聊天模块"  
	}  
}  

基本功能：  
1.投稿：可接收的投稿类型：图片、视频，支持多频道转发。  
  命令：  
  /setsubgroup                        #设定审稿群组，group里的用户都可以审稿  
  /setsubchannel @channel 简单描述    #设定接收频道，可以填加多个，审稿时可以选择采纳到指定频道  
         
2.批量转发：可以转发别的群里的图片、视频内容到指定群，不保留原标题内容  
  命令：  
  /batchstart@channel  #设定转发到指定频道  
  /batchstop           #停止转发  
  
3.AI聊天：可接收群组@消息和单独消息，通过调用AI聊天API返回聊天内容。  
