import unittest
import identidock

class TestCase(unittest.TestCase):
    def setUp(self):
        identidock.app.config["TESTING"] = True
        self.app = identidock.app.test_client()

    def test_get_mainpage(self):
        page = self.app.post("/", data=dict(name="Moby Dick"))
        self.assertEqual(page.status_code, 200)
        self.assertIn('Hello', str(page.data))
        self.assertIn('Moby Dick', str(page.data))


    def test_html_escaping(self):
        page = self.app.post("/", data=dict(name="><b>TEST</b><!--"))
        self.assertNotIn('<b>', str(page.data))

if __name__ == '__main__':
    unittest.main()
