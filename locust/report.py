import logging

logger = logging.getLogger(__name__)

class ReportHandler(object):

    def __init__(self):
        self.test_suites = dict()
        self._options = dict()
        self.acceptable_options = ["locustfile","repetition"]
    
    def get_test_suite(self, id):
        try:
            return self.test_suites[id]
        except Exception as e:
            logger.error("Can't get test suite with id %s : %s", id, e)
        return None

    def set_test_suite(self, test_suite):
        try:
            self.test_suites[test_suite.id] = test_suite
        except Exception as e:
            logger.error("Can't set test suite : %s",e)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        for x in self.acceptable_options:
            self._options[x] = getattr(value, x)

class TestSuiteSummary(object):
    def __init__(self):
        self.test_suites = []
        self.total_pass = 0
        self.total_fail = 0
        self.total_warning = 0

    @property
    def test_suites(self):
        return self.test_suites

    def append_test_suite(self, test_suite):
        self.test_suites.append(test_suite)

    @property
    def total_fail(self):
        return self.total_fail
    
    @total_fail.setter
    def total_fail(self, value):
        self.total_fail = value
    
    @property
    def total_pass(self):
        return self.total_pass
    
    @total_pass.setter
    def total_pass(self, value):
        self.total_pass = value

    @property
    def total_warning(self):
        return self.total_warning
    
    @total_warning.setter
    def total_warning(self, value):
        self.total_warning = value
    

class TestCaseSummary(object):
    def __init__(self):
        self.test_cases = []
        self.repetition = 0
        self.total_fail = 0
        self.total_pass = 0
        self.status = None
        self.total_duration = 0
        self.test_steps = []
    
    @property
    def test_cases(self):
        return self.test_cases

    def append_test_case(self, test_case):
        self.test_cases.append(test_case)

    @property
    def test_steps(self):
        return self.test_steps
    
    def append_test_step(self, test_step):
        self.test_steps.append(test_step)
    
    @property
    def repetition(self):
        return self.repetition

    @repetition.setter
    def repetition(self, value):
        self.repetition = value
    
    @property
    def total_fail(self):
        return self.total_fail
    
    @total_fail.setter
    def total_fail(self, value):
        self.total_fail = value
    
    @property
    def total_pass(self):
        return self.total_pass
    
    @total_pass.setter
    def total_pass(self, value):
        self.total_pass = value

    @property
    def status(self):
        return self.status

    @status.setter
    def status(self, value):
        self.status = value

    @property
    def total_duration(self):
        return self.total_duration
    
    @total_pass.setter
    def total_duration(self, value):
        self.total_duration = value


class TestStepSummary(object):
    def __init__(self):
        self.test_steps = []
        self.repetition = 0
        self.total_fail = 0
        self.total_pass = 0
        self.status = None
        self.total_duration = 0

    @property
    def test_steps(self):
        return self.test_steps
    
    def append_test_step(self, test_step):
        self.test_steps.append(test_step)
    
    @property
    def repetition(self):
        return self.repetition

    @repetition.setter
    def repetition(self, value):
        self.repetition = value
    
    @property
    def total_fail(self):
        return self.total_fail
    
    @total_fail.setter
    def total_fail(self, value):
        self.total_fail = value
    
    @property
    def total_pass(self):
        return self.total_pass
    
    @total_pass.setter
    def total_pass(self, value):
        self.total_pass = value

    @property
    def status(self):
        return self.status

    @status.setter
    def status(self, value):
        self.status = value

    @property
    def total_duration(self):
        return self.total_duration
    
    @total_pass.setter
    def total_duration(self, value):
        self.total_duration = value


report = ReportHandler()