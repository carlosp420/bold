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
from Bio._py3k import StringIO

from . import utils


class Response(object):
    """Accepts results from a call to the BOLD API. Parses the data and returns
    a Response object.
    """
    def _parse_data(self, service, result_string):
        """Parses XML response from BOLD.

        :param result_string: XML or JSON string returned from BOLD
        :return: list of all items as dicts if service=call_id
        """
        self.method = service

        if result_string.strip() == '':
            raise ValueError("BOLD did not return any result.")

        if service == 'call_taxon_search' or service == 'call_taxon_data':
            self._parse_json(result_string)

        if service == 'call_specimen_data' or service == 'call_full_data' or \
                service == 'call_id':
            # Result_string could be data as tab-separated values (tsv)
            # ugly hack for python 2.6 that does not have ET.ParseError
            if sys.version.startswith('2.6'):
                try:
                    self._parse_xml(result_string)
                except xml.parsers.expat.ExpatError:
                    self.items = result_string
            else:
                try:
                    self._parse_xml(result_string)
                except ET.ParseError:
                    self.items = result_string

        if service == 'call_sequence_data':
            self._parse_fasta(result_string)

        if service == 'call_trace_files':
            # file_contents is in binary form
            self.file_contents = result_string

    def _parse_json(self, result_string):
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

    def _parse_xml(self, result_string):
        items_from_bold = []
        append = items_from_bold.append

        if self.method == 'call_id':
            xml_tag = 'match'
        else:
            xml_tag = 'record'

        root = ET.fromstring(result_string)
        for match in root.findall(xml_tag):
            item = dict()
            fields = [
                # These pairs correspond to convertions of key names from BOLD
                # to friendly versions:
                #
                # (key name from BOLD, friendlier key name)

                # For call_id
                ('ID', 'bold_id'),
                ('sequencedescription', 'sequence_description'),
                ('database', 'database'),
                ('citation', 'citation'),
                ('taxonomicidentification', 'taxonomic_identification'),
                ('similarity', 'similarity'),
                ('specimen/url', 'specimen_url'),
                ('specimen/collectionlocation/country', 'specimen_collection_location_country'),
                ('specimen/collectionlocation/coord/lat', 'specimen_collection_location_latitude'),
                ('specimen/collectionlocation/coord/lon', 'specimen_collection_location_longitude'),

                ('record_id', 'record_id'),
                ('processid', 'process_id'),
                ('bin_uri', 'bin_uri'),
                ('specimen_identifiers/sampleid', 'specimen_identifiers_sample_id'),
                ('specimen_identifiers/catalognum', 'specimen_identifiers_catalog_num'),
                ('specimen_identifiers/fieldnum', 'specimen_identifiers_field_num'),
                ('specimen_identifiers/institution_storing', 'specimen_identifiers_institution_storing'),
                ('taxonomy/identification_provided_by', 'taxonomy_identification_provided_by'),
                ('taxonomy/phylum/taxon/taxID', 'taxonomy_phylum_taxon_id'),
                ('taxonomy/phylum/taxon/name', 'taxonomy_phylum_taxon_name'),
                ('taxonomy/class/taxon/taxID', 'taxonomy_class_taxon_id'),
                ('taxonomy/class/taxon/name', 'taxonomy_class_taxon_name'),
                ('taxonomy/order/taxon/taxID', 'taxonomy_order_taxon_id'),
                ('taxonomy/order/taxon/name', 'taxonomy_order_taxon_name'),
                ('taxonomy/family/taxon/taxID', 'taxonomy_family_taxon_id'),
                ('taxonomy/family/taxon/name', 'taxonomy_family_taxon_name'),
                ('taxonomy/genus/taxon/taxID', 'taxonomy_genus_taxon_id'),
                ('taxonomy/genus/taxon/name', 'taxonomy_genus_taxon_name'),
                ('taxonomy/species/taxon/taxID', 'taxonomy_species_taxon_id'),
                ('taxonomy/species/taxon/name', 'taxonomy_species_taxon_name'),
                ('specimen_details/voucher_type', 'specimen_details_voucher_type'),
                ('specimen_details/voucher_desc', 'specimen_details_voucher_desc'),
                ('specimen_details/extrainfo', 'specimen_details_extra_info'),
                ('specimen_details/lifestage', 'specimen_details_lifestage'),
                ('collection_event/collector', 'collection_event_collector'),
                ('collection_event/collectors', 'collection_event_collectors'),
                ('collection_event/collectiondate', 'collection_event_collection_date'),
                ('collection_event/coordinates/lat', 'collection_event_coordinates_latitude'),
                ('collection_event/coordinates/long', 'collection_event_coordinates_longitude'),
                ('collection_event/exactsite', 'collection_event_exact_site'),
                ('collection_event/country', 'collection_event_country'),
                ('collection_event/province', 'collection_event_province'),
                ('specimen_imagery/media/mediaID', 'specimen_imagery_media_id'),
                ('specimen_imagery/media/caption', 'specimen_imagery_media_caption'),
                ('specimen_imagery/media/metatags', 'specimen_imagery_media_metatags'),
                ('specimen_imagery/media/copyright', 'specimen_imagery_media_copyright'),
                ('specimen_imagery/media/image_file', 'specimen_imagery_media_image_file'),
                ('tracefiles/read/read_id', 'tracefiles_read_read_id'),
                ('tracefiles/read/run_date', 'tracefiles_read_run_date'),
                ('tracefiles/read/sequencing_center', 'tracefiles_read_sequencing_center'),
                ('tracefiles/read/direction', 'tracefiles_read_direction'),
                ('tracefiles/read/seq_primer', 'tracefiles_read_seq_primer'),
                ('tracefiles/read/trace_link', 'tracefiles_read_trace_link'),
                ('tracefiles/read/markercode', 'tracefiles_read_marker_code'),
                ('sequences/sequence/sequenceID', 'sequences_sequence_sequence_id'),
                ('sequences/sequence/markercode', 'sequences_sequence_marker_code'),
                ('sequences/sequence/genbank_accession', 'sequences_sequence_genbank_accession'),
                ('sequences/sequence/nucleotides', 'sequences_sequence_nucleotides'),
            ]
            for field in fields:
                if match.find(field[0]) is not None:
                    key = field[1]
                    matched = match.findall(field[0])
                    if len(matched) == 0:
                        item[key] = None
                    elif len(matched) == 1:
                        item[key] = match.find(field[0]).text
                    elif len(matched) > 1:
                        item[key] = [i.text for i in matched]
            append(item)
        self.items = items_from_bold

    def _parse_fasta(self, result_string):
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

        if service == 'call_trace_files':
            payload = dict()
            for k, v in kwargs.items():
                if v is not None and k != 'url':
                    payload[k] = v
            params = _urlencode(payload)

        url = kwargs['url'] + "?" + params
        req = _Request(url, headers={'User-Agent': 'BiopythonClient'})
        handle = _urlopen(req)
        response = Response()
        if service == 'call_trace_files':
            binary_result = handle.read()
            response._parse_data(service, binary_result)
        else:
            result = _as_string(handle.read())
            response._parse_data(service, result)
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

    if service == 'call_trace_files':
        url = "http://www.boldsystems.org/index.php/API_Public/trace"

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


def call_trace_files(taxon=None, ids=None, bin=None, container=None,
                     institutions=None, researchers=None, geo=None,
                     marker=None):
    """
    Trace files can be retrieved from BOLD by querying with several parameters.

    :param taxon:
    :param ids:
    :param bin:
    :param container:
    :param institutions:
    :param researchers:
    :param geo:
    :param marker:
    :return: a TAR file consisting of compressed Trace Files (traces in either
             .ab1 or .scf format) along with a file listing the Process ID, taxon and
             marker for each Trace File included.
    """
    return request('call_trace_files', taxon=taxon, ids=ids, bin=bin,
                   container=container, institutions=institutions,
                   researchers=researchers, geo=geo, marker=marker
                   )
