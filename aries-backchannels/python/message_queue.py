import threading, asyncio

message_queues = {}
mq_lock = threading.Lock()


def _get_queue(message_type):
    if message_type in message_queues:
        return message_queues[message_type]
    else:
        try:
            mq_lock.acquire()
            if message_type in message_queues:
                return message_queues[message_type]
            else:
                selected_queue = asyncio.Queue()
                message_queues[message_type] = selected_queue
                return selected_queue
        finally:
            mq_lock.release()


async def pop_message_queue(message_type, timeout=0):
    print(f"calling message_queue.pop_message_queue({message_type}, {timeout})")
    if timeout <= 0:
        timeout = None

    selected_queue = _get_queue(message_type)

    res = await asyncio.wait_for(
        asyncio.shield(message_queues[message_type].get()), timeout
    )
    print(
        f"finished message_queue.pop_message_queue({message_type}, {timeout}) -> {res}"
    )
    return res


async def push_message_queue(message_type, value, timeout=0):
    print(
        f"calling message_queue.push_message_queue({message_type}, {value}, {timeout})"
    )
    if timeout <= 0:
        timeout = None

    selected_queue = _get_queue(message_type)

    await asyncio.wait_for(asyncio.shield(selected_queue.put(value)), timeout)
    print(
        f"finished message_queue.push_message_queue({message_type}, {value}, {timeout})"
    )


async def clear_all():
    try:
        mq_lock.acquire()
        message_queues = {}
    finally:
        mq_lock.release()


message_stacks = {}
ms_lock = threading.Lock()


def _get_stack(message_type):
    if message_type in message_stacks:
        return message_stacks[message_type]
    else:
        try:
            ms_lock.acquire()
            if message_type in message_stacks:
                return message_stacks[message_type]
            else:
                selected_stack = asyncio.LifoQueue()
                message_stacks[message_type] = selected_stack
                return selected_stack
        finally:
            ms_lock.release()


async def pop_message_stack(message_type, timeout=0):
    print(f"calling message_stack.pop_message({message_type}, {timeout})")
    if timeout <= 0:
        timeout = None

    selected_stack = _get_stack(message_type)

    res = await asyncio.wait_for(
        asyncio.shield(message_stacks[message_type].get()), timeout
    )
    print(f"finished message_stack.pop_message({message_type}, {timeout}) -> {res}")
    return res


async def push_message_stack(message_type, value, timeout=0):
    print(f"calling message_stack.push_message({message_type}, {value}, {timeout})")
    if timeout <= 0:
        timeout = None

    selected_stack = _get_stack(message_type)

    await asyncio.wait_for(asyncio.shield(selected_stack.put(value)), timeout)
    print(f"finished message_stack.push_message({message_type}, {value}, {timeout})")


async def clear_all_stacks():
    try:
        ms_lock.acquire()
        message_stacks = {}
    finally:
        ms_lock.release()
