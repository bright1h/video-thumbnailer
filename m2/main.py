import os
import json
import redis
from flask import Flask, jsonify
import requests

app = Flask(__name__)

DIR = "./tmp/"


class RedisResource:
    REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
    QUEUE_NAME = 'queue:thumbnail'

    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    conn = redis.Redis(host=host, *port)


def download_file_and_post_to_queue(bucket, object):
    url = "http://localhost:8080/{}/{}".format(bucket, object)
    r = requests.get(url, allow_redirects=True)
    print(r.status_code)
    if r.status_code == 200:
        path = DIR + bucket + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        open(path + object, 'wb').write(r.content)
        RedisResource.conn.rpush(
            RedisResource.QUEUE_NAME,
            json.dumps({
                'path': path,
                'bucket': bucket,
                'fname': object,
            }))
        return 200
    return r.status_code


@app.route('/<bucket>/<object>', methods=['POST'])
def post_object(bucket, object):
    status = download_file_and_post_to_queue(bucket, object)
    return jsonify({"status": status})


@app.route('/<bucket>', methods=['POST'])
def post_all_object(bucket):
    url = "http://localhost:8080/{}?list".format(bucket)
    r_bucket = requests.get(url)
    if r_bucket.status_code == 200:
        json_res = r_bucket.json()
        objects = json_res['objects']
        vids = [obj['name'] for obj in objects if ".mp4" in obj['name']]
        for vid_name in vids:
            status = download_file_and_post_to_queue(bucket, vid_name)
            if status != 200: return jsonify({"status": status})

    return jsonify({"status": r_bucket.status_code})


@app.route('/<bucket>', methods=['GET'])
def get_gifs(bucket):
    url = "http://localhost:8080/{}?list".format(bucket)
    r = requests.get(url)
    if r.status_code == 200:
        json_res = r.json()
        objects = json_res['objects']
        gif_images = [obj['name'] for obj in objects if ".gif" in obj['name']]
        return jsonify({"gif_images": gif_images})

    return jsonify({"status": r.status_code})


if __name__ == '__main__':
    app.run()
