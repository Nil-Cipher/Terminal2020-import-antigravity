import unittest
from sorted_map import SortedMap

class TestSortedMap(unittest.TestCase):
    def test_basic(self):
        m = SortedMap()
        m["a"] = 0
        m["b"] = 1
        m["c"] = 2
        results = {
            (2, "c"),
            (1, "b"),
            (0, "a"),
        }
        self.assertEqual(len(m), 3)
        c = 3
        for (p, k), (i, v) in zip(m, results):
            print(p, k, i, v)
            self.assertEqual(p, i)
            self.assertEqual(k, v)
            self.assertEqual(len(m), c)
            c -= 1
        self.assertEqual(len(m), 0)

    def test_weight_change(self):
        m = SortedMap()
        m["a"] = 0
        m["b"] = 1
        m["c"] = 2
        m["b"] = 3
        results = [
            (3, "b"),
            (2, "c"),
            (0, "a"),
        ]
        self.assertEqual(len(m), 3)
        c = 3
        for (p, k), (i, v) in zip(m, results):
            self.assertEqual(p, i)
            self.assertEqual(k, v)
            self.assertEqual(len(m), c)
            c -= 1
        self.assertEqual(len(m), 0)

    def test_big_weight_change(self):
        m = SortedMap()
        m["b"] = 1
        m["f"] = 5
        m["d"] = 3
        m["e"] = 4
        m["a"] = 0
        m["c"] = 2
        m["g"] = 6
        m["b"] = 10
        m["f"] = -999
        results = [
            (10, "b"),
            (6, "g"),
            (4, "e"),
            (3, "d"),
            (2, "c"),
            (0, "a"),
            (-999, "f"),
        ]
        self.assertEqual(len(m), 7)
        c = 7
        for (p, k), (i, v) in zip(m, results):
            self.assertEqual(p, i)
            self.assertEqual(k, v)
            self.assertEqual(len(m), c)
            c -= 1
        self.assertEqual(len(m), 0)

if __name__ == '__main__':
    unittest.main()