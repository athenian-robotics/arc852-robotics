import logging
import time
from threading import Lock
from threading import Thread

import requests
from flask import Flask
from flask import redirect
from flask import request
from werkzeug.wrappers import Response

import arc852.cli_args  as cli
from arc852.constants import HTTP_DELAY_SECS_DEFAULT, HTTP_PORT_DEFAULT, IMAGE_X_DEFAULT, IMAGE_Y_DEFAULT

# Find where this package is installed
_image_fname = "/image.jpg"

logger = logging.getLogger(__name__)


class ImageServer(object):
    args = [cli.template_file, cli.http_port, cli.http_delay_secs, cli.image_x, cli.image_y, cli.http_verbose]

    def __init__(self,
                 template_file,
                 camera_name="",
                 image_x=IMAGE_X_DEFAULT,
                 image_y=IMAGE_Y_DEFAULT,
                 http_port=HTTP_PORT_DEFAULT,
                 http_delay_secs=HTTP_DELAY_SECS_DEFAULT,
                 http_verbose=False,
                 log_info=logger.info,
                 log_debug=logger.debug,
                 log_error=logger.error):
        self.__template_file = template_file
        self.__image_x = image_x
        self.__image_y = image_y
        self.__camera_name = camera_name
        self.__http_port = http_port
        self.__http_delay_secs = http_delay_secs
        self.__log_info = log_info
        self.__log_debug = log_debug
        self.__log_error = log_error

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

            logging.getLogger('werkzeug').addFilter(FlaskFilter(_image_fname))

    @property
    def image(self):
        with self.__current_image_lock:
            if self.__current_image is None:
                return []
            # retval, buf = utils.encode_image(self.__current_image)
            return self.__current_image

    @image.setter
    def image(self, image):
        # Wait until potential sleep in start() has completed
        if not self.__ready_to_serve:
            return

        if not self.__started:
            self.__log_error("ImageServer.start() not called")
            return

        with self.__current_image_lock:
            self.__current_image = image

    def start(self):
        if self.__started:
            self.__log_error("ImageServer.start() already called")
        else:
            self.__log_info("Starting ImageServer")
            Thread(target=self.__start).start()

    def stop(self):
        if not self.__flask_launched:
            return

        self.__ready_to_stop = True
        url = "http://localhost:{0}".format(self.__http_port)
        self.__log_info("Shutting down %s", url)

        try:
            requests.post("{0}/__shutdown__".format(url))
        except requests.exceptions.ConnectionError:
            self.__log_error("Unable to stop ImageServer")

    def __start(self):
        self.__log_info("Using template file %s", self.__template_file)
        self.__log_info("Starting HTTP server listening on port %d", self.__http_port)
        self.__ready_to_serve = True
        self.__started = True

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

        @flask.route(_image_fname)
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

                return html.replace("_TITLE_", "") \
                    .replace("_DELAY_SECS_", str(delay_secs)) \
                    .replace("_NAME_", self.__camera_name) \
                    .replace("_WIDTH_", str(self.__image_x)) \
                    .replace("_HEIGHT_", str(self.__image_y)) \
                    .replace("_IMAGE_FNAME_", _image_fname)
            except BaseException as e:
                self.__log_error("Unable to create template file with %s [%s]", self.__template_file, e, exc_info=True)
                time.sleep(1)

        def run_http(flask_server, host, port):
            while not self.__stopped:
                try:
                    flask_server.run(host=host, port=int(port))
                except BaseException as e:
                    self.__log_error("Restarting HTTP server [%s]", e, exc_info=True)
                    time.sleep(1)
                finally:
                    self.__log_info("HTTP server shutdown")

        # Run HTTP server in a thread
        Thread(target=run_http, kwargs={"flask_server": flask, "host": "0.0.0.0", "port": self.__http_port}).start()
        self.__flask_launched = True
        self.__log_info("Running HTTP server listening on port %d", self.__http_port)

