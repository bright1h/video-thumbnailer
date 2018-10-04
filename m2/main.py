import os
import json
import redis
from flask import Flask, jsonify, render_template, send_from_directory, request
import requests

app = Flask(__name__)

BASE_URL = "http://webapp:8080"
# BASE_URL = "http://localhost:8080"
DIR = os.getcwd() + "/tmp/"

WEBSITE_BASE_URL = "http://localhost:5000"


class RedisResource:
    REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
    QUEUE_NAME = 'queue:thumbnail'

    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    conn = redis.Redis(host=host, *port)


# Prevent Error Message
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/<bucket>/<object>', methods=['POST'])
def post_object(bucket, object):
    RedisResource.conn.rpush(
        RedisResource.QUEUE_NAME,
        json.dumps({
            'bucket': bucket,
            'fname': object,
        }))

    return render_template("action_performed.html",
                           msg="You submit job to the queue",
                           url="{}/{}/show_all_video".format(WEBSITE_BASE_URL, bucket))


@app.route('/<bucket>/<object>/delete', methods=['POST'])
def send_delete_object_request(bucket, object):
    url = "{}/{}/{}?delete".format(BASE_URL, bucket, object)
    r = requests.delete(url)
    msg = "You successfully deleted the file"
    if r.status_code != 200:
        msg = "You successfully deleted the file"
    return render_template("action_performed.html",
                           msg=msg,
                           url="{}/{}/show_all_gif".format(WEBSITE_BASE_URL, bucket))


@app.route('/<bucket>', methods=['POST'])
def post_all_vid(bucket):
    url = "{}/{}?list".format(BASE_URL, bucket)
    r_bucket = requests.get(url)
    if r_bucket.status_code == 200:
        json_res = r_bucket.json()
        objects = json_res['objects']
        vids = [obj['name'] for obj in objects if obj['name'].split('.')[-1] in ("mp4", "avi", "mov")]
        for vid_name in vids:
            RedisResource.conn.rpush(
                RedisResource.QUEUE_NAME,
                json.dumps({
                    'bucket': bucket,
                    'fname': vid_name,
                }))

    return render_template("action_performed.html",
                           msg="You submitted jobs to the queue",
                           url="{}".format(WEBSITE_BASE_URL))


@app.route('/<bucket>', methods=['GET'])
def get_gif_images(bucket):
    url = "{}/{}?list".format(BASE_URL, bucket)
    r = requests.get(url)
    if r.status_code == 200:
        json_res = r.json()
        objects = json_res['objects']
        gif_images = [obj['name'] for obj in objects if ".gif" in obj['name']]
        return jsonify({"gif_images": gif_images})

    return render_template("action_performed.html",
                           msg="Unexpected Error Occurred",
                           url="{}".format(WEBSITE_BASE_URL))


@app.route('/<bucket>/show_all_video', methods=['GET'])
def show_all_vid(bucket):
    url = "{}/{}?list".format(BASE_URL, bucket)
    r = requests.get(url)
    if r.status_code == 200:
        json_res = r.json()
        objects = json_res['objects']
        all_vids = [obj['name'] for obj in objects if obj['name'].split('.')[-1] in ("mp4", "avi", "mov")]
        return render_template("show_all_videos.html", videos=all_vids, bucket=bucket)

    return render_template("action_performed.html",
                           msg="Unexpected Error Occurred",
                           url="{}".format(WEBSITE_BASE_URL))


@app.route('/<bucket>/show_all_gif', methods=['GET'])
def show_all_gif(bucket):
    url = "{}/{}?list".format(BASE_URL, bucket)
    r = requests.get(url)
    if r.status_code == 200:
        json_res = r.json()
        objects = json_res['objects']
        all_gif = [obj['name'] for obj in objects if ".gif" in obj['name']]

        return render_template("show_all_gif.html", gifs=all_gif, bucket=bucket)

    return render_template("action_performed.html",
                           msg="Unexpected Error Occurred",
                           url="{}/{}/show_all_video".format(WEBSITE_BASE_URL, bucket))


@app.route('/<bucket>/show_all_gif/delete', methods=['POST'])
def delete_all_gif(bucket):
    gif_list = list(request.values)
    msg = "You successfully deleted the files"
    for gif in gif_list:
        url = "{}/{}/{}?delete".format(BASE_URL, bucket, gif)
        r = requests.delete(url)
        if r.status_code != 200:
            msg = "Unexpected Error Occurred"
    return render_template("action_performed.html",
                           msg=msg,
                           url="{}/{}/show_all_gif".format(WEBSITE_BASE_URL, bucket))


@app.route('/', methods=['GET'])
def show_buckets():
    url = "{}/buckets".format(BASE_URL)
    r = requests.get(url)
    if r.status_code == 200:
        json_res = r.json()
        return render_template("show_all_buckets.html", buckets=json_res)

    return render_template("action_performed.html",
                           msg="Unexpected Error Occurred",
                           url="{}".format(WEBSITE_BASE_URL))


if __name__ == '__main__':
    app.run()
