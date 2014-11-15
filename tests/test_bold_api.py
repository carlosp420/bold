# -*- coding: utf-8 -*-
import unittest

import bold
from bold import api


class TestApi(unittest.TestCase):

    def setUp(self):
        pass

    def test_call_id(self):
        seq = "TTTTTGGTATTTGAGCAGGAATAGTAGGAACTTCTCTCAGTTTAATTATTCGAATAGAATTAGGTAATCCAGGTTTCTTAATTGGAGATGATCAAATTTATAATACTATTGTAACAGCCCATGCTTTTATTATAATTTTTTTTATAGTTATACCTATTGTAATTGGAGGATTTGGAAATTGACTAGTTCCCCTAATATTAGGTGCACCTGATATAGCTTTCCCTCGTATAAATAATATAAGATATTGACTACTTCCACCATCTTTAATATTATTAATTTCAAGTAGTATTGTAGAAAATGGAGCTGGAACAGGTTGAACAGTTTACCCCCCTCTTTCCTCTAATATTGCTCATAGAGGAACCTCAGTAGACTTAGCAATTTTTTCTCTTCATTTAGCTGGTATTTCTTCTATTTTAGGAGCTATTAATTTTATTACTACAATTATTAATATACGAGTTAATGGAATATCCTATGATCAAATACCTTTATTTGTTTGAGCTGTTGGAATTACAGCTCTTCTTTTACTTCTTTCTTTACCTGTTTTAGCAGGAGCTATCACAATACTTCTTACAGATCGAAATTTAAATACATCATTTTTTGATCCTGCAGGAGGAGGTGATCCAATTTTATACCAACATTTATTTTGATTTTTTGGTCACCC"
        db = "COX1_SPECIES_PUBLIC"
        res = bold.call_id(seq, db)
        for item in res.items:
            if item['similarity'] == 1:
                self.assertEqual('Euptychia ordinata', item['taxonomic_identification'])

    def test_call_taxon_search(self):
        taxonomic_identification = 'Euptychia ordinata'
        expected = 302603
        res = bold.call_taxon_search(taxonomic_identification, fuzzy=False)
        item = res.items[0]
        self.assertEqual(expected, item['tax_id'])

        taxonomic_identification = 'Fabaceae'
        res = bold.call_taxon_search(taxonomic_identification, fuzzy=False)
        item = res.items[0]
        self.assertEqual('Plants', item['tax_division'])
        self.assertEqual(187, item['parent_id'])
        self.assertEqual('Fabales', item['parent_name'])
        self.assertEqual('Fabaceae', item['taxon_rep'])

    def test_call_taxon_data(self):
        tax_id = 302603
        # using default datatype='basic'
        res = bold.call_taxon_data(tax_id)
        item = res.items[0]
        self.assertEqual(7044, item['parent_id'])

    def test_parse_json(self):
        json_string = '{"302603":{"taxid":302603,"taxon":"Euptychia ordinata","tax_rank":"species","tax_division":"Animals","parentid":7044,"parentname":"Euptychia"}}'
        res = api.Response()
        res.parse_json(json_string)
        item = res.items[0]
        self.assertEqual(302603, item['tax_id'])
        self.assertEqual(7044, item['parent_id'])

        json_string = '{"taxid":891,"taxon":"Fabaceae","tax_rank":"family","tax_division":"Plants","parentid":187,"parentname":"Fabales","taxonrep":"Fabaceae"}'
        res = api.Response()
        res.parse_json(json_string)
        item = res.items[0]
        self.assertEqual('Fabaceae', item['taxon'])
        self.assertEqual('Plants', item['tax_division'])

    def tearDown(self):
        pass


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
