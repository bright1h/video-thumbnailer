import os
import json
import redis
from flask import Flask, jsonify
import requests

app = Flask(__name__)

BASE_URL = "http://webapp:8080"
# BASE_URL = "http://localhost:8080"

DIR = os.getcwd()+"/tmp/"


class RedisResource:
    REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
    QUEUE_NAME = 'queue:thumbnail'

    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    conn = redis.Redis(host=host, *port)


@app.route('/<bucket>/<object>', methods=['POST'])
def post_object(bucket, object):
    # status = download_file_and_post_to_queue(bucket, object)
    RedisResource.conn.rpush(
        RedisResource.QUEUE_NAME,
        json.dumps({
            'bucket': bucket,
            'fname': object,
        }))

    return jsonify({"status": 200})


@app.route('/<bucket>', methods=['POST'])
def post_all_vid(bucket):
    url = "{}/{}?list".format(BASE_URL,bucket)
    r_bucket = requests.get(url)
    if r_bucket.status_code == 200:
        json_res = r_bucket.json()
        objects = json_res['objects']
        vids = [obj['name'] for obj in objects if ".mp4" in obj['name']]
        for vid_name in vids:
            RedisResource.conn.rpush(
                RedisResource.QUEUE_NAME,
                json.dumps({
                    'bucket': bucket,
                    'fname': vid_name,
                }))
            # status = download_file_and_post_to_queue(bucket, vid_name)
            # if status != 200: return jsonify({"status": status})

    return jsonify({"status": r_bucket.status_code})


@app.route('/<bucket>', methods=['GET'])
def get_gif_images(bucket):
    url = "{}/{}?list".format(BASE_URL,bucket)
    r = requests.get(url)
    if r.status_code == 200:
        json_res = r.json()
        objects = json_res['objects']
        gif_images = [obj['name'] for obj in objects if ".gif" in obj['name']]
        return jsonify({"gif_images": gif_images})

    return jsonify({"status": r.status_code})


if __name__ == '__main__':
    app.run()
