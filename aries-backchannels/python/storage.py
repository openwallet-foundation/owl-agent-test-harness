import threading


storage = {}
storage_lock = threading.Lock()


def store_resource(data_id, data_type, data):
    storage_lock.acquire()
    try:
        if not data_id in storage:
            storage[data_id] = {}
        storage[data_id][data_type] = data
        return data
    finally:
        storage_lock.release()


def get_resource(data_id, data_type):
    storage_lock.acquire()
    try:
        if data_id in storage:
            if data_type in storage[data_id]:
                return storage[data_id][data_type]
        return None
    finally:
        storage_lock.release()


def get_resources(data_type):
    storage_lock.acquire()
    try:
        data_items = {}
        for data_id in storage:
            if data_type in storage[data_id]:
                data_items[data_id] = storage[data_id][data_type]
        return data_items
    finally:
        storage_lock.release()


def delete_resource(data_id, data_type):
    storage_lock.acquire()
    try:
        if data_id in storage:
            if data_type in storage[data_id]:
                stored_data = storage[data_id][data_type]
                del storage[data_id][data_type]
                return stored_data
        return None
    finally:
        storage_lock.release()


def push_resource(data_id, data_type, data):
    storage_lock.acquire()
    try:
        if not data_id in storage:
            storage[data_id] = {}
        if not data_type in storage[data_id]:
            storage[data_id][data_type] = []
        storage[data_id][data_type].append(data)
        return data
    finally:
        storage_lock.release()


def pop_resource(data_id, data_type):
    storage_lock.acquire()
    try:
        if data_id in storage:
            if data_type in storage[data_id]:
                if 0 < len(storage[data_id][data_type]):
                    data = storage[data_id][data_type][0]
                    del storage[data_id][data_type][0]
                    return data
        return None
    finally:
        storage_lock.release()

def pop_resource_latest(data_type):
    storage_lock.acquire()
    try:
        data_ids = list(storage.keys())
        data_id = data_ids[len(data_ids) - 1]
        if data_type in storage[data_id]:
            if 0 < len(storage[data_id][data_type]):
                if len(storage[data_id][data_type]) > 1:
                    data = storage[data_id][data_type][len(storage[data_id][data_type])-1]
                    del storage[data_id][data_type][len(storage[data_id][data_type])-1]
                else:
                    data = storage[data_id][data_type][0]
                    del storage[data_id][data_type][0]
                return data
        return None
    finally:
        storage_lock.release()