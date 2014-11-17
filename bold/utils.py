# -*- coding: utf-8 -*-
from Bio._py3k import basestring


def _prepare_sequence(seq_record):
    """Outputs a DNA sequence as string.

    :param seq_record: Either sequence as string or sequence object
    :return: sequence as string
    """
    if isinstance(seq_record, basestring):
        return seq_record
    else:
        try:
            return str(seq_record.seq)
        except AttributeError:
            raise AttributeError("No valid sequence was found for %s." % seq_record)
