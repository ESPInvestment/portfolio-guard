import unittest
from datetime import date
from tools.validate_provider_feed import read_manifest, validate

SAMPLE="""isin,price_type,provider_symbol,exchange,currency,verified,notes
FR0010524777,CLOSE,LYM9.DEX,XETRA,EUR,true,Test only
DE0009770206,NAV,ODDO_TEST,KVG,EUR,true,Test only
"""
def obs(isin="FR0010524777",date="2026-11-13",price="123.45",currency="EUR",price_type="CLOSE",symbol="LYM9.DEX",exchange="XETRA"):
    return dict(isin=isin,date=date,price=price,currency=currency,price_type=price_type,source="Test only",symbol=symbol,exchange=exchange)

class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.mapping=read_manifest(SAMPLE)
        self.day=date(2026,11,16)
    def test_valid(self):
        accepted,errors=validate([obs()],self.mapping,self.day)
        self.assertEqual(len(accepted),1);self.assertEqual(errors,[])
    def test_unverified_mapping_fails_closed(self):
        mapping=read_manifest(SAMPLE.replace("EUR,true,Test only","EUR,false,Test only"))
        accepted,errors=validate([obs()],mapping,self.day)
        self.assertEqual(len(accepted),0);self.assertTrue(errors)
    def test_price_type_currency_symbol_mismatch(self):
        for change in ({"price_type":"NAV"},{"currency":"USD"},{"symbol":"OTHER"},{"exchange":"OTHER"}):
            with self.subTest(change=change):
                accepted,errors=validate([obs(**change)],self.mapping,self.day)
                self.assertFalse(accepted);self.assertTrue(errors)
    def test_duplicate_future_negative(self):
        for batch in ([obs(),obs()],[obs(date="2099-01-01")],[obs(price="-1")]):
            accepted,errors=validate(batch,self.mapping,self.day)
            self.assertTrue(errors)
    def test_missing_fields(self):
        accepted,errors=validate([{"isin":"FR0010524777"}],self.mapping,self.day)
        self.assertFalse(accepted);self.assertTrue(errors)
    def test_nav(self):
        v=obs(isin="DE0009770206",symbol="ODDO_TEST",exchange="KVG",price_type="NAV")
        accepted,errors=validate([v],self.mapping,self.day)
        self.assertEqual(len(accepted),1);self.assertFalse(errors)

if __name__=="__main__":
    unittest.main()
