# -*- coding: utf-8 -*-
import unittest

import bold


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
        result = bold.call_taxon_search(taxonomic_identification, fuzzy=False)
        self.assertEqual(expected, result.tax_id)

        taxonomic_identification = 'Fabaceae'
        result = bold.call_taxon_search(taxonomic_identification, fuzzy=False)
        self.assertEqual('Plants', result.tax_division)
        self.assertEqual(187, result.parent_id)
        self.assertEqual('Fabales', result.parent_name)
        self.assertEqual('Fabaceae', result.taxon_rep)

    def tearDown(self):
        pass


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
