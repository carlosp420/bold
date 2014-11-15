import json
import logging
import xml.etree.ElementTree as ET

from Bio._py3k import Request as _Request
from Bio._py3k import urlopen as _urlopen
from Bio._py3k import urlencode as _urlencode
from Bio._py3k import _as_string

from . import utils


class Response(object):
    """Accepts results from a call to the BOLD API. Parses the data and returns
    a Response object.
    """
    def __init__(self):
        self.items = []
        self.tax_id = ''
        self.taxon = ''
        self.tax_rank = ''
        self.tax_division = ''
        self.parent_id = ''
        self.parent_name = ''
        self.taxon_rep = ''

    def parse_data(self, service, result_string):
        """Parses XML response from BOLD.

        :param result_string: XML or JSON string returned from BOLD
        :return: list of all items as dicts if service=call_id
        """
        if service == 'call_id':
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

        if service == 'call_taxon_search':
            response = json.loads(result_string)
            if hasattr(response, 'items'):
                for k, v in response.items():
                    try:
                        self.tax_id = int(k)
                        if v['taxon']:
                            self.taxon = v['taxon']
                        if v['tax_rank']:
                            self.tax_rank = v['tax_rank']
                        if v['tax_division']:
                            self.tax_division = v['tax_division']
                        if v['parentid']:
                            self.parent_id = v['parentid']
                        if v['parentname']:
                            self.parent_name = v['parentname']
                        if v['taxonrep']:
                            self.taxon_rep = v['taxonrep']
                    except KeyError:
                        attrs = {'tax_id': self.tax_id, 'taxon': self.taxon,
                                 'tax_rank': self.tax_rank, 'tax_division': self.tax_division,
                                 'parent_id': self.parent_id, 'parent_name': self.parent_name,
                                 'taxon_rep': self.taxon_rep,
                                 }
                        for k, v in attrs.items():
                            if v == '':
                                # TODO show that warning comes from this module and function
                                logging.warning("Couldn't find value for: ``%s``" % k)




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

        if service == 'call_taxon_search':
            if kwargs['fuzzy']:
                fuzzy = 'true'
            else:
                fuzzy = 'false'
            params = _urlencode({
                'taxName': kwargs['taxonomic_identification'],
                'fuzzy': fuzzy,
            })
            url = kwargs['url'] + "?" + params

        req = _Request(url, headers={'User-Agent': 'BiopythonClient'})
        handle = _urlopen(req)
        result = _as_string(handle.read())
        response = Response()
        response.parse_data(service, result)
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

    if service == 'call_taxon_search':
        url = "http://www.boldsystems.org/index.php/API_Tax/TaxonSearch"
        return req.get(service=service, url=url, **kwargs)


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
    return request('call_taxon_search',
                   taxonomic_identification=taxonomic_identification,
                   fuzzy=fuzzy
                   )
