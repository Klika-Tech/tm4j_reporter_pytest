import re
from copy import deepcopy
import pytest


class TM4JReporter:
    @staticmethod
    def _resolve_outcome(outcome: str) -> str:
        """
        Map pytest test outcome to tm4j outcome
        """
        # A key is for pytest, value is for TM4J
        outcomes = {
            'passed': 'Pass',
            'failed': 'Fail'}
        return outcomes[outcome]

    def prepare_tm4j_report_json(self, pytest_json: dict) -> dict:
        """
        Takes original report from json-report plugin and fill with custom data
        """
        report = pytest_json
        results = {}

        for test_dict in report['tests']:
            test_name_full = test_dict['nodeid']
            # test_common.py::test_T303_one
            test_name_wo_module = test_name_full.split('::')[-1]
            # test_T303_one

            tm4j_num_ptrn = 'T\d+'
            t_name_ptrn = '.*'
            is_test_valid_tm4j = re.match(
                f'^.*_({tm4j_num_ptrn})_({t_name_ptrn})', test_name_wo_module)
            if not is_test_valid_tm4j:
                continue
            tm4j_num = is_test_valid_tm4j.group(1)
            test_name = is_test_valid_tm4j.group(2)

            results[tm4j_num] = {
                'name': test_name,
                'outcome': self._resolve_outcome(test_dict['outcome'])}
            results[tm4j_num].update(test_dict['metadata'])
        return results


def pytest_json_modifyreport(json_report):
    """
    The hook belongs to json-report plugin
    take original report and fill with custom data
    """
    json_report_orig = deepcopy(json_report)
    for key in json_report_orig.keys():
        del json_report[key]
    t = TM4JReporter()
    json_report['tests'] = t.prepare_tm4j_report_json(json_report_orig)


def pytest_json_runtest_metadata(item, call):
    """
    The hook belongs to json-report plugin
    push metadata from the test body into the report
    """
    if call.when == 'teardown':
        result = {}
        for step in range(len(item.meta_steps)):
            result[f'step_{step+1}'] = item.meta_steps[step]
        result['summary'] = item.meta_summary
        return result


@pytest.fixture
def tm4j_r(request):
    """
    TM4J-related metadata can be added to test using MetaHolder class

    def test_T303_one(tm4j_r):
        tm4j_r.summary = 'test one summary'
        tm4j_r.step('test one step A')
        tm4j_r.step('test one step B')
    """
    class MetaHolder:
        def __init__(self):
            self.steps = []
            self.summary = None

        def step(self, text: str):
            self.steps.append(text)

    m = MetaHolder()
    yield m
    request.node.meta_steps = m.steps
    request.node.meta_summary = m.summary
    return m
