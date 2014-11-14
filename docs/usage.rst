=====
Usage
=====

To use BOLD retriever in a project::

    >>> import bold

    >>> # ID Engine API http://www.boldsystems.org/index.php/resources/api?type=idengine
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
