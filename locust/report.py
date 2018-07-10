import logging
from test_object import TestSuite, TestCase, TestStep, TestStatus
import random
logger = logging.getLogger(__name__)

class ReportHandler(object):

    def __init__(self):
        self.test_suites = dict()
        self._options = dict()
        self.acceptable_options = ["locustfile","repetition"]
        self.total_pass = None
        self.total_failure = None
        self.total_warning = None
        self.test_suite_summary = dict()
    
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

    def set_dummy_data(self):
        for x in range (0,2):
            test_suite = TestSuite(name='TS-%s' % (random.randint(0,100)))
            for y in range (0,3):
                tc_name = 'TC-%s' % (random.randint(0,100))
                for m in range (0,2):
                    test_case = TestCase(name=tc_name,status=TestStatus.SUCCESS, group = y, repetition_index=m)
                    for z in range (0,5):
                        test_step = TestStep(name="TST-%s" % (z), status=TestStatus.SUCCESS)
                        test_case.append_test_step(test_step)
                    test_suite.set_test_case(test_case)
            self.set_test_suite(test_suite)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        for x in self.acceptable_options:
            self._options[x] = getattr(value, x)

    def compile_report(self):
        test_suite_summary = dict()
        for _,test_suite in self.test_suites.iteritems():
            test_case_summary_list = dict()
            for _,test_case in test_suite.test_cases.iteritems():
                group = test_case.group
                if not group in test_case_summary_list:
                    test_case_summary = TestCaseSummary()
                    test_case_summary_list[group] = test_case_summary
                test_case_summary_list[group].test_cases[test_case.repetition_index] = test_case
                test_case_summary_list[group].repetition = len(test_case_summary_list[group].test_cases)
            test_suite_summary[test_suite.id] = test_case_summary_list

        for ts_id,test_case_summary_list in test_suite_summary.iteritems():
            for group, test_case_summary in test_case_summary_list.iteritems():
                for x in range (0,len(test_case_summary.test_cases[0].test_steps)):
                    test_step_summary = TestStepSummary()
                    for y in range (0, test_case_summary.repetition):
                        test_step_summary.append_test_step(test_case_summary.test_cases[y].test_steps[x])
                    test_case_summary.append_test_step(test_step_summary)
                test_case_summary_list[group] = test_case_summary
            test_suite_summary[ts_id] = test_case_summary_list
        self.test_suite_summary = test_suite_summary

report = ReportHandler()

class TestCaseSummary(object):
    def __init__(self):
        self.test_cases = dict()
        self.repetition = 0
        self.total_fail = 0
        self.total_pass = 0
        self.status = None
        self.total_duration = 0
        self.test_steps = []
  
    def append_test_step(self, test_step):
        self.test_steps.append(test_step)

class TestStepSummary(object):
    def __init__(self):
        self.test_steps = []
        self.repetition = 0
        self.total_fail = 0
        self.total_pass = 0
        self.status = None
        self.total_duration = 0

    
    def append_test_step(self, test_step):
        self.test_steps.append(test_step)
    
report.set_dummy_data()
report.compile_report()