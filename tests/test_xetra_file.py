import unittest
from tools.inspect_xetra_file import inspect,json_records
class TestXetra(unittest.TestCase):
 def test_array(self):
    r=json_records('[{"isin":"FR0010524777","venue":"XETA"},{"isin":"OTHER"}]')
    found,keys=inspect(r)
    self.assertEqual(found["FR0010524777"],1)
    self.assertEqual(keys["FR0010524777"],["isin","venue"])
 def test_lines(self):
    r=json_records('{"isin":"FR0010524777"}\n{"isin":"LU0321465469"}\n')
    found,_=inspect(r)
    self.assertEqual(sum(found.values()),2)
 def test_no_match(self):
    found,_=inspect([{"isin":"OTHER"}])
    self.assertEqual(sum(found.values()),0)
if __name__=="__main__":unittest.main()
