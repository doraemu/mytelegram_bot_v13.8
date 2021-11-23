USER_LOCK = []
PROCESS_LOCK = []


def user_lock(userid):
    if userid in USER_LOCK: return False
    else: 
        USER_LOCK.append(userid)
        return True

    
def user_unlock(userid): 
    if userid in USER_LOCK: USER_LOCK.remove(userid)


def user_check(userid): 
    return userid in USER_LOCK

      
def process_lock(pid):
    if pid in PROCESS_LOCK: return False
    else: 
        PROCESS_LOCK.append(pid)
        return True

    
def process_unlock(pid): 
    if pid in PROCESS_LOCK: PROCESS_LOCK.remove(pid)

    
def process_check(pid): 
    return pid in PROCESS_LOCK    
