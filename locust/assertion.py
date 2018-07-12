import logging, time
from locust.test.testcases import LocustTestCase
from test_object import TestStep
from . import runners

logger = logging.getLogger(__name__)

def decorate_assertion(func):
    def wrapper(self, *args, **kwargs):
        self.report_test_step = TestStep()
        self.report_test_step.time_start = time.time()
        self.report_test_step.response = self.res
        status, name, error = func(self, *args, **kwargs)
        self.report_test_step.status = status
        self.report_test_step.name = name
        self.report_test_step.reason = error
        self.report_test_step.test_case_id = runners.test_case.id
        self.report_test_step.time_end = time.time()
        return self.report_test_step
    return wrapper

class Assertion:
    def __init__(self, response):
        self.this = self.ActualObject
        self.this.res = response
        self.res = response

    @decorate_assertion
    def custom_assert(self, name, fname, *args, **kwargs):
        """custom function in user code hammertime"""
        status = None
        error = ""
        try:
            status = fname(*args, **kwargs)
        except Exception, e:
            status = False
            error = e
        return status, name, error

    class ActualObject(LocustTestCase):
        def __init__(self, name, actualObj):
            self.actualObj = actualObj
            self.name = name

        @decorate_assertion
        def equal_to(self, sc):
            """check status code based on given code"""
            status = None
            name = None
            error = ""
            if self.actualObj == sc:
                status = True
                name = "expect " + self.name + " " + str(self.actualObj) + " is equal to " + str(sc)
            else:
                status = False
                name = "expect " + self.name + " " + str(self.actualObj) + " is not equal to " + str(sc)
                error = str(self.actualObj) + " is not equal to " + str(sc) 
            return status, name, error
    
        @decorate_assertion
        def status_200(self):
            """check status code 200"""
            status = None
            name = None
            error = ""
            if self.res.status_code == 200:
                status = True
                name = "expect " + self.name + str(self.actualObj) + " is 200"
            else:
                status = False
                name = "expect " + self.name + " " + str(self.actualObj) + " is not 200"
                error = str(self.actualObj) + " is not 200"
            return status, name, error

        @decorate_assertion
        def is_false(self, msg=None):
            """Check that the expression is true."""
            status = None
            name = None
            error = ""
            try:
                self.assertFalse(self.actualObj, msg)
            except Exception, e:
                status = False
                name = "expect " + self.name + " is not false"
                error = e
            else:
                status = True
                name = "expect " + self.name + " is false"
            return status, name, error
                
        @decorate_assertion
        def is_true(self, msg=None):
            """Check that the expression is true."""
            status = None
            name = None
            error = ""
            try:
                self.assertTrue(self.actualObj, msg)
            except Exception, e:
                status = False
                name = "expect " + self.name + " is not true"
                error = e
            else:
                status = True
                name = "expect " + self.name + " is true"
            return status, name, error

        @decorate_assertion
        def contain(self, member, msg=None):
            """check object contain member"""
            status = None
            name = None
            error = ""
            try:
                self.assertIn(member, self.actualObj, msg)
            except Exception, e:
                status = False
                name = "expect " + self.name + " is not contain " + str(member)
                error = e
            else:
                status = True
                name = "expect " + self.name + " is contain " + str(member)
            return status, name, error
        
        @decorate_assertion
        def less_than(self, b, msg=None):
            """less than assertion, ex : a<b"""
            status = None
            name = None
            error = ""
            try:
                self.assertLess(self.actualObj, b, msg)
            except Exception, e:
                status = False
                name = "expect " + self.name + " is not less than " + str(b)
                error = e
            else:
                status = True
                name = "expect " + self.name + " is less than " + str(b)
            return status, name, error

        @decorate_assertion
        def lessEqualThan(self, b, msg=None):
            """less equal than assertion, ex : a<=b"""
            status = None
            name = None
            error = ""
            try:
                self.assertLessEqual(self.actualObj, b, msg)
            except Exception, e:
                status = False
                name = "expect " + self.name + " is not less equal than " + str(b)
                error = e
            else:
                status = True
                name = "expect " + self.name + " is less equal than " + str(b)
            return status, name, error

        @decorate_assertion
        def greaterThan(self, b, msg=None):
            """greater than assertion, ex : a>b"""
            status = None
            name = None
            error = ""
            try:
                self.assertGreater(self.actualObj, b, msg)
            except Exception, e:
                status = False
                name = "expect " + self.name + " is not greater than " + str(b)
                error = e
            else:
                status = True
                name = "expect " + self.name + " is greater than " + str(b)
            return status, name, error

        @decorate_assertion
        def greaterEqualThan(self, b, msg=None):
            """greater equal than assertion, ex : a>=b"""
            status = None
            name = None
            error = ""
            try:
                self.assertGreaterEqual(self.actualObj, b, msg)
            except Exception, e:
                status = False
                name = "expect " + self.name + " is not greater equal than " + str(b)
                error = e
            else:
                status = True
                name = "expect " + self.name + " is greater equal than " + str(b)
            return status, name, error