from jigna.api import View
from threading import Thread
import unittest
import time

from selenium import webdriver

# Local imports.
from test_jigna_qt import TestJignaQt, Person, body_html


class TestJignaWebSync(TestJignaQt):
    @classmethod
    def setUpClass(cls, port=8888, async=False):
        person_view = View(body_html=body_html, async=async)
        fred = Person(name='Fred', age=42)
        t = Thread(target=person_view.serve, kwargs=dict(port=port, model=fred))
        t.setDaemon(True)
        t.start()

        browser = webdriver.Firefox()
        browser.get('http://localhost:%d'%port)
        cls.person_view = person_view
        cls.fred = fred
        cls.browser = browser

    @classmethod
    def tearDownClass(cls):
        from tornado.ioloop import IOLoop
        cls.browser.quit()
        IOLoop.instance().stop()
        import time
        time.sleep(1)

    def setUp(self):
        cls = self.__class__
        self.person_view = cls.person_view
        self.browser = cls.browser
        self.fred = cls.fred
        self.fred.spouse = None
        self.fred.fruits = []
        self.fred.friends = []

    def execute_js(self, js):
        return self.browser.execute_script(js)

    def reset_user_var(self):
        self.execute_js("jigna.user = undefined;")

    def get_attribute(self, js, expect):
        self.reset_user_var()
        get_js = """jigna.get_attribute(\'%s\').done(function(result)
                                {jigna.user = result;})"""%js
        self.execute_js(get_js)

        check_js = "return jigna.user;"
        result = self.execute_js(check_js)
        count = 0
        while result is None and expect is not None and count < 10:
            time.sleep(0.1)
            result = self.execute_js(check_js)
            count += 1
        self.reset_user_var()
        return result

    def assertJSEqual(self, js, value):
        result = self.get_attribute(js, value)
        if isinstance(value, (list, tuple)):
            msg = "Lengths different: expected %d, got %d" % \
                (len(value), len(result))
            self.assertEqual(len(value), len(result), msg)
            for index in range(len(value)):
                expect = value[index]
                got = result[index]
                if got != expect:
                    got = self.get_attribute(js+"[%d]"%index, expect)
                msg = "%s[%s] != %s, got %s"%(js, index, expect, got)
                self.assertEqual(expect, got, msg)
        else:
            msg = "%s != %s, got %s"%(js, value, result)
            self.assertEqual(value, result, msg)

    def test_instance_trait(self):
        # Overridden to work with the web backend.
        self.assertJSEqual("jigna.models.model.spouse", None)
        wilma = Person(name='Wilma', age=40)
        self.fred.spouse = wilma
        self.get_attribute("jigna.models.model.spouse.name", "")
        self.assertJSEqual("jigna.models.model.spouse.name", 'Wilma')
        self.assertJSEqual("jigna.models.model.spouse.age", 40)

        # Set in the JS side.
        self.execute_js("jigna.models.model.spouse.name = 'Wilmaji'")
        self.execute_js("jigna.models.model.spouse.age = 41")
        self.assertEqual(wilma.name, "Wilmaji")
        self.assertEqual(wilma.age, 41)


# Delete this so running just this file does not run all the tests.
del TestJignaQt

if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
