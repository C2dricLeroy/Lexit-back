from redis import Redis
from rq import Queue, Worker

redis_conn = Redis(host="redis", port=6379)
email_queue = Queue("emails", connection=redis_conn)

if __name__ == "__main__":
    worker = Worker([email_queue], connection=redis_conn)
    worker.work()
