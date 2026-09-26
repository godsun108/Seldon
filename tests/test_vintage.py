import unittest
from seldon.vintage import VintagePoint,as_known,fingerprint
class TestVintage(unittest.TestCase):
 def test_revision_cannot_leak_backward(self):
  p=[VintagePoint(1,10,2.0,"GDP"),VintagePoint(1,20,3.0,"GDP")]
  self.assertEqual(as_known(p,15)[("GDP",1)].value,2.0)
  self.assertEqual(as_known(p,25)[("GDP",1)].value,3.0)
 def test_future_release_hidden(self):
  p=[VintagePoint(1,20,3.0,"GDP")]
  self.assertEqual(as_known(p,19),{})
 def test_fingerprint_stable_order(self):
  a=VintagePoint(1,2,3.0,"X"); b=VintagePoint(2,3,4.0,"X")
  self.assertEqual(fingerprint([a,b]),fingerprint([b,a]))
if __name__=="__main__": unittest.main()
