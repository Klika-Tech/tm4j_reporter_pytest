from copy import deepcopy
import pytest


class TM4JReporter:
    def __init__(self):
        self.test_prefix = 'test_'

    def _resolve_outcome(self, outcome):
        """
        map pytest test outcome to tm4j outcome
        """
        outcomes = {
            'passed': 'Pass',
            'failed': 'Fail'}
        return outcomes[outcome]

    def prepare_tm4j_report_json(self, pytest_json: dict) -> dict:
        report = pytest_json
        results = {}
        for test_dict in report['tests']:
            test_name_full = test_dict['nodeid']
            test_name_wo_module = test_dict['nodeid'].split('::')[-1]
            # play.py::test_T406_hello
            assert test_name_wo_module.startswith(self.test_prefix)
            test_name_w_tm4j_num = '_'.join(test_name_full.split('_')[1:])
            tm4j_num = test_name_w_tm4j_num.split('_')[0]
            test_name = '_'.join(test_name_w_tm4j_num.split('_')[1:])
            results[tm4j_num] = {
                'name': test_name,
                'outcome': self._resolve_outcome(test_dict['outcome'])}
            results[tm4j_num].update(test_dict['metadata'])
            # {
            #   "tests": {
            #     "T303": {
            #       "name": "one",
            #       "outcome": "Pass",
            #       "step_1": "test one step A",
            #       "step_2": "test one step B",
            #       "summary": "test one summary"
            #     },
            #     "T304": {
            #       "name": "two",
            #       "outcome": "Pass",
            #       "step_1": "test two step A",
            #       "step_2": "test two step B",
            #       "summary": "test two summary"
            #     }
            #   }
            # }
        return results


def pytest_json_modifyreport(json_report):
    json_report_orig = deepcopy(json_report)
    for key in json_report_orig.keys():
        del json_report[key]
    t = TM4JReporter()
    json_report['tests'] = t.prepare_tm4j_report_json(json_report_orig)
    assert True


def pytest_json_runtest_metadata(item, call):
    if call.when == 'teardown':
        result = {}
        for step in range(len(item.meta_steps)):
            result[f'step_{step+1}'] = item.meta_steps[step]
        result['summary'] = item.meta_summary
        return result


@pytest.fixture
def tm4j_r(request):

    class MetaHolder:
        def __init__(self):
            self.steps = []
            self.summary = None

        def step(self, text):
            self.steps.append(text)

    m = MetaHolder()

    yield m
    request.node.meta_steps = m.steps
    request.node.meta_summary = m.summary
    return m
