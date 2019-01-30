import logging
import time
from multiprocessing import Manager
from multiprocessing import Process
from threading import Lock
from threading import Thread

import requests
from flask import Flask
from flask import redirect
from flask import request
from werkzeug.wrappers import Response

import arc852.cli_args  as cli
from arc852.constants import CAMERA_NAME_DEFAULT
from arc852.constants import HTTP_HOST_DEFAULT, HTTP_DELAY_SECS_DEFAULT, HTTP_PORT_DEFAULT
from arc852.opencv_utils import encode_image

logger = logging.getLogger(__name__)

_image_endpoint_url = "/image.jpg"


class ProcessImageServer(object):
    args = [cli.template_file, cli.http_port, cli.http_delay_secs, cli.http_verbose]

    def __init__(self,
                 template_file,
                 camera_name=CAMERA_NAME_DEFAULT,
                 http_host=HTTP_HOST_DEFAULT,
                 http_delay_secs=HTTP_DELAY_SECS_DEFAULT,
                 http_verbose=False,
                 log_info=logger.info,
                 log_debug=logger.debug,
                 log_error=logger.error):
        self.__template_file = template_file
        self.__manager = Manager()
        self.__queue = self.__manager.Queue()
        self.__camera_name = camera_name
        self.__http_host = http_host
        self.__http_delay_secs = http_delay_secs
        self.__log_info = log_info
        self.__log_debug = log_debug
        self.__log_error = log_error

        vals = self.__http_host.split(":")
        self.__host = vals[0]
        self.__port = vals[1] if len(vals) == 2 else HTTP_PORT_DEFAULT

        self.__current_image_lock = Lock()
        self.__current_image = None
        self.__ready_to_stop = False
        self.__flask_launched = False
        self.__ready_to_serve = False
        self.__started = False
        self.__stopped = False

        if not http_verbose:
            class FlaskFilter(logging.Filter):
                def __init__(self, fname):
                    super(FlaskFilter, self).__init__()
                    self.__fname = "GET {0}".format(fname)

                def filter(self, record):
                    return self.__fname not in record.msg

            logging.getLogger('werkzeug').addFilter(FlaskFilter(_image_endpoint_url))

    @property
    def image(self):
        with self.__current_image_lock:
            if self.__current_image is None:
                return []

            return self.__current_image

    @image.setter
    def image(self, image):
        # Wait until potential sleep in start() has completed
        if not self.__ready_to_serve:
            return

        if not self.__started:
            self.__log_error("ImageServer.start() not called")
            return

        # Put image on queue for other process to serve up
        self.__queue.put(image)

    def __set_image(self, image):
        if not self.__flask_launched:
            height, width = image.shape[:2]
            self.__launch_flask(width, height)

        with self.__current_image_lock:
            # Encode to bytes if passed in as an nparray
            if isinstance(image, bytes):
                self.__current_image = image
            else:
                retval, buf = encode_image(image)
                self.__current_image = buf.tobytes()

    def __launch_flask(self, width, height):

        flask = Flask(__name__)

        @flask.route('/')
        def index():
            return redirect("/image?delay={0}".format(self.__http_delay_secs))

        @flask.route('/image')
        def image_option():
            return get_page(request.args.get("delay"))

        @flask.route("/image" + "/<string:delay>")
        def image_path(delay):
            return get_page(delay)

        @flask.route(_image_endpoint_url)
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
            if shutdown_func:
                self.__stopped = True
                shutdown_func()
            return "Shutting down..."

        def get_page(delay):
            delay_secs = float(delay) if delay else self.__http_delay_secs
            try:
                with open(self.__template_file) as f:
                    html = f.read()

                name = self.__camera_name
                return html.replace("_TITLE_", name + " camera") \
                    .replace("_DELAY_SECS_", str(delay_secs)) \
                    .replace("_NAME_", name) \
                    .replace("_WIDTH_", str(width)) \
                    .replace("_HEIGHT_", str(height)) \
                    .replace("_IMAGE_FNAME_", _image_endpoint_url)
            except BaseException as e:
                self.__log_error("Unable to create template file with %s [%s]", self.__template_file, e, exc_info=True)
                time.sleep(1)

        def run_http(flask_server, host, port):
            while not self.__stopped:
                try:
                    self.__log_info("Starting server with {0}:{1}".format(host, port))
                    flask_server.run(host=host, port=int(port))
                except BaseException as e:
                    self.__log_error("Restarting HTTP server [%s]", e, exc_info=True)
                    time.sleep(1)
                finally:
                    self.__log_info("HTTP server shutdown")

        # Run HTTP server in a thread
        Thread(target=run_http, kwargs={"flask_server": flask, "host": self.__host, "port": self.__port}).start()

        self.__flask_launched = True
        self.__log_info("Running HTTP server on http://%s:%s/", self.__host, self.__port)

    def start(self):
        if self.__started:
            self.__log_error("ImageServer.start() already called")
            return

        if self.__flask_launched:
            return

        # Cannot start the flask server until the dimensions of the image are known
        # So do not fire up the thread until the first image is available
        self.__log_info("Starting ImageServer")
        self.__log_info("Using template file %s", self.__template_file)
        self.__log_info("Starting HTTP server on http://%s:%s/", self.__host, self.__port)

        self.__ready_to_serve = True
        self.__started = True

        def read_queue():
            # Read images from queue
            while not self.__ready_to_stop:
                self.__set_image(self.__queue.get())

        Process(target=read_queue).start()

    def stop(self):
        if not self.__flask_launched:
            return

        self.__ready_to_stop = True
        url = "http://{0}:{1}".format(self.__host, self.__port)
        self.__log_info("Shutting down %s", url)

        try:
            requests.post("{0}/__shutdown__".format(url))
        except requests.exceptions.ConnectionError:
            self.__log_error("Unable to stop ImageServer")
