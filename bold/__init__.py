# -*- coding: utf-8 -*-

__author__ = 'Carlos Pena'
__email__ = 'mycalesis@gmail.com'
__version__ = '0.0.1'

import logging

from .api import call_id
from .api import call_taxon_search
from .api import call_taxon_data
from .api import call_specimen_data
from .api import call_sequence_data
from .api import call_full_data
from .api import call_trace_files


logging.basicConfig(format='[bold module]:%(levelname)s:%(message)s', level=logging.DEBUG)
