import os
from contextlib import contextmanager
from redlock import Redlock


@contextmanager
def worker_lock_manager(key, ttl, **kwargs):
    """
    Distributed lock
    :param key: Distributed lockID
    :param ttl: Distributed lock生存时间
    : param kwargs: optional parameter dictionary
    :return: None
    """
    redis_servers = [{
        'host': f'{os.environ.get("REDIS_IP")}',
        'port': f'{os.environ.get("REDIS_PORT")}',

    }]

    rlk = Redlock(redis_servers)

    # Get lock
    lock = rlk.lock(key, ttl)

    yield lock

    # Release the lock
    rlk.unlock(lock)
