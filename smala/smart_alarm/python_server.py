import cgi
import sys
import os.path
import logging

# important for apache web server:
project_path = os.environ['smart_alarm_path']
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


def application(environ, start_response):
    logger.warning("python_server application started")
    # response for POST
    if environ['REQUEST_METHOD'] == 'POST':
        post = cgi.FieldStorage(
           fp=environ['wsgi.input'],
           environ=environ,
           keep_blank_values=False
        )

        # xml_data is a long-lived, per-process object; reload it so we
        # never overwrite fields the alarm daemon changed on disk since.
        xml_data.read_data()

        for s in post:
            if s == 'uploadMp3File':
                item = post['uploadMp3File']
                filename = os.path.basename(item.filename)
                try:
                    with open(os.path.join('./music', filename), 'wb') as f:
                        f.write(item.file.read())
                    xml_data.readFileNamesInMusicDirectory()
                    logger.warning("Uploaded MP3 file %s", filename)
                except (OSError, ValueError) as error:
                    logger.warning("Could not upload MP3 file %s: %s", filename, error)
                    start_response('400 Bad Request', [('content-type', 'text/plain')])
                    return [b'Could not upload MP3 file.']
            elif s == 'deleteMp3File':
                    filename = os.path.basename(post.getvalue(s))
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
                    xml_data.changeValue(s, post.getvalue(s))
                    logger.warning("{} changed to {}".format(s, post.getvalue(s)))
                except Exception as e:
                    logger.warning("Error: Couldn't change xml entry {} to {} with error: {}".format(s, post.getvalue(s), e))


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
