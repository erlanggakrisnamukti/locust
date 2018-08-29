from test_object import TestSuite, TestCase, TestStep, TestStatus
from .log import console_logger
import random, time, logging

logger = logging.getLogger(__name__)

class Color():
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREY = '\033[38;5;246m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Mark():
    CHECK_MARK = u'\u2714'
    CROSS_MARK = u'\u2715'
    EXCLAMATION_MARK = u'\u01c3'

class ReportHandler(object):

    def __init__(self):
        self.test_suites = dict()
        self._options = dict()
        self.acceptable_options = ["locustfile","repetition"]
        self.total_success = 0
        self.total_fail = 0
        self.total_warning = 0
        self.total_duration = 0
        self.test_suites_summary = dict()
    
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
    
    def append_test_suite_summary(self, test_suite_summary):
        try:
            self.test_suites_summary[test_suite_summary._id] = test_suite_summary
        except Exception as e:
            logger.error("Can't append suite summary : %s",e)

    def set_dummy_data(self):
        self.test_suites = dict()
        for x in range (0,2):
            test_suite = TestSuite(name='TS-%s' % (random.randint(0,100)))
            for y in range (0,3):
                tc_name = 'TC-%s' % (random.randint(0,100))
                for m in range (0,2):
                    test_case = TestCase(name=tc_name,status=TestStatus.SUCCESS, group = y, repetition_index=m)
                    test_case = TestCase(name=tc_name, group = y, repetition_index=m)
                    status = TestStatus.SUCCESS
                    for z in range (0,5):
                        test_step = TestStep(name="TST-%s" % (z), status=TestStatus.SUCCESS)
                        message = None
                        if z > 2 :
                            if status != TestStatus.FAIL :
                                status = random.choice((TestStatus.SUCCESS,TestStatus.FAIL))
                            else :
                                message = str(random.randint(1000000,1000000000))
                        test_step = TestStep(name="TST-%s" % (z), status=status, message=message, dummy=True)
                        test_case.append_test_step(test_step)
                    test_case.auto_set_status()
                    test_suite.set_test_case(test_case)
                    time.sleep(0.2)
            self.set_test_suite(test_suite)
    
    def print_stats(self):
        color = Color()
        mark = Mark()

        console_logger.info("")
        console_logger.info(color.UNDERLINE + "REPORT:" +  color.END)
        console_logger.info("")
        for test_suite_id, test_suite_summary in self.test_suites_summary.iteritems():
            name_width = len(test_suite_summary.name)
            console_logger.info((color.BOLD + "%" + str(name_width+2) + "s" + color.END) % (test_suite_summary.name))
            for ts_id, test_case_summary in test_suite_summary.test_cases.iteritems():
                name_width = len(test_case_summary.name)
                text_color = None
                icon_status = None

                if test_case_summary.total_success == test_case_summary.repetition :
                    text_color = color.GREEN
                    icon_status = mark.CHECK_MARK
                elif test_case_summary.total_success == 0 :
                    text_color = color.RED
                    icon_status = mark.CROSS_MARK
                else :
                    text_color = color.YELLOW
                    icon_status = mark.EXCLAMATION_MARK

                console_logger.info((text_color + "%5s" + "%" + str(name_width+1) + "s" + " - %s/%s (%s secs)" + color.END ) % (icon_status, test_case_summary.name, test_case_summary.total_success, test_case_summary.repetition, round(test_case_summary.total_duration, 3)))
                if test_case_summary.reason:
                    name_width = len(test_case_summary.reason)
                    console_logger.info((color.GREY + "%" + str(name_width+8) + "s" + color.END) % (test_case_summary.reason))

            console_logger.info("")

        console_logger.info("")
        console_logger.info((color.GREEN + "Finished in %s secs" + color.END) % (round(report.total_duration, 3)))

        console_logger.info("")
        console_logger.info(color.UNDERLINE + "Summary:" + color.END)
        console_logger.info((color.GREEN + "%s %s tests completed" + color.END) % (mark.CHECK_MARK, report.total_success))
        console_logger.info((color.YELLOW + "%s %s tests warning" + color.END) % (mark.EXCLAMATION_MARK, report.total_warning))
        console_logger.info((color.RED + "%s %s tests failed" + color.END) % (mark.CROSS_MARK, report.total_fail))
        console_logger.info("")

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        for x in self.acceptable_options:
            self._options[x] = getattr(value, x)

    def compile_report(self):
        """Copy test suite, test case, and test step instance into summary instance 
        so it will be easier to access the datas needed for reports.

        Returns:
            dict -- test suites' summary
        """

        test_suites_summary = dict()
        for _,test_suite in self.test_suites.iteritems():
            test_suite_summary = TestSuiteSummary(test_suite=test_suite)
            test_case_summary_dict = dict()
            for _,test_case in test_suite.test_cases.iteritems():
                group = test_case.group
                if not group in test_case_summary_dict:
                    test_case_summary = TestCaseSummary()
                    test_case_summary_dict[group] = test_case_summary
                test_case_summary_dict[group].test_cases[test_case.repetition_index] = test_case
            test_suite_summary.test_cases = self.summarize_test_case(test_case_summary_dict)
            test_suites_summary[test_suite.id] = test_suite_summary

        for ts_id,test_suite_summary in test_suites_summary.iteritems():
            for group, test_case_summary in test_suite_summary.test_cases.iteritems():
                failure_reason = None
                highest_status = TestStatus.SUCCESS
                for x in range (0,len(test_case_summary.test_cases[0].test_steps)):
                    test_step_summary = TestStepSummary()
                    for y in range (0, test_case_summary.repetition):
                        test_step_summary.append_test_step(test_case_summary.test_cases[y].test_steps[x])
                    test_case_summary.append_test_step(self.summarize_test_step(test_step_summary))
                    if test_step_summary.status.value > highest_status.value :
                        highest_status = test_step_summary.status
                        failure_reason = "%s on step %s [%s]" % (highest_status.name,x,test_step_summary.name)
                test_case_summary.reason = failure_reason
                test_suite_summary.test_cases[group] = test_case_summary
            test_suites_summary[ts_id] = test_suite_summary

        for ts_id, test_suite_summary in test_suites_summary.iteritems():
            test_suites_summary[ts_id] = self.summarize_test_suite(test_suite_summary)
            self.summarize_all(test_suite_summary)
        self.test_suites_summary = test_suites_summary

    def summarize_all(self, test_suite_summary):
        """Sum up total duration, fail, success, and warning of the test.
        
        Arguments:
            test_suite_summary {dict} -- test suite's summary
        """

        self.total_duration += test_suite_summary.total_duration
        self.total_fail += test_suite_summary.total_fail
        self.total_success += test_suite_summary.total_success
        self.total_warning += test_suite_summary.total_warning
        self.append_test_suite_summary(test_suite_summary)

    def summarize_test_suite(self, test_suite_summary):
        """Sum up total success, fail, and warning of test case 
        and put it inside test suite summary attribute.
        
        Arguments:
            test_suite_summary {dict} -- test suite's summary
        
        Returns:
            dict -- test suite's summary
        """

        for _, test_case in test_suite_summary.test_cases.iteritems():
            test_suite_summary.total_duration += test_case.total_duration
            if test_case.status is TestStatus.SUCCESS:
                test_suite_summary.total_success += 1
            elif test_case.status is TestStatus.FAIL:
                test_suite_summary.total_fail += 1
            elif test_case.status is TestStatus.WARNING:
                test_suite_summary.total_warning += 1
        return test_suite_summary

    def summarize_test_case(self, test_case_summary_dict):
        """Determine test case's status, whether it is a success, fail or warning.
        Also sum up total fail and success of test cases.
        
        Arguments:
            test_case_summary_dict {dict} -- test case's summary
        
        Returns:
            dict -- test case's summary
        """

        for _, test_case_summary in test_case_summary_dict.iteritems():
            test_case_summary.repetition = len(test_case_summary.test_cases)
            test_case_summary.name = test_case_summary.test_cases[0].name
            for _, test_case in test_case_summary.test_cases.iteritems():
                test_case_summary.total_duration += test_case.time_end - test_case.time_start
                if(test_case.status is TestStatus.SUCCESS):
                    test_case_summary.total_success += 1
                elif(test_case.status is TestStatus.FAIL):
                    test_case_summary.total_fail += 1 
            if test_case_summary.total_success > 0 :
                if test_case_summary.total_success == test_case_summary.repetition :
                    test_case_summary.status = TestStatus.SUCCESS
                else :
                    test_case_summary.status = TestStatus.WARNING
            else :
                test_case_summary.status = TestStatus.FAIL
        return test_case_summary_dict
    
    def summarize_test_step(self, test_step_summary):
        """Determine a test step's status, whether it is a success, fail or warning.
        Since a test step can be repeated more than one time, it is needed to set
        a result conclusion from the repeated step. Usefull for test step's summary in reports.
        Also sum up total fail and success of test steps.
        
        Arguments:
            test_step_summary {dict} -- test step's summary
        
        Returns:
            dict -- test step's summary
        """

        test_step_summary.name = test_step_summary.test_steps[0].name
        for test_step in test_step_summary.test_steps:
            test_step_summary.total_duration = test_step.time_end - test_step.time_start
            if test_step.status is TestStatus.SUCCESS:
                test_step_summary.total_success += 1
            elif test_step.status is TestStatus.FAIL:
                test_step_summary.total_fail += 1
        if test_step_summary.total_success > 0 :
            if test_step_summary.total_success == len(test_step_summary.test_steps) :
                test_step_summary.status = TestStatus.SUCCESS
            else :
                test_step_summary.status = TestStatus.WARNING
        else :
            test_step_summary.status = TestStatus.FAIL
        return test_step_summary

class TestSuiteSummary(TestSuite):
    def __init__(self, *args, **kwargs):
        super(TestSuiteSummary, self).__init__(*args, **kwargs)
        if (kwargs.has_key('test_suite')):
            test_suite = kwargs.get('test_suite')
            self._name = test_suite.name
            self._path = test_suite.path
            self._id = test_suite.id
        self._test_cases = list()
        self.total_duration = 0
        self.total_fail = 0
        self.total_warning = 0
        self.total_success = 0

class TestCaseSummary(object):
    def __init__(self):
        self.test_cases = dict()
        self.repetition = 0
        self.total_fail = 0
        self.total_success = 0
        self.status = None
        self.total_duration = 0
        self.test_steps = []
        self.name = None
        self.reason = None

    def append_test_step(self, test_step):
        self.test_steps.append(test_step)

class TestStepSummary(object):
    def __init__(self):
        self.test_steps = []
        self.total_fail = 0
        self.total_success = 0
        self.status = None
        self.total_duration = 0
        self.name = None

    def append_test_step(self, test_step):
        self.test_steps.append(test_step)

report = ReportHandler()
