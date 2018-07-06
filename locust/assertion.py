import logging, time
from locust.test.testcases import LocustTestCase
from test_object import TestStep

logger = logging.getLogger(__name__)

def decorate_assertion(func):
    def wrapper(self, *args, **kwargs):
        self.report_test_step = TestStep()
        self.report_test_step.time_start = time.time()
        self.report_test_step.response = self.res
        statusnameObj = func(self, *args, **kwargs)
        self.report_test_step.status = statusnameObj.status
        self.report_test_step.name = statusnameObj.name
        logger.info(statusnameObj.status)
        logger.info(statusnameObj.name)
        self.report_test_step.time_end = time.time()
        return self.report_test_step
    return wrapper

class StatusNameObj:
    def __init__(self, **kwargs):
        self._name = kwargs.get('name', None)
        self._status = kwargs.get('status', None)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

class Assertion:

    def __init__(self, response):
        self.this = self.ActualObject
        self.this.res = response
        self.res = response

    @decorate_assertion
    def custom_assert(self, name, fname, *args, **kwargs):
        """custom function in user code hammertime"""
        statusnameObj = StatusNameObj()
        try:
            statusnameObj.result = fname(*args, **kwargs)
        except Exception, e:
            logger.info(e)
            statusnameObj.result = False
        finally:
            statusnameObj.name = name
        return statusnameObj

    class ActualObject(LocustTestCase):
        def __init__(self, name, actualObj):
            self.actualObj = actualObj
            self.name = name

        @decorate_assertion
        def equal_to(self, sc):
            """check status code based on given code"""
            statusnameObj = StatusNameObj()
            if self.actualObj == sc:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is equal to " + str(sc)
            else:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not equal to " + str(sc)
            return statusnameObj
    
        @decorate_assertion
        def status_200(self):
            """check status code 200"""
            statusnameObj = StatusNameObj()
            if self.res.status_code == 200:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is 200"
            else:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not 200"
            return statusnameObj

        @decorate_assertion
        def is_false(self, msg=None):
            """Check that the expression is true."""
            statusnameObj = StatusNameObj()
            try:
                self.assertFalse(self.actualObj, msg)
            except Exception, e:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not false"
            else:
                logger.info("report is false sent")
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is false"
            return statusnameObj
                
        @decorate_assertion
        def is_true(self, msg=None):
            """Check that the expression is true."""
            statusnameObj = StatusNameObj()
            try:
                self.assertTrue(self.actualObj, msg)
            except Exception, e:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not true"
            else:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is true"
            return statusnameObj

        @decorate_assertion
        def contain(self, member, msg=None):
            """check object contain member"""
            statusnameObj = StatusNameObj()
            try:
                self.assertIn(member, self.actualObj, msg)
            except Exception, e:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not contain " + str(member)
            else:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is contain " + str(member)
            return statusnameObj
        
        @decorate_assertion
        def less_than(self, b, msg=None):
            """less than assertion, ex : a<b"""
            statusnameObj = StatusNameObj()
            try:
                self.assertLess(self.actualObj, b, msg)
            except Exception, e:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not less than " + str(b)
            else:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is less than " + str(b)
            return statusnameObj

        @decorate_assertion
        def lessEqualThan(self, b, msg=None):
            """less equal than assertion, ex : a<=b"""
            statusnameObj = StatusNameObj()
            try:
                self.assertLessEqual(self.actualObj, b, msg)
            except Exception, e:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not less equal than " + str(b)
            else:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is less equal than " + str(b)
            return statusnameObj

        @decorate_assertion
        def greaterThan(self, b, msg=None):
            """greater than assertion, ex : a>b"""
            statusnameObj = StatusNameObj()
            try:
                self.assertGreater(self.actualObj, b, msg)
            except Exception, e:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not greater than " + str(b)
            else:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is greater than " + str(b)
            return statusnameObj

        @decorate_assertion
        def greaterEqualThan(self, b, msg=None):
            """greater equal than assertion, ex : a>=b"""
            statusnameObj = StatusNameObj()
            try:
                self.assertGreaterEqual(self.actualObj, b, msg)
            except Exception, e:
                statusnameObj.status = False
                statusnameObj.name = "expect " + self.name + " is not greater equal than " + str(b)
            else:
                statusnameObj.status = True
                statusnameObj.name = "expect " + self.name + " is greater equal than " + str(b)
            return statusnameObj