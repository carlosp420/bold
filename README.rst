===================================================
Bold - Python library to invoke the BOLDSYSTEMS API
===================================================

.. image:: https://travis-ci.org/carlosp420/bold.svg
        :target: https://travis-ci.org/carlosp420/bold
.. image:: https://coveralls.io/repos/carlosp420/bold/badge.png
        :target: https://coveralls.io/r/carlosp420/bold
.. image:: https://readthedocs.org/projects/bold/badge/?version=latest
        :target: http://bold.readthedocs.org/en/latest/
        :alt: Documentation Status

Documentation: https://bold.readthedocs.org
-------------------------------------------

What?
-----
``bold`` is a Python library that can be used to interact with the BOLDSYSTEMS
API. ``bold`` has methods to send COI sequences to BOLDSYSTEMS in order to
identify species using DNA barcoding.

Quick start
-----------
First:

.. code-block:: shell

    $ pip install bold

Then:

.. code-block:: python

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

    >>> taxonomic_identification = 'Euptychia ordinata'

    >>> res = bold.call_taxon_search(taxonomic_identification, fuzzy=False)
    >>> item = res.items[0]  # there can be more than one result
    >>> item['tax_id']
    302603
    >>> item['tax_division']
    'Animals'

    >>> tax_id = 302603

    >>> res = bold.call_taxon_data(tax_id, data_type='basic')
    >>> item = res.items[0]
    >>> item['tax_rank']
    'species'
    >>> item['parent_id']
    7044

    >>> res = bold.call_specimen_data(taxon='Euptychia|Splendeuptychia')
    >>> item = res.items[0]
    >>> item['taxonomy_family_taxon_name']
    'Nymphalidae'

    >>> res = bold.call_sequence_data(taxon='Hermeuptychia', geo='Peru')
    >>> items = res.items
    >>> [item.id for item in items]
    ['GBLN4477-14|Hermeuptychia', 'GBLN4478-14|Hermeuptychia', 'GBLN4479-14|Hermeuptychia']

    >>> res = bold.call_full_data(taxon='Hermeuptychia', geo='Peru')
    >>> item = res.items[0]
    >>> [item['sequences_sequence_genbank_accession'] for item in res.items]
    ['KF466142', 'KF466143', 'KF466144']

    >>> res = bold.call_trace_files(taxon='Euptychia mollis',
    ...                             institutions='York University')
    >>> with open("trace_files.tar", "wb") as handle:
    ...     handle.write(res.file_contents)
    4106240

Further documentation can be found at https://bold.readthedocs.org

