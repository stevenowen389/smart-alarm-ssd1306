import sys
import os.path
import logging
from email.parser import BytesParser
from email.policy import default
from urllib.parse import parse_qsl

# Apache configuration variables do not automatically become process variables.
project_path = os.environ.get('smart_alarm_path', os.path.dirname(os.path.abspath(__file__)))
if project_path not in sys.path:
    sys.path.append(project_path)
os.chdir(project_path)

from modules.xml_data import Xml_data


logger = logging.getLogger(__name__)


xml_data = Xml_data(str(project_path) + '/data.xml')

MIME_TABLE = {'.txt': 'text/plain',
              '.html': 'text/html',
              '.css': 'text/css',
              '.xml': 'text/xml',
              '.js': 'application/javascript',
              '.png': 'image/png'}


def parse_post(environ):
    """Return submitted fields and an optional uploaded file."""
    content_length = int(environ.get('CONTENT_LENGTH') or 0)
    body = environ['wsgi.input'].read(content_length)
    content_type = environ.get('CONTENT_TYPE', '')

    if content_type.startswith('multipart/form-data'):
        message = BytesParser(policy=default).parsebytes(
            b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + body
        )
        fields = {}
        upload = None
        for part in message.iter_parts():
            name = part.get_param('name', header='content-disposition')
            filename = part.get_filename()
            if not name:
                continue
            if filename:
                upload = (name, filename, part.get_payload(decode=True))
            else:
                fields[name] = part.get_content()
        return fields, upload

    return dict(parse_qsl(body.decode('utf-8'), keep_blank_values=True)), None


def application(environ, start_response):
    logger.warning("python_server application started")
    # response for POST
    if environ['REQUEST_METHOD'] == 'POST':
        post, upload = parse_post(environ)

        # xml_data is a long-lived, per-process object; reload it so we
        # never overwrite fields the alarm daemon changed on disk since.
        xml_data.read_data()

        for s in post:
            if s == 'deleteMp3File':
                    filename = os.path.basename(post[s])
                    file_path = os.path.join('./music', filename)
                    try:
                        os.remove(file_path)
                        xml_data.readFileNamesInMusicDirectory()
                        logger.warning("Deleted MP3 file %s", filename)
                    except OSError as error:
                        logger.warning("Could not delete MP3 file %s: %s", filename, error)
                        start_response('400 Bad Request', [('content-type', 'text/plain')])
                        return [b'Could not delete MP3 file.']
            else:
                try:
                    xml_data.changeValue(s, post[s])
                    logger.warning("{} changed to {}".format(s, post[s]))
                except Exception as e:
                    logger.warning("Error: Couldn't change xml entry {} to {} with error: {}".format(s, post[s], e))

        if upload:
            _, uploaded_filename, uploaded_data = upload
            filename = os.path.basename(uploaded_filename)
            try:
                with open(os.path.join('./music', filename), 'wb') as f:
                    f.write(uploaded_data)
                xml_data.readFileNamesInMusicDirectory()
                logger.warning("Uploaded MP3 file %s", filename)
            except (OSError, ValueError) as error:
                logger.warning("Could not upload MP3 file %s: %s", filename, error)
                start_response('400 Bad Request', [('content-type', 'text/plain')])
                return [b'Could not upload MP3 file.']


    path = environ['PATH_INFO']
    if path != '/data.xml':
        path = './web' + path
    else:
        path = '.' + path

    if os.path.exists(path):
        if path == './web/':
            path = './web/index.html'
        h = open(path, 'rb')
        content = h.read()
        h.close()

        headers = [('content-type', content_type(path))]
        if path == './data.xml':
            headers.append(('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0'))
        start_response('200 OK', headers)
        return [content]
    else:
        return show_404_app(environ, start_response, path)


def content_type(path):
    """Return a guess at the mime type for this path
    based on the file extension"""

    name, ext = os.path.splitext(path)

    if ext in MIME_TABLE:
        return MIME_TABLE[ext]
    else:
        return "application/octet-stream"


def show_404_app(environ, start_response, path):
    start_response('404 Not Found', [('content-type','text/html')])
    return ["""<html><h1>""" + path + """ not Found</h1><p>
               That page is unknown. Return to
               the <a href="/">alarm clock</a>.</p>
               </html>""", ]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    import webbrowser

    httpd = make_server('', 8090, application)
    logger.debug('Serving on port 8090...')

    url = "http://127.0.0.1:8090"
    webbrowser.open(url)

    try:
        while True:
            logger.debug('Server request.')
            httpd.handle_request()
    except KeyboardInterrupt:  # Strg + C
        httpd.server_close()
        logger.warning('Server Closed.')
    except:
        httpd.server_close()
        logger.error('Error')
