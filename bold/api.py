class Request(object):
    def get(self, service, url, db, **kwargs):
        return "hola k awse"


def request(service, db, **kwargs):
    """Constructs a :class:`Request <Request>`.
    Returns a :class:`Response <Response>` object.
    """
    # User wants the service `call_id`. So we need to use this URL:
    url = "http://boldsystems.org/index.php/Ids_xml"
    req = Request()
    return req.get(service=service, url=url, db=db, **kwargs)


def call_id(seq, db, **kwargs):
    return request('call_id', db, **kwargs)