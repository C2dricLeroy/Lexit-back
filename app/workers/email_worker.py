from redis import Redis
from rq import Queue, Worker

from app.tasks.email import send_email

redis_conn = Redis(host="redis", port=6379)
queue = Queue("emails", connection=redis_conn)

if __name__ == "__main__":
    worker = Worker(queues=["emails"], connection=redis_conn)
    worker.work()
