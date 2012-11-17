import unittest

class Tests(unittest.TestCase):
    def test_location_macros(self):
        import streamer
        r = streamer.lookup_location_query_macro('usa')
        self.assertIsNotNone(r)
        usa_bbox = [-124.848974,24.396308,-66.885444,49.384358]
        for i, x in enumerate(r):
            self.assertAlmostEqual(x, usa_bbox[i], 5)
        r = streamer.lookup_location_query_macro('bogus')
        self.assertIsNone(r)
        r = streamer.lookup_location_query_macro('contintental_usa')
        self.assertIsNotNone(r)
        self.assertIsInstance(r, list)
        self.assertListEqual(r, streamer.lookup_location_query_macro('usa'))
                    
if __name__ == '__main__':
    unittest.main()