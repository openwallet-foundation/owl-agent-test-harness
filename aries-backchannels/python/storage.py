import threading


storage = {}
storage_lock = threading.Lock()

# data_id is the thread_id (at least as used by aca-py)
# the exchange_id is specific to the protocol (e.g. cred or proof exchange)
data_to_exch_id = {}
exch_to_data_id = {}


def data_exch_mapping_name(data_type, exch_id_name):
    return data_type + "." + exch_id_name


def add_data_exch_mapping(data_id, data_type, data, exch_id_name):
    if exch_id_name and exch_id_name in data:
        exch_id = data[exch_id_name]
    else:
        return
    mapping_name = data_exch_mapping_name(data_type, exch_id_name)
    if not mapping_name in data_to_exch_id:
        data_to_exch_id[mapping_name] = {}
    data_to_exch_id[mapping_name][data_id] = exch_id
    if not mapping_name in exch_to_data_id:
        exch_to_data_id[mapping_name] = {}
    exch_to_data_id[mapping_name][exch_id] = data_id


def get_data_id_from_exch_id(data_type, exch_id_name, exch_id):
    mapping_name = data_exch_mapping_name(data_type, exch_id_name)
    if mapping_name in exch_to_data_id:
        return exch_to_data_id[mapping_name][exch_id]
    return None


def get_exch_id_from_data_id(data_type, exch_id_name, data_id):
    mapping_name = data_exch_mapping_name(data_type, exch_id_name)
    if mapping_name in data_to_exch_id:
        return data_to_exch_id[mapping_name][data_id]
    return None


def store_resource(data_id, data_type, data, exch_id_name=None):
    storage_lock.acquire()
    try:
        if data_id not in storage:
            storage[data_id] = {}
        storage[data_id][data_type] = data
        add_data_exch_mapping(data_id, data_type, data, exch_id_name)
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


def get_resource_latest(data_type):
    storage_lock.acquire()
    try:
        data_ids = list(storage.keys())
        data_id = data_ids[-1]
        # data_type_keys = list(storage[data_id].keys())
        # data_type = data_type_keys[-1]
        data = storage[data_id][data_type][-1]
        return data
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


def push_resource(data_id, data_type, data, exch_id_name=None):
    storage_lock.acquire()
    try:
        if data_id not in storage:
            storage[data_id] = {}
        if data_type not in storage[data_id]:
            storage[data_id][data_type] = []
        storage[data_id][data_type].append(data)
        add_data_exch_mapping(data_id, data_type, data, exch_id_name)
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
                    data = storage[data_id][data_type][-1]
                    del storage[data_id][data_type][-1]
                else:
                    data = storage[data_id][data_type][0]
                    del storage[data_id][data_type][0]
                return data
        return None
    finally:
        storage_lock.release()
