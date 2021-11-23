import time
import json
import os
import threading

PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

DB_LOCK = []
    
def save_file(dbname, data):
    f = open(PATH + dbname + '.json', 'w', encoding='utf-8')
    f.write(json.dumps(data, ensure_ascii=False))
    f.close()
    
def save_lock(dbname, data):
    global DB_LOCK
    while dbname in DB_LOCK: time.sleep(0.05)
    DB_LOCK.append(dbname)
    save_file(dbname, data)
    DB_LOCK.remove(dbname)
    
def save(dbname, data, lock=False):
    if lock: threading.Thread(target=save_lock(dbname, data)).start()
    else: save_file(dbname, data)
    
def read(dbname):
    data = json.loads(open(PATH + dbname + '.json', 'r', encoding='utf-8').read())
    return data