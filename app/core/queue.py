from redis import Redis
from rq import Queue, Retry

from app.tasks.email import send_email

redis_conn = Redis(host="redis", port=6379)
emails_queue = Queue("emails", connection=redis_conn)


def enqueue_email():
    """Enqueue an email"""
    job = emails_queue.enqueue(
        send_email,
        "cedricleroy28@gmail.com",
        "Hello",
        "This is the body",
        retry=Retry(max=5, interval=[10, 30, 60, 120]),
    )
    return {"job_id": job.get_id()}
