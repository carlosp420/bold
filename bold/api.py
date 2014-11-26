import json
import os
import re
from random import randint
import sys
import warnings
import xml
import xml.etree.ElementTree as ET

from Bio import BiopythonWarning
from Bio import SeqIO
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
        if result_string.strip() == '':
            raise ValueError("BOLD did not return any result.")

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
            self.parse_json(result_string)

        if service == 'call_taxon_data':
            self.parse_json(result_string)

        if service == 'call_specimen_data' or service == 'call_full_data':
            # Result_string could be data as tab-separated values (tsv)
            # ugly hack for python 2.6 that does not have ET.ParseError
            if sys.version.startswith('2.6'):
                try:
                    self.parse_xml(result_string)
                except xml.parsers.expat.ExpatError:
                    self.items = result_string
            else:
                try:
                    self.parse_xml(result_string)
                except ET.ParseError:
                    self.items = result_string

        if service == 'call_sequence_data':
            self.parse_fasta(result_string)

    def parse_json(self, result_string):
        items_from_bold = []
        append = items_from_bold.append
        response = json.loads(result_string)
        if hasattr(response, 'items'):
            # Is this a simple JSON and we got only one item?
            simple_json = False
            for i in response.keys():
                res = re.search('^[0-9]+', i)
                if res is None:
                    simple_json = True

            if simple_json is True:
                response = [response]
            for obj in response:
                item = dict()
                try:
                    json_obj = response[obj]
                except TypeError:
                    json_obj = obj

                for k, v in json_obj.items():
                    if k == 'taxid':
                        item['tax_id'] = v
                    elif k == 'taxon':
                        item['taxon'] = v
                    elif k == 'tax_rank':
                        item['tax_rank'] = v
                    elif k == 'tax_division':
                        item['tax_division'] = v
                    elif k == 'parentid':
                        item['parent_id'] = v
                    elif k == 'parentname':
                        item['parent_name'] = v
                    elif k == 'taxonrep':
                        item['taxon_rep'] = v
                    else:
                        item[k] = v
                append(item)
            self.items = items_from_bold
        else:
            raise ValueError("BOLD did not return any result.")

    def parse_xml(self, result_string):
        items_from_bold = []
        append = items_from_bold.append

        root = ET.fromstring(result_string)
        for match in root.findall('record'):
            item = dict()
            fields = [
                'record_id',
                'processid',
                'bin_uri',
                'specimen_identifiers/sampleid',
                'specimen_identifiers/catalognum',
                'specimen_identifiers/fieldnum',
                'specimen_identifiers/institution_storing',
                'taxonomy/identification_provided_by',
                'taxonomy/phylum/taxon/taxID',
                'taxonomy/phylum/taxon/name',
                'taxonomy/class/taxon/taxID',
                'taxonomy/class/taxon/name',
                'taxonomy/order/taxon/taxID',
                'taxonomy/order/taxon/name',
                'taxonomy/family/taxon/taxID',
                'taxonomy/family/taxon/name',
                'taxonomy/genus/taxon/taxID',
                'taxonomy/genus/taxon/name',
                'taxonomy/species/taxon/taxID',
                'taxonomy/species/taxon/name',
                'specimen_details/voucher_type',
                'specimen_details/voucher_desc',
                'specimen_details/extrainfo',
                'specimen_details/lifestage',
                'collection_event/collector',
                'collection_event/collectors',
                'collection_event/collectiondate',
                'collection_event/coordinates/lat',
                'collection_event/coordinates/long',
                'collection_event/exactsite',
                'collection_event/country',
                'collection_event/province',
                'specimen_imagery/media/mediaID',
                'specimen_imagery/media/caption',
                'specimen_imagery/media/metatags',
                'specimen_imagery/media/copyright',
                'specimen_imagery/media/image_file',
                'tracefiles/read/read_id',
                'tracefiles/read/run_date',
                'tracefiles/read/sequencing_center',
                'tracefiles/read/direction',
                'tracefiles/read/seq_primer',
                'tracefiles/read/trace_link',
                'tracefiles/read/markercode',
                'sequences/sequence/sequenceID',
                'sequences/sequence/markercode',
                'sequences/sequence/genbank_accession',
                'sequences/sequence/nucleotides',
            ]
            for field in fields:
                if match.find(field) is not None:
                    key = field.replace('/', '_')
                    matched = match.findall(field)
                    if len(matched) == 0:
                        item[key] = None
                    elif len(matched) == 1:
                        item[key] = match.find(field).text
                    elif len(matched) > 1:
                        item[key] = [i.text for i in matched]
            append(item)
        self.items = items_from_bold

    def parse_fasta(self, result_string):
        filename = "tmp_" + str(randint(1, 1000000)) + ".fas"
        with open(filename, "w") as handle:
            handle.write(result_string)
        generator = SeqIO.parse(filename, "fasta")
        self.items = [i for i in generator]
        os.remove(filename)


class Request(object):
    """Constructs a :class:`Request <Request>`. Sends it and returns a
    :class:`Response <Response>` object.
    """
    def get(self, service, **kwargs):
        """
        Does HTTP request to BOLD webservice.

        :param service: the BOLD API alias to interact with.
        """
        params = ''

        if service == 'call_id':
            sequence = utils._prepare_sequence(kwargs['seq'])
            params = _urlencode({'db': kwargs['db'], 'sequence': sequence})

        if service == 'call_taxon_search':
            if kwargs['fuzzy']:
                # TODO: it shouldn't be: if kwargs['fuzzy'] is True ?
                fuzzy = 'true'
            else:
                fuzzy = 'false'
            params = _urlencode({
                'taxName': kwargs['taxonomic_identification'],
                'fuzzy': fuzzy,
            })

        if service == 'call_taxon_data':
            params = _urlencode({
                'taxId': kwargs['tax_id'],
                'dataTypes': kwargs['data_type'],
            })

        if service == 'call_specimen_data':
            payload = dict()
            for k, v in kwargs.items():
                if v is not None and k != 'url':
                    payload[k] = v
            params = _urlencode(payload)

        if service == 'call_sequence_data':
            payload = dict()
            for k, v in kwargs.items():
                if v is not None and k != 'url':
                    payload[k] = v
            params = _urlencode(payload)

        if service == 'call_full_data':
            payload = dict()
            for k, v in kwargs.items():
                if v is not None and k != 'url':
                    payload[k] = v
            params = _urlencode(payload)

        url = kwargs['url'] + "?" + params
        req = _Request(url, headers={'User-Agent': 'BiopythonClient'})
        handle = _urlopen(req)
        result = _as_string(handle.read())
        response = Response()
        response.parse_data(service, result)
        return response


def request(service, **kwargs):
    """Build our request. Also do checks for proper use of arguments.

    :param service: the BOLD API alias to interact with.
    :return: Request object with correct URL:
             end-point for the API of the service of interest.
    """
    req = Request()

    if service == 'call_id':
        # User wants the service `call_id`. So we need to use this URL:
        url = "http://boldsystems.org/index.php/Ids_xml"
        return req.get(service=service, url=url, **kwargs)

    if service == 'call_taxon_search':
        url = "http://www.boldsystems.org/index.php/API_Tax/TaxonSearch"
        return req.get(service=service, url=url, **kwargs)

    if service == 'call_taxon_data':
        url = "http://www.boldsystems.org/index.php/API_Tax/TaxonData"
        return req.get(service=service, url=url, **kwargs)

    if service == 'call_specimen_data':
        url = "http://www.boldsystems.org/index.php/API_Public/specimen"

        args_returning_lots_of_data = ['institutions', 'researchers', 'geo']
        for arg in args_returning_lots_of_data:
            if kwargs[arg] is not None:
                warnings.warn('Requesting ``' + arg + '`` data from BOLD will '
                              'possibly return a lot of records and the transfer '
                              'of data might take a lot of time to complete as '
                              'many Megabytes are expected.',
                              BiopythonWarning
                              )
        return req.get(service=service, url=url, **kwargs)

    if service == 'call_sequence_data':
        url = "http://www.boldsystems.org/index.php/API_Public/sequence"
    elif service == 'call_full_data':
        url = "http://www.boldsystems.org/index.php/API_Public/combined"

    args_returning_lots_of_data = ['institutions', 'researchers', 'geo']
    for arg in args_returning_lots_of_data:
        if kwargs[arg] is not None:
            warnings.warn('Requesting ``' + arg + '`` data from BOLD will '
                                                  'possibly return a lot of records and the transfer '
                                                  'of data might take a lot of time to complete as '
                                                  'many Megabytes are expected.',
                          BiopythonWarning
                          )
    return req.get(service=service, url=url, **kwargs)


def call_id(seq, db, **kwargs):
    """Call the ID Engine API
    http://www.boldsystems.org/index.php/resources/api?type=idengine

    :param seq: DNA sequence string or seq_record object.
    :param db: the BOLD database of available records.
               Choices: ``COX1_SPECIES``, ``COX1``, ``COX1_SPECIES_PUBLIC``,
               ``COX1_L640bp``.
    :param kwargs:
    :return:
    """
    return request('call_id', seq=seq, db=db, **kwargs)


def call_taxon_search(taxonomic_identification, fuzzy=False):
    """Call the TaxonSearch API
    http://www.boldsystems.org/index.php/resources/api?type=taxonomy#Ideasforwebservices-SequenceParameters

    :param taxonomic_identification: species or any taxon name
    :param fuzzy: False by default
    :return:
    """
    # TODO check when Fuzzy is True
    return request('call_taxon_search',
                   taxonomic_identification=taxonomic_identification,
                   fuzzy=fuzzy
                   )


def call_taxon_data(tax_id, data_type=None):
    """Call the TaxonData API. It has several methods to get additional
    metadata.

    :param tax_id:
    :param data_type: ``basic|all|images``. Default is ``basic``.
    :return:
    """
    if data_type is None:
        # We will use by default data_type='basic'
        data_type = 'basic'
    return request('call_taxon_data', tax_id=tax_id, data_type=data_type)


def call_specimen_data(taxon=None, ids=None, bin=None, container=None,
                       institutions=None, researchers=None, geo=None,
                       format=None):
    """Call the Specimen Data Retrieval API. Returns matching specimen data
    records.

    :param taxon: ``Aves|Reptilia``, ``Bos taurus``
    :param format: Optional: ``format='tsv'`` will return results a string
                   containing data in tab-separated values. If not used, the
                   data will be returned as dictionary (default behaviour).
    :return:
    """
    if format is not None and format != 'tsv':
        raise ValueError('Invalid value for ``format``')

    return request('call_specimen_data', taxon=taxon, ids=ids, bin=bin,
                   container=container, institutions=institutions,
                   researchers=researchers, geo=geo, format=format
                   )


def call_sequence_data(taxon=None, ids=None, bin=None, container=None,
                       institutions=None, researchers=None, geo=None,
                       marker=None):
    """Call the Specimen Data Retrieval API. Returns DNA sequences in FASTA
    format for matching records.

    :param taxon: ``Aves|Reptilia``, ``Bos taurus``
    :return: Seq objects
    """
    return request('call_sequence_data', taxon=taxon, ids=ids, bin=bin,
                   container=container, institutions=institutions,
                   researchers=researchers, geo=geo, marker=marker
                   )


def call_full_data(taxon=None, ids=None, bin=None, container=None,
                   institutions=None, researchers=None, geo=None,
                   marker=None, format=None):
    """Call the Full Data Retrieval API (combined). Returns data as TSV format
    or list of dicts parsed from a XML file.

    :param taxon: ``Aves|Reptilia``, ``Bos taurus``
    :return: Seq objects
    """
    if format is not None and format != 'tsv':
        raise ValueError('Invalid value for ``format``')

    return request('call_full_data', taxon=taxon, ids=ids, bin=bin,
                   container=container, institutions=institutions,
                   researchers=researchers, geo=geo, marker=marker, format=format
                   )
