import time

class TestSuite(object):
    def __init__(self, **kwargs):
        self._id = 'TSU-'+int(time.time())
        self._name = kwargs.get('name', None)
        self._test_cases = kwargs.get('test_cases', [])
        self._path = kwargs.get('path', None)

    @property
    def get_test_cases(self):
        return self._test_cases

    @property
    def append_test_case(self, test_case):
        self._test_cases.append(test_case)


class TestCase(object):
    def __init__(self, **kwargs):
        self._id = 'TC-'+int(time.time())
        self._name = kwargs.get('name', None)
        self._test_steps = kwargs.get('test_steps', [])
        self._status = kwargs.get('status', None)
        self._time_start = kwargs.get('time_start', None)
        self._time_end = kwargs.get('time_end', None)

    @property
    def get_test_steps(self):
        return self._test_steps

    @property
    def append_test_step(self, test_step):
        self._test_steps.append(test_step)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def time_start(self):
        return self._time_start

    @time_start.setter
    def time_start(self, time_start):
        self._time_start = time_start

    @property
    def time_end(self):
        return self._time_end

    @time_end.setter
    def time_end(self, time_end):
        self._time_end = time_end


class TestStep(object):
    def __init__(self, **kwargs):
        self._id = 'TST-'+int(time.time())
        self._name = kwargs.get('name', None)
        self._status = kwargs.get('status', None)
        self._time_start = kwargs.get('time_start', None)
        self._time_end = kwargs.get('time_end', None)
        self._repetition_index = kwargs.get('repetition_index', None)
        self._request = kwargs.get('request', None)
        self._response = kwargs.get('response', None)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def time_start(self):
        return self._time_start

    @time_start.setter
    def time_start(self, time_start):
        self._time_start = time_start

    @property
    def time_end(self):
        return self._time_end

    @time_end.setter
    def time_end(self, time_end):
        self._time_end = time_end

    @property
    def repetition_index(self):
        return self._repetition_index

    @repetition_index.setter
    def repetition_index(self, index):
        self._repetition_index = index

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, request):
        self._request = request

   @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response