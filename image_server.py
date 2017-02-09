import logging
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

logger = logging.getLogger(__name__)

IMAGE_FNAME = "/image.jpg"


class ImageServer(object):
    def __init__(self, camera_name, http_host, http_delay_secs, http_file, verbose=False):
        self.__camera_name = camera_name
        self.__http_host = http_host
        self.__http_delay_secs = http_delay_secs
        self.__http_file = http_file

        vals = self.__http_host.split(":")
        self.__host = vals[0]
        self.__port = vals[1] if len(vals) == 2 else 8080

        self.__current_image_lock = Lock()
        self.__current_image = None
        self.__ready_to_stop = False
        self.__flask_launched = False
        self.started = False
        self.stopped = False

        if not verbose:
            class FlaskFilter(logging.Filter):
                def __init__(self, fname):
                    super(FlaskFilter, self).__init__()
                    self.__fname = "GET {0}".format(fname)

                def filter(self, record):
                    return self.__fname not in record.msg

            logging.getLogger('werkzeug').addFilter(FlaskFilter(IMAGE_FNAME))

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
        if not self.enabled:
            return

        if not self.started:
            logger.error("ImageServer.start() not called")
            return

        if not self.__flask_launched:
            self._launch_flask(image)

        with self.__current_image_lock:
            self.__current_image = image

    def _launch_flask(self, image):
        flask = Flask(__name__)
        height, width = image.shape[:2]

        @flask.route('/')
        def index():
            return redirect("/image?delay=.5")

        @flask.route('/image')
        def image_option():
            return get_page(request.args.get("delay"))

        @flask.route("/image" + "/<string:delay>")
        def image_path(delay):
            return get_page(delay)

        @flask.route(IMAGE_FNAME)
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
                self.stopped = True
                shutdown_func()
            return "Shutting down..."

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
                    .replace("_HEIGHT_", str(height)) \
                    .replace("_IMAGE_FNAME_", IMAGE_FNAME)
            except BaseException as e:
                logger.error("Unable to create template file with {0} [{1}]".format(self.__http_file, e), exc_info=True)
                time.sleep(1)

        def run_http(flask_server, host, port):
            while not self.stopped:
                try:
                    flask_server.run(host=host, port=port)
                except BaseException as e:
                    logger.error("Restarting HTTP server [{0}]".format(e), exc_info=True)
                    time.sleep(1)
                finally:
                    logger.info("HTTP server shutdown")

        # Run HTTP server in a thread
        Thread(target=run_http, kwargs={"flask_server": flask, "host": self.__host, "port": self.__port}).start()
        self.__flask_launched = True
        logger.info("Running HTTP server on http://{0}:{1}/".format(self.__host, self.__port))

    def start(self):
        # We cannot start the flask server until we know the dimensions of the image
        # So we do not fire up the thread until the first image is available
        if self.__flask_launched or not self.enabled:
            return

        if self.started:
            logger.error("ImageServer.start() already called")
            return

        logger.info("Using template file {0}".format(self.__http_file))
        logger.info("Starting HTTP server on http://{0}:{1}/".format(self.__host, self.__port))
        self.started = True

    def stop(self):
        self.__ready_to_stop = True
        url = "http://{0}:{1}".format(self.__host, self.__port)
        logger.info("Shutting down {0}".format(url))
        requests.post("{0}/__shutdown__".format(url))
