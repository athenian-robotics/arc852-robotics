import logging
import os
import sys
import time
from threading import Lock
from threading import Thread

import opencv_utils as utils
import requests
from flask import Flask
from flask import redirect
from flask import request
from werkzeug.wrappers import Response

http_host_default = "localhost:8080"
http_delay_secs_default = 0.5

path = os.path.abspath(sys.modules[__name__].__file__)
dir = os.path.dirname(path)
http_file_default = dir + "/html/image-reader.html"

logger = logging.getLogger(__name__)

class ImageServer(object):
    def __init__(self, camera_name, http_host, http_delay_secs, http_file):
        self.__camera_name = camera_name
        self.__http_host = http_host
        self.__http_delay_secs = http_delay_secs
        self.__http_file = http_file

        vals = self.__http_host.split(":")
        self.__host = vals[0]
        self.__port = vals[1] if len(vals) == 2 else 8080

        self.__current_image_lock = Lock()
        self.__current_image = None
        self.__launched = False
        self.__stopped = False
        self.__ready_to_stop = False

    @property
    def enabled(self):
        return len(self.__http_host) > 0

    @property
    def image(self):
        with self.__current_image_lock:
            if self.__current_image is None:
                return []
            retval, buf = utils.encode_image(self.__current_image)
            return buf.tobytes()

    @image.setter
    def image(self, image):
        if self.enabled:
            with self.__current_image_lock:
                self.__current_image = image

    def serve_images(self, width, height):
        if self.__launched or not self.enabled:
            return

        logger.info("Using template file {0}".format(self.__http_file))

        flask = Flask(__name__)

        @flask.route('/')
        def index():
            return redirect("/image?delay=.5")

        def get_page(delay):
            delay_secs = float(delay) if delay else self.__http_delay_secs
            try:
                with open(self.__http_file) as f:
                    html = f.read()

                name = self.__camera_name if self.__camera_name else "Unnamed"
                return html.replace("_TITLE_", name + " camera") \
                    .replace("_DELAY_SECS_", str(delay_secs)) \
                    .replace("_NAME_", name) \
                    .replace("_WIDTH_", str(width)) \
                    .replace("_HEIGHT_", str(height))
            except BaseException as e:
                logger.error("Unable to create template file with {0} [{1}]".format(self.__http_file, e), exc_info=True)
                time.sleep(1)

        @flask.route('/image')
        def image_option():
            return get_page(request.args.get("delay"))

        @flask.route("/image" + "/<string:delay>")
        def image_path(delay):
            return get_page(delay)

        @flask.route("/image.jpg")
        def image_jpg():
            response = Response(self.image, mimetype="image/jpeg")
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            return response

        @flask.route("/__shutdown__", methods=['POST'])
        def shutdown():
            if not self.__ready_to_stop:
                return "Not ready to stop"
            shutdown_func = request.environ.get('werkzeug.server.shutdown')
            if shutdown_func is not None:
                self.__stopped = True
                shutdown_func()
            return "Shutting down..."

        def run_http(flask_server, host, port):
            while not self.__stopped:
                try:
                    flask_server.run(host=host, port=port)
                except BaseException as e:
                    logger.error("Restarting HTTP server [{0}]".format(e), exc_info=True)
                    time.sleep(1)
                finally:
                    logger.info("HTTP server shutdown")

        # Run HTTP server in a thread
        Thread(target=run_http, kwargs={"flask_server": flask, "host": self.__host, "port": self.__port}).start()
        self.__launched = True
        logger.info("Started HTTP server listening on {0}:{1}".format(self.__host, self.__port))

    def stop(self):
        self.__ready_to_stop = True
        requests.post("http://{0}:{1}/__shutdown__".format(self.__host, self.__port))
