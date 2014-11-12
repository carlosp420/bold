import xml.etree.ElementTree as ET

from Bio._py3k import Request as _Request
from Bio._py3k import urlopen as _urlopen
from Bio._py3k import urlencode as _urlencode
from Bio._py3k import _as_bytes
from Bio._py3k import _as_string


class Response(object):
    """Accepts results from a call to the BOLD API. Parses the data and returns
    a Response object.
    """
    def __init__(self):
        self.id_from_bold = ''

    def parse_data(self, result_string):
        root = ET.fromstring(result_string)
        ids_from_bold = []
        for match in root.findall('match'):
            out = dict()
            # out['seq'] = str(seq_object)
            # out['id'] = str(id)
            similarity = match.find('similarity').text
            out['similarity'] = similarity
            tax_id = match.find('taxonomicidentification').text
            out['tax_id'] = tax_id

            if match.find('specimen/collectionlocation/country').text:
                ctry = match.find('specimen/collectionlocation/country').text
                out['collection_country'] = ctry
            else:

                out['collection_country'] = "None"

            myid = match.find('ID').text
            out['bold_id'] = myid

            # good code from here
            # TODO parse all items as objects
            ids_from_bold.append(myid)
        self.id_from_bold = ids_from_bold



class Request(object):
    """Constructs a :class:`Request <Request>`. Sends it and returns a
    :class:`Response <Response>` object.
    """
    def get(self, service, seq, db, url, **kwargs):
        """
        :param service: the BOLD API alias to interact with.
        :param seq: DNA sequence string or seq_record object.
        :param db: the BOLD database of available records.
                   Choices: ``COX1_SPECIES``, ``COX1``, ``COX1_SPECIES_PUBLIC``,
                   ``COX1_L640bp``.
        :param url: end-point for the API of the service of interest.
        """
        # TODO convert seq to string sequence if it is seq_record object
        params = _urlencode({'db': db, 'sequence': seq})
        f = url + "?" + params
        req = _Request(f, headers={'User-Agent': 'BiopythonClient'})
        handle = _urlopen(req)
        result = _as_string(handle.read())
        response = Response()
        response.parse_data(result)
        return response


def request(service, seq, db, **kwargs):
    """Build our request.

    :param service: the BOLD API alias to interact with.
    :param seq: DNA sequence string or seq_record object.
    :param db: the BOLD database of available records.
               Choices: ``COX1_SPECIES``, ``COX1``, ``COX1_SPECIES_PUBLIC``,
               ``COX1_L640bp``.
    :return
    """
    url = ''
    if service == 'call_id':
        # User wants the service `call_id`. So we need to use this URL:
        url = "http://boldsystems.org/index.php/Ids_xml"
    req = Request()
    return req.get(service=service, seq=seq, db=db, url=url, **kwargs)


def call_id(seq, db, **kwargs):
    """Call the ID Engine API
    http://www.boldsystems.org/index.php/resources/api?type=idengine

    :param seq:
    :param db:
    :param kwargs:
    :return:
    """
    return request('call_id', seq, db, **kwargs)