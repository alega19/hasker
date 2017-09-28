import json

from django.http import HttpResponse


class AjaxResponse(HttpResponse):

    def __init__(self, error=False, errmsg='Unknown error', **kwargs):
        kwargs['error'] = error
        if error:
            kwargs['errmsg'] = errmsg
        content = json.dumps(kwargs)
        super(AjaxResponse, self).__init__(content_type='application/json', content=content)
