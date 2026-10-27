import unittest
from osint99.domainintel import validate_domain

class DomainIntelTests(unittest.TestCase):
    def test_valid_domain(self):
        self.assertEqual(validate_domain("Example.COM."), "example.com")

    def test_rejects_url_and_path(self):
        for value in ("https://example.com", "example.com/path", "127.0.0.1", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_domain(value)

if __name__ == "__main__":
    unittest.main()
