
from locust import events
from locust.runners import locust_runner, SLAVE_REPORT_INTERVAL, DistributedLocustRunner, STATE_HATCHING
from collections import deque
from locust.stats import StatsEntry, RequestStats
import math
import logging
import gevent
from . import runners

logger = logging.getLogger(__name__)

# The time window in seconds that current_percentile use data from
PERCENTILE_TIME_WINDOW = 15.0

# Are we running in distributed mode or not?
is_distributed = isinstance(locust_runner, DistributedLocustRunner)

response_times = deque([])

def on_request_success_ramping(**kwargs):
    '''logger.info('success ramping')'''
    response_time = kwargs.get('response_time', '')
    '''logger.info('{} : {}'.format('response time', response_time))'''
    if is_distributed:
        response_times.append(response_time)
    else:
        response_times.append(response_time)

        # remove from the queue
        rps = runners.locust_runner.stats.aggregated_stats("Total").current_rps
        current_users = runners.locust_runner.user_count
        '''logger.info('{} : {}'.format('rps', rps))'''
        '''logger.info('{} : {}'.format('users', current_users))'''
        if len(response_times) > rps*PERCENTILE_TIME_WINDOW:
            for i in range(len(response_times) - int(math.ceil(rps*PERCENTILE_TIME_WINDOW))):
                response_times.popleft()

def on_report_to_master_ramping(client_id, data):
    global response_times
    data["current_responses"] = response_times
    response_times = []

def on_slave_report_ramping(client_id, data):
    if "current_responses" in data:
        response_times.append(data["current_responses"])

    # remove from the queue
    slaves = locust_runner.slave_count
    response_times_per_slave_count = PERCENTILE_TIME_WINDOW/SLAVE_REPORT_INTERVAL
    if len(response_times) > slaves * response_times_per_slave_count:
        response_times.popleft()

def register_listeners():
    events.report_to_master += on_report_to_master_ramping
    events.slave_report += on_slave_report_ramping
    events.request_success += on_request_success_ramping

def remove_listeners():
    events.report_to_master.__isub__(on_report_to_master_ramping)
    events.slave_report.__isub__(on_slave_report_ramping)
    events.request_success.__isub__(on_request_success_ramping)

def current_percentile(percent):
    if is_distributed:
        # Flatten out the deque of lists and calculate the percentile to be returned
        return percentile(sorted([item for sublist in response_times for item in sublist]), percent)
    else:
        return percentile(sorted(response_times), percent)

def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return 0
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def start_ramping(hatch_rate=None, max_locusts=1000, hatch_stride=100,
          percent=0.95, response_time_limit=2000, acceptable_fail=0.05,
          precision=200, start_count=0, calibration_time=15):
    
    locust_runner.running_type = runners.RAMP

    register_listeners()
    
    def ramp_up(clients, hatch_stride, boundery_found=False):
        while True:
            if locust_runner.state != STATE_HATCHING:
                if locust_runner.num_clients >= max_locusts:
                    logger.info("Ramp up halted; Max locusts limit reached: %d" % max_locusts)
                    return ramp_down(clients, hatch_stride)

                gevent.sleep(calibration_time)
                fail_ratio = runners.locust_runner.stats.aggregated_stats("Total").fail_ratio
                if fail_ratio > acceptable_fail:
                    logger.info("Ramp up halted; Acceptable fail ratio %d%% exceeded with fail ratio %d%%" % (acceptable_fail*100, fail_ratio*100))
                    return ramp_down(clients, hatch_stride)

                p = current_percentile(percent)
                if p >= response_time_limit:
                    logger.info("Ramp up halted; Percentile response times getting high: %d" % p)
                    return ramp_down(clients, hatch_stride)

                if boundery_found and hatch_stride <= precision:
                    logger.info("Sweet spot found! Ramping stopped at %i locusts" % (locust_runner.num_clients))
                    return remove_listeners()

                logger.info("Ramping up...")
                if boundery_found:
                    hatch_stride = max((hatch_stride/2),precision)
                clients += hatch_stride
                locust_runner.start_hatching(clients, locust_runner.hatch_rate)
            gevent.sleep(1)

    def ramp_down(clients, hatch_stride):
        while True:
            if locust_runner.state != STATE_HATCHING:
                if locust_runner.num_clients < max_locusts:
                    gevent.sleep(calibration_time)
                    fail_ratio = runners.locust_runner.stats.aggregated_stats("Total").fail_ratio
                    if fail_ratio <= acceptable_fail:
                        p = current_percentile(percent)
                        if p <= response_time_limit:
                            if hatch_stride <= precision:
                                logger.info("Sweet spot found! Ramping stopped at %i locusts" % (locust_runner.num_clients))
                                return remove_listeners()

                            logger.info("Ramping up...")
                            hatch_stride = max((hatch_stride/2),precision)
                            clients += hatch_stride
                            locust_runner.start_hatching(clients, locust_runner.hatch_rate)
                            return ramp_up(clients, hatch_stride, True)

                logger.info("Ramping down...")
                hatch_stride = max((hatch_stride/2),precision)
                clients -= hatch_stride
                if clients > 0:
                    locust_runner.start_hatching(clients, locust_runner.hatch_rate)
                else:
                    logger.warning("No responses met the ramping thresholds, check your ramp configuration, locustfile and \"--host\" address")
                    logger.info("RAMPING STOPPED")
                    return remove_listeners()
            gevent.sleep(1)

    if hatch_rate:
        locust_runner.hatch_rate = hatch_rate
    if start_count > 0:
        locust_runner.start_hatching(start_count, hatch_rate)
    logger.info("RAMPING STARTED")
    ramp_up(start_count, hatch_stride)