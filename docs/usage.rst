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
    0.9171
    >>> item['collection_country']   # country of origin of the specimen in BOLD
    'Brazil'
    >>> item['latitude']
    -23.9
    >>> item['longitude']
    -46.39

TaxonSearch API
---------------

Also known as **Taxon Name Service** found at this URL:
http://www.boldsystems.org/index.php/resources/api?type=taxonomy#Ideasforwebservices-SequenceParameters

It retrieves taxonomic information based on a taxon name::

    >>> import bold
    >>> taxonomic_identification = 'Euptychia ordinata'

    >>> res = bold.call_taxon_search(taxonomic_identification, fuzzy=False)
    >>> res.tax_id
    302603
    >>> res.tax_division
    'Animals'
    >>> res.tax_rank
    'species'
    >>> res.parent_name
    'Euptychia'
    >>> res.parent_id
    7044
