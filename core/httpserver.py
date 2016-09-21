from __future__ import print_function, absolute_import
from shadowsocks import eventloop

class SlowHTTPServer():
    '''SSLand built-in but really slow WSGI server

    Works with shadowsocks.eventloop
    `server` is the WSGIServer instance.
    '''

    def __init__(self, wsgi_app, port=8000):
        from web.urls import urlpatterns
        from wsgiref.simple_server import make_server
        from django.conf.urls import url
        def static_view(request, path):
            from django.http import HttpResponse, HttpResponseNotFound
            from django.contrib.staticfiles.finders import find
            import mimetypes
            fp = find(path)
            if fp:
                resp = HttpResponse(
                    file(fp, 'rb').read(),
                    content_type = mimetypes.guess_type(path, strict=False)[0]
                )
                resp['Cache-Control'] = 'max-age=300'
            else:
                resp = HttpResponseNotFound()
            return resp
        urlpatterns.append(url(r'^static/(?P<path>[^\?]+)$', static_view))
        self.server = make_server('', port, wsgi_app)
    
    def add_to_loop(self, loop):
        loop.add(self.server, eventloop.POLL_IN, self)
    
    def handle_event(self, sock, fd, event):
        if sock == self.server and event == eventloop.POLL_IN:
            self.server.handle_request()
