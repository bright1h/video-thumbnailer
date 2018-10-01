#!/usr/bin/env python3

from moviepy.editor import VideoFileClip
import logging
import json
import uuid
import redis
import os
import requests

# Worker
LOG = logging
REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
QUEUE_NAME = 'queue:thumbnail'
INSTANCE_NAME = uuid.uuid4().hex

LOG.basicConfig(
    level=LOG.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def watch_queue(redis_conn, queue_name, callback_func, timeout=30):
    """
    Listen to Redis
    """
    active = True

    while active:
        # Fetch a json-encoded task using a blocking (left) pop
        # queue_name implied keys in the list
        packed = redis_conn.blpop([queue_name], timeout=timeout)

        if not packed:
            # if nothing is returned, poll a again
            continue

        _, packed_task = packed

        # If it's treated to a poison pill, quit the loop
        if packed_task == b'DIE':
            active = False
        else:
            task = None
            try:
                task = json.loads(packed_task)
            except Exception:
                LOG.exception('json.loads failed')
            if task:
                callback_func(task)


def upload_gif(log, bucket, path, uploaded_file):
    log.info("Upload %s", uploaded_file)
    r_create = requests.post("http://localhost:8080/" + bucket + '/' + uploaded_file + "?create")
    if r_create.status_code != 200:
        log.info("Fail to create ticket, status : %d", r_create.status_code)
        return

    files = {'file': open(path+uploaded_file, 'rb')}
    r_upload = requests.put("http://localhost:8080/" + bucket + '/' + uploaded_file + "?partNumber=1", files=files)
    if r_upload != 200:
        log.info("Fail to upload a file, status : %d", r_upload.status_code)
        return
    r_complete = requests.post("http://localhost:8080/" + bucket + '/' + uploaded_file + "?complete")

    if r_complete != 200:
        log.info("Fail to complete the uploaded object, status : %d", r_complete.status_code)
        return

    log.info("Done, %s is uploaded, status : 200", uploaded_file)
    return r_create.status_code


def make_gif(log, task):
    """
    Convert the video file to the gif image
    """
    path = task.get('path')
    bucket = task.get('bucket')
    fname = task.get('fname')
    output = fname.replace('.mp4', '.gif')
    print(path, bucket, fname, output)
    log.info('Convert %s to GIF image', fname)
    vid = VideoFileClip(path+fname)
    duration = vid.duration
    start = duration * 2 / 3
    if duration < 5:
        start = duration
    if duration - start < 5:
        start = duration - 5

    clip = vid.subclip(start, start + 5).resize((320, 240))
    clip.write_gif(path+output, fps=10)
    log.info("Done, %s", output)
    upload_gif(log, bucket, path, output)


def execute_factor(log, task):
    number = task.get('number')
    if number:
        number = int(number)
        log.info('Factoring %d', number)
        factors = [trial for trial in range(1, number + 1) if number % trial == 0]
        log.info('Done, factors = %s', factors)
    else:
        log.info('No number given.')


def main():
    LOG.info('Starting a worker...')
    LOG.info('Unique name: %s', INSTANCE_NAME)
    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    named_logging = LOG.getLogger(name=INSTANCE_NAME)
    named_logging.info('Trying to connect to %s [%s]', host, REDIS_QUEUE_LOCATION)
    redis_conn = redis.Redis(host=host, *port)
    watch_queue(
        redis_conn,
        QUEUE_NAME,
        lambda task_descr: make_gif(named_logging, task_descr))


if __name__ == '__main__':
    main()
