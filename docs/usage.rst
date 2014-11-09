========
Usage
========

To use BOLD retriever in a project::

    >>> import bold
    >>> seq = 'ATACGCTAGTGCATACTA'
    >>> r = bold.id(seq, db='COX1')
    >>> r.bold_id
    'JSDPX043-08'
    >>> r.taxonomicidentification
    'Hymenopenaeus debilis'

