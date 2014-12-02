=====
Usage
=====
This package BOLD can be used to interact with the BOLDSYSTEMS API. We can use
methods to interact with the several end-points.

ID Engine API
-------------
The ID Engine API is found at this URL:
http://www.boldsystems.org/index.php/resources/api?type=idengine

How to use it::

    >>> import bold
    >>> seq = 'TTTTTGGTATTTGAGCAGGAATAGTAGGAACTTCTCTCAGTTTAATTATTCGAATAGAATTAGGTAATCCAGGTTTCTTAATTGGAGATGATCAAATTTATAATACTATTGTAACAGCCCATGCTTTTATTATAATTTTTTTTATAGTTATACCTATTGTAATTGGAGGATTTGGAAATTGACTAGTTCCCCTAATATTAGGTGCACCTGATATAGCTTTCCCTCGTATAAATAATATAAGATATTGACTACTTCCACCATCTTTAATATTATTAATTTCAAGTAGTATTGTAGAAAATGGAGCTGGAACAGGTTGAACAGTTTACCCCCCTCTTTCCTCTAATATTGCTCATAGAGGAACCTCAGTAGACTTAGCAATTTTTTCTCTTCATTTAGCTGGTATTTCTTCTATTTTAGGAGCTATTAATTTTATTACTACAATTATTAATATACGAGTTAATGGAATATCCTATGATCAAATACCTTTATTTGTTTGAGCTGTTGGAATTACAGCTCTTCTTTTACTTCTTTCTTTACCTGTTTTAGCAGGAGCTATCACAATACTTCTTACAGATCGAAATTTAAATACATCATTTTTTGATCCTGCAGGAGGAGGTGATCCAATTTTATACCAACATTTATTTTGATTTTTTGGTCACCC'

    >>> res = bold.call_id(seq, db='COX1')

    >>> # res.items will contain a list of BOLD identifications including
    >>> # additional metadata. Let us look at one of the items:
    >>> item = res.items[1]

    >>> item['bold_id']  # this is the ID assigned by BOLD
    'GBLN3590-14'
    >>> item['taxonomic_identification']   # the species name
    'Hermeuptychia gisella'
    >>> item['similarity']   # degree of Barcode similiarity
    '0.9171'
    >>> item['specimen_collection_location_country']   # country of origin of the specimen in BOLD
    'Brazil'
    >>> item['specimen_collection_location_latitude']
    '-23.9'
    >>> item['specimen_collection_location_longitude']
    '-46.39'

TaxonSearch API
---------------

Also known as **Taxon Name Service** found at this URL:
http://www.boldsystems.org/index.php/resources/api?type=taxonomy#Ideasforwebservices-SequenceParameters

It retrieves taxonomic information based on a **taxon name**::

    >>> import bold
    >>> taxonomic_identification = 'Euptychia ordinata'

    >>> res = bold.call_taxon_search(taxonomic_identification, fuzzy=False)
    >>> item = res.items[0]  # there can be more than one result
    >>> item['tax_id']
    302603
    >>> item['tax_division']
    'Animals'
    >>> item['tax_rank']
    'species'
    >>> item['parent_name']
    'Euptychia'
    >>> item['parent_id']
    7044

TaxonData API
-------------

Also known as **Taxonomy ID Service** found at this URL:
http://www.boldsystems.org/index.php/resources/api?type=taxonomy#Ideasforwebservices-SpecimenParameters
It retrieves taxonomic information based on a
**BOLD taxonomy ID** (``tax_id``).

The ``data_type=basic`` API call returns similar metadata as our method
``bold.call_taxon_search``::

    >>> import bold
    >>> tax_id = 302603

    >>> res = bold.call_taxon_data(tax_id, data_type='basic')
    >>> item = res.items[0]
    >>> item['tax_rank']
    'species'
    >>> item['parent_id']
    7044

The ``data_tye=all`` API call returns additional data from several sources::

    >>> res = bold.call_taxon_data(tax_id, data_type='all')
    >>> item = res.items[0]
    >>> item['gbif_map']
    'http://data.gbif.org/species/5132936/overviewMap.png'
    >>> item['sequencinglabs']
    {'Mined from GenBank': 1}

It is possible to obtain other kinds of data_type or do combination of them.
See here for more info http://www.boldsystems.org/index.php/resources/api?type=taxonomy
For example, we can get metadata about ``images`` alone, or in combination with
the ``basic`` data_type::

    >>> import bold
    >>> tax_id = 88899
    >>> res = bold.call_taxon_data(tax_id, data_type='basic,images')
    >>> item = res.items[0]
    >>> item['taxon']
    'Momotus'
    >>> [(i['image'], i['photographer']) for i in item['images']]
    [('BSPBB/MJM_7364_IMG_2240_d+1345758620.JPG', 'Oscar Lopez')]

Specimen data retrieval
-----------------------
API calls to retrieve matching specimen data records for a combination of
parameters.
See here for more info http://www.boldsystems.org/index.php/resources/api?type=webservices

Parameters can accept more than one value by using the pipe symbol ``|``, which
is equivalent do ``OR``.::

    >>> res = bold.call_specimen_data(taxon='Euptychia|Splendeuptychia')
    >>> item = res.items[0]
    >>> item['taxonomy_family_taxon_name']
    'Nymphalidae'

    >>> res = bold.call_specimen_data(ids='11-SRNP-42276')
    >>> item = res.items[0]
    >>> [i for i in item['specimen_imagery_media_image_file']]
    ['http://www.boldsystems.org/pics/MHMYM/11-SRNP-42276-DHJ543456+1331929372.jpg', 'http://www.boldsystems.org/pics/MHMYM/11-SRNP-42276-DHJ543457+1331929372.jpg']

    >>> bin = 'BOLD:AAE2777'
    >>> res = bold.call_specimen_data(bin=bin)
    >>> class_taxon_names = [item['taxonomy_class_taxon_name'] for item in res.items]
    >>> class_taxon_names[0]
    'Insecta'

By default, ``bold.call_specimen_data`` will return items as dictionary
objects. However, it is also possible to get data from BOLD as tab-separated
values that can be opened in MS Excel-like software.::

    >>> res = bold.call_specimen_data(geo='Iceland', format='tsv')
    >>> with open("output_file.csv", "w") as handle:
    ...     handle.write(res.items)
    186060

Sequence data retrieval
-----------------------
API calls to retrieve DNA sequences for records using a combination of
parameters.
See here for more info http://www.boldsystems.org/index.php/resources/api?type=webservices
Bio.bold returns the data as a list of SeqRecord objects.

Parameters can accept more than one value by using the pipe symbol ``|``, which
is equivalent do ``OR``.::

    >>> res = bold.call_sequence_data(taxon='Hermeuptychia', geo='Peru')
    >>> items = res.items
    >>> [item.id for item in items]
    ['GBLN4477-14|Hermeuptychia', 'GBLN4478-14|Hermeuptychia', 'GBLN4479-14|Hermeuptychia']


Full Data Retrieval (Specimen + Sequence)
-----------------------------------------
Retrieves TSV file or item objects of data from voucher, taxonomic, specimen,
collection data and sequence for each record.
BOLD does not support the FASTA format for this API call.::

    >>> res = bold.call_full_data(taxon='Hermeuptychia', geo='Peru')
    >>> item = res.items[0]
    >>> [item['sequences_sequence_genbank_accession'] for item in res.items]
    ['KF466142', 'KF466143', 'KF466144']


Trace File Data Retrieval
-------------------------
Trace files can be retrieved from BOLD by querying with several parameters.
Returns a TAR file consisting of compressed Trace Files (traces in either
.ab1 or .scf format) along with a file listing the Process ID, taxon and
marker for each Trace File included.
This call will return the file contents ready to be written to a file.::

    >>> res = bold.call_trace_files(taxon='Euptychia mollis',
    ...                             institutions='York University')
    >>> with open("trace_files.tar", "wb") as handle:
    ...     handle.write(res.file_contents)
    4106240
