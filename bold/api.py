import collections
import xml.etree.ElementTree as ET

from Bio._py3k import Request as _Request
from Bio._py3k import urlopen as _urlopen
from Bio._py3k import urlencode as _urlencode
from Bio._py3k import _as_bytes
from Bio._py3k import _as_string

from . import utils


class Response(object):
    """Accepts results from a call to the BOLD API. Parses the data and returns
    a Response object.
    """
    def __init__(self):
        self.items = []
        self.id_from_bold = ''

    def parse_data(self, result_string):
        """Parses XML response from BOLD.

        :param result_string: XML string returned from BOLD
        :return: list of all items as dicts
        """
        items_from_bold = []
        append = items_from_bold.append

        root = ET.fromstring(result_string)
        for match in root.findall('match'):
            item = dict()
            item['bold_id'] = match.find('ID').text
            item['sequencedescription'] = match.find('sequencedescription').text
            item['database'] = match.find('database').text
            item['citation'] = match.find('citation').text
            item['taxonomic_identification'] = match.find('taxonomicidentification').text
            item['similarity'] = float(match.find('similarity').text)

            if match.find('specimen/url').text:
                item['specimen_url'] = match.find('specimen/url').text
            else:
                item['specimen_url'] = ''

            if match.find('specimen/collectionlocation/country').text:
                item['collection_country'] = match.find('specimen/collectionlocation/country').text
            else:
                item['collection_country'] = ''

            if match.find('specimen/collectionlocation/coord/lat').text:
                item['latitude'] = float(match.find('specimen/collectionlocation/coord/lat').text)
            else:
                item['latitude'] = ''

            if match.find('specimen/collectionlocation/coord/lon').text:
                item['longitude'] = float(match.find('specimen/collectionlocation/coord/lon').text)
            else:
                item['longitude'] = ''

            append(item)
        self.items = items_from_bold


class Request(object):
    """Constructs a :class:`Request <Request>`. Sends it and returns a
    :class:`Response <Response>` object.
    """
    def get(self, service, **kwargs):
        """
        :param service: the BOLD API alias to interact with.
        :param seq: DNA sequence string or seq_record object.
        :param db: the BOLD database of available records.
                   Choices: ``COX1_SPECIES``, ``COX1``, ``COX1_SPECIES_PUBLIC``,
                   ``COX1_L640bp``.
        :param url: end-point for the API of the service of interest.
        """
        url = ''

        if service == 'call_id':
            sequence = utils._prepare_sequence(kwargs['seq'])
            params = _urlencode({'db': kwargs['db'], 'sequence': sequence})
            url = kwargs['url'] + "?" + params

        req = _Request(url, headers={'User-Agent': 'BiopythonClient'})
        handle = _urlopen(req)
        result = _as_string(handle.read())
        response = Response()
        response.parse_data(result)
        return response


def request(service, **kwargs):
    """Build our request.

    :param service: the BOLD API alias to interact with.
    :param seq: DNA sequence string or seq_record object.
    :param db: the BOLD database of available records.
               Choices: ``COX1_SPECIES``, ``COX1``, ``COX1_SPECIES_PUBLIC``,
               ``COX1_L640bp``.
    :return
    """
    req = Request()

    if service == 'call_id':
        # User wants the service `call_id`. So we need to use this URL:
        url = "http://boldsystems.org/index.php/Ids_xml"
        return req.get(service=service, url=url, **kwargs)
    #if service ==


def call_id(seq, db, **kwargs):
    """Call the ID Engine API
    http://www.boldsystems.org/index.php/resources/api?type=idengine

    :param seq:
    :param db:
    :param kwargs:
    :return:
    """
    return request('call_id', seq=seq, db=db, **kwargs)


def call_taxon_search(taxonomic_identification, fuzzy=False):
    """Call the
    :param taxonomic_identification: species or any taxon name
    :param fuzzy: False by default
    :return:
    """
    return request('call_taxon_search', fuzzy)
