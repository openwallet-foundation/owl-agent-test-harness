import threading


storage = {}
storage_lock = threading.Lock()


def store_resource(data_id, data_type, data):
    storage_lock.acquire()
    try:
        storage[data_id] = {"data_type": data_type, "data": data}
        return data
    finally:
        storage_lock.release()


def get_resource(data_id, data_type):
    storage_lock.acquire()
    try:
        if data_id in storage:
            stored_data = storage[data_id]
            if stored_data["data_type"] == data_type:
                return stored_data["data"]
            else:
                return None
        else:
            return None
    finally:
        storage_lock.release()


def delete_resource(data_id, data_type):
    storage_lock.acquire()
    try:
        if data_id in storage:
            stored_data = storage[data_id]
            if stored_data["data_type"] == data_type:
                del storage[data_id]
                return stored_data["data"]
            else:
                return None
        else:
            return None
    finally:
        storage_lock.release()

