#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_bold
----------------------------------

Tests for `bold` module.
"""

import unittest

import bold


class TestApi(unittest.TestCase):

    def setUp(self):
        pass

    def test_call_id(self):
        seq = "TTTTTGGTATTTGAGCAGGAATAGTAGGAACTTCTCTCAGTTTAATTATTCGAATAGAATTAGGTAATCCAGGTTTCTTAATTGGAGATGATCAAATTTATAATACTATTGTAACAGCCCATGCTTTTATTATAATTTTTTTTATAGTTATACCTATTGTAATTGGAGGATTTGGAAATTGACTAGTTCCCCTAATATTAGGTGCACCTGATATAGCTTTCCCTCGTATAAATAATATAAGATATTGACTACTTCCACCATCTTTAATATTATTAATTTCAAGTAGTATTGTAGAAAATGGAGCTGGAACAGGTTGAACAGTTTACCCCCCTCTTTCCTCTAATATTGCTCATAGAGGAACCTCAGTAGACTTAGCAATTTTTTCTCTTCATTTAGCTGGTATTTCTTCTATTTTAGGAGCTATTAATTTTATTACTACAATTATTAATATACGAGTTAATGGAATATCCTATGATCAAATACCTTTATTTGTTTGAGCTGTTGGAATTACAGCTCTTCTTTTACTTCTTTCTTTACCTGTTTTAGCAGGAGCTATCACAATACTTCTTACAGATCGAAATTTAAATACATCATTTTTTGATCCTGCAGGAGGAGGTGATCCAATTTTATACCAACATTTATTTTGATTTTTTGGTCACCC"
        db = "COX1_SPECIES_PUBLIC"
        expected = "GBLN2781-10"
        res = bold.call_id(seq, db)
        result = res.id_from_bold
        self.assertEqual(expected, result)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()