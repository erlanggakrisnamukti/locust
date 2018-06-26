import logging
from locust.test.testcases import LocustTestCase

logger = logging.getLogger(__name__)

class Assertion(LocustTestCase):

    def __init__(self, response):
        self.res = response
    
    def status_code_200(self):
        if self.res.status_code == 200:
            return True
        else:
            return False
    
    def status_code_equal(self, sc):
        if self.res.status_code == sc:
            return True
        else:
            return False

    def custom_assert(self, fname, *args, **kwargs):
        try:
            result = fname(*args, **kwargs)
            return result
        except Exception, e:
            logger.info(e)
            return False

    def assert_false(self, expr, msg=None):
        """Check that the expression is true."""
        try:
            self.assertFalse(expr, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True
    
    def assert_true(self, expr, msg=None):
        """Check that the expression is true."""
        try:
            self.assertTrue(expr, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True
    
    def assert_almost_equal(self, expr, msg=None):
        try:
            self.assertAlmostEqual(expr, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True

    def assert_in(self, member, container, msg=None):
        try:
            self.assertIn(member, container, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True
    
    def assert_less(self, a, b, msg=None):
        try:
            self.assertLess(a, b, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True

    def assert_less_equal(self, a, b, msg=None):
        try:
            self.assertLessEqual(a, b, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True

    def assert_greater(self, a, b, msg=None):
        try:
            self.assertGreater(a, b, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True

    def assert_greater_equal(self, a, b, msg=None):
        try:
            self.assertGreaterEqual(a, b, msg)
        except Exception, e:
            logger.info(e)
            return False
        else:
            logger.info("report sent")
            return True