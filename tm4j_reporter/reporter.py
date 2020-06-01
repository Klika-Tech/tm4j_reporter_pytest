from copy import deepcopy


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
        # {"T406": {"name": "hello", "outcome": "Pass"}}
        return results


def pytest_json_modifyreport(json_report):
    json_report_orig = deepcopy(json_report)
    for key in json_report_orig.keys():
        del json_report[key]
    t = TM4JReporter()
    json_report['tests'] = t.prepare_tm4j_report_json(json_report_orig)
