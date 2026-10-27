import unittest
from unittest.mock import patch
from osint99.collector import check_public_url, _SearchResults


class CollectorTests(unittest.TestCase):
    def test_invalid_url_rejected(self):
        with self.assertRaises(ValueError):
            check_public_url("")

    def test_search_parser_extracts_real_result_links(self):
        parser = _SearchResults()
        parser.feed('<a class="result__a" href="https://example.com">Example result</a>')
        self.assertEqual(parser.results[0]["title"], "Example result")
        self.assertEqual(parser.results[0]["url"], "https://example.com")

    @patch("osint99.collector.urlopen")
    def test_http_error_is_not_claimed_as_missing_account(self, mocked):
        from urllib.error import HTTPError
        mocked.side_effect = HTTPError("https://example.com", 403, "Forbidden", {}, None)
        result = check_public_url("https://example.com")
        self.assertEqual(result["result"], "http-error")
        self.assertEqual(result["status"], 403)
        self.assertIn("inconclusive", result["note"].lower())


if __name__ == "__main__":
    unittest.main()
