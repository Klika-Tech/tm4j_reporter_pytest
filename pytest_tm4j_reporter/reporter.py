from copy import deepcopy
from datetime import datetime
from itertools import chain
from json import load
from os import environ
from re import match
from typing import Union

import pytest
from _pytest.config import Config
from pytest_jsonreport.plugin import JSONReport
from tm4j_reporter_api.tm4j_api.tm4j_api import create_test_execution_result, create_test_cycle, configure_tm4j_api


class TM4JReporter:
    def __init__(self, config: Union[Config, None] = None):
        self._config = config
        self.prefix_test = 'T'
        self.project_prefix = None
        self.api_key = None
        self.testcycle_key = None
        self.report = None
        self.testcycle_prefix = None
        self.testcycle_description = ''
        self.project_webui_host = None
        self.result_mapping = None

    def _param_validation(self):
        if self.result_mapping:
            allowed = ['tm4j-default', 'pytest']
            assert self.result_mapping in allowed, f'tm4j_result_mapping param value unknown: {self.result_mapping}'

    def _load_config_params(self, config: Config):
        """
        Load config params from pytest.ini to TM4JReporter obj attributes
        The sys env variables with the same name override the ones from pytest.ini
        :param config: config pytest object
        """
        mandatory_param_list = [
            'tm4j_project_prefix',
            ]
        if not self._config.option.tm4j_no_publish:
            mandatory_param_list.append('tm4j_api_key')

        optional_param_list = ['tm4j_testcycle_key',
                               'tm4j_project_webui_host',
                               'tm4j_testcycle_prefix',
                               'tm4j_testcycle_description',
                               'tm4j_result_mapping',
                               ]

        mandatory_absent = []
        for param in chain(mandatory_param_list, optional_param_list):
            attr = param.split('tm4j_')[-1]  # strip tm4j_ prefix
            if param in environ.keys():
                value = environ[param]
            else:
                value = config.getini(param)  # '' if not found

            if not value and param in mandatory_param_list:
                mandatory_absent.append(param)
            setattr(self, attr, value)

        self._param_validation()

        if mandatory_absent:
            raise AssertionError(f"The following mandatory parameters not found in config or in sys env vars:\n"
                                 f"{', '.join(mandatory_absent)}\n"
                                 f"See README for list of parameters and their descriptions")

    def pytest_configure(self, config: Config):
        if not hasattr(config, '_tm4j_report'):
            self._config._tm4j_report = self

        self._load_config_params(config)

        # Activate json-report plugin for report generation
        plugin = JSONReport(config)
        config._json_report = plugin
        config.pluginmanager.register(plugin)

    def pytest_json_modifyreport(self, json_report: dict):
        """
        The hook belongs to json-report plugin
        Rewrites an original report
        """
        json_report_orig = deepcopy(json_report)
        for key in json_report_orig.keys():
            del json_report[key]
        json_report['tests'] = self.prepare_tm4j_report_json(json_report_orig)
        self.report = {'tests': json_report['tests']}

    @staticmethod
    def pytest_json_runtest_metadata(item, call) -> dict:
        """
        The hook belongs to json-report plugin
        Reads the metadata from the test body and writes it to the report
        """

        if call.when == 'teardown':
            metadata = {}
            # metaproperties have format "property_name": default value
            meta_properties = {"steps": [], "comment": ""}
            for meta_property, default_value in meta_properties.items():
                if hasattr(item, meta_property):
                    metadata[meta_property] = getattr(item, meta_property)
                else:
                    metadata[meta_property] = default_value
            return metadata

    @staticmethod
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
                self.comment = None

            def step(self, text: str):
                self.steps.append(text)

        m = MetaHolder()
        yield m
        request.node.steps = m.steps
        request.node.comment = m.comment
        return m

    def _resolve_outcome(self, outcome: str) -> str:
        """
        Map pytest test outcome to tm4j outcome
        """
        # A key is for pytest, value is for TM4J
        outcomes_base = {
            'passed': 'Pass',
            'failed': 'Fail'}

        outcomes_tm4j_default = outcomes_base.copy()
        outcomes_tm4j_default.update({
                'skipped': 'Not executed',
                'xfailed': 'Pass',
                'xpassed': 'Fail'})

        outcomes_pytest = outcomes_base.copy()
        outcomes_pytest.update({
            'skipped': 'Skip',
            'xfailed': 'xFail',
            'xpassed': 'xPass'})

        if self.result_mapping == 'tm4j-default':
            outcomes = outcomes_tm4j_default
        elif self.result_mapping == 'pytest':
            outcomes = outcomes_pytest
        else:
            raise AssertionError(f'unknown mapping scheme: {self.result_mapping}')

        try:
            tm4j_outcome = outcomes[outcome]
        except KeyError:
            raise AssertionError(f'unknown pytest outcome: {outcome}')
        return tm4j_outcome

    def prepare_tm4j_report_json(self, pytest_json: dict) -> dict:
        """
        Prepares the data for report
        Example output:

        {'T303': {'name': 'one', 'outcome': 'Pass',
                  'steps': ['test one step A', 'test one step B'],
                  'comment': 'test one comment'},
         'T304': {'name': 'two', 'outcome': 'Pass',
                  'steps': ['test two step A', 'test two step B'],
                  'comment': 'test two comment'}}

        :type pytest_json: dict generated by the json-report plugin
        """
        report = pytest_json
        results = {}
        tests_wo_tm4j_id = []

        for test_dict in report['tests']:
            test_name_full = test_dict['nodeid']
            # test_common.py::test_T303_one
            test_name_wo_module = test_name_full.split('::')[-1]
            # test_T303_one

            tm4j_num_ptrn = f'{self.prefix_test}' + r'\d+'
            t_name_ptrn = '.*'
            is_test_valid_tm4j = match(
                f'^.*_({tm4j_num_ptrn})_({t_name_ptrn})', test_name_wo_module)
            if not is_test_valid_tm4j:
                tests_wo_tm4j_id.append(test_name_full)
                continue
            tm4j_num = is_test_valid_tm4j.group(1)
            test_name = is_test_valid_tm4j.group(2)

            results[tm4j_num] = {
                'name': test_name,
                'outcome': self._resolve_outcome(test_dict['outcome'])}

            # append to comments: crash info
            if 'crash' in test_dict['call']:
                crash = test_dict['call']['crash']
                crash_msg = f"crash info:<br>" \
                            f"path: {crash['path']}<br>" \
                            f"lineno: {crash['lineno']}<br>" \
                            f"message: {crash['message']}<br>"
                if test_dict['metadata']['comment'] is not None:
                    test_dict['metadata']['comment'] += f'<br><br>{crash_msg}'
                else:
                    test_dict['metadata']['comment'] = crash_msg

            results[tm4j_num].update(test_dict['metadata'])

        if tests_wo_tm4j_id:
            print(f"\n\n[TM4J] WARNING: some test results cannot be exported to TM4J "
                  f"because they don't have a TM4J test ID in their name."
                  f"\nexample: \"test_{self.prefix_test}123_testname\" "
                  f"where {self.prefix_test}123 is a TM4J test ID"
                  f"\ntests affected: {' '.join(tests_wo_tm4j_id)}")

        return results

    @staticmethod
    def _report_load_from_file(path: str = './.report.json') -> dict:
        """
        :param path: full path to json-file
        :return: dictionary
        """
        with open(path) as report_obj:
            return load(report_obj)

    def report_publish(self, external_source: Union[None, str] = None):
        """
        Publish a report to TM4J. creates a new test cycle if not found in pytest.ini
        :param external_source: load from json-file if path specified
        """
        if external_source is None:
            report = self._report_load_from_file()
        else:
            report = self.report

        configure_tm4j_api(self.api_key, self.project_prefix)

        if not self.testcycle_key:
            print('[TM4J] Creating a new test cycle...')
            timestamp = datetime.now().utcnow().strftime('%d-%b-%Y %H:%M:%S UTC')
            # e.g. 19-Jul-2020 19:33:00 UTC
            tcycle_name = f'{self.testcycle_prefix} {timestamp}'

            if self.testcycle_description:
                tcycle_key_full = create_test_cycle(tcycle_name, description=self.testcycle_description)
            else:
                tcycle_key_full = create_test_cycle(tcycle_name)

            # e.g. tcycle_key_full: QT-R64
            self.testcycle_key = tcycle_key_full.split('-')[-1]
            # e.g. self.testcycle_key: R64
            print(f'[TM4J] Created a new test cycle: key={tcycle_key_full}, name="{tcycle_name}"')
            if self.testcycle_description:
                print(f'[TM4J] Test cycle description: {self.testcycle_description}')
        else:
            tcycle_key_full = f'{self.project_prefix}-{self.testcycle_key}'
            print(f'[TM4J] Using existing test cycle: key={tcycle_key_full}')

        for tkey, item in report['tests'].items():
            execution_status = item['outcome']
            tcase_key_full = f"{self.project_prefix}-{tkey}"
            create_test_execution_result(
                test_cycle_key=tcycle_key_full,
                test_case_key=tcase_key_full,
                execution_status=execution_status,
                comment=item["comment"])
            # todo: make create_test_execution_result() return result - need to change API client for this
        print(f'[TM4J] Report published. Project: {self.project_prefix}. Test cycle key: {self.testcycle_key}')

        jira_plugin_url = 'com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page'
        if self.project_webui_host != '':
            print(f'[TM4J] Test cycle URL: https://{self.project_webui_host}/projects/{self.project_prefix}?'
                  f'selectedItem={jira_plugin_url}#!/testCycle/{tcycle_key_full}')

    def pytest_unconfigure(self, config: Config):
        assert isinstance(config, Config)  # "config" object is not used, but required for the pytest hook
        if config.option.tm4j_no_publish:
            print('[TM4J] Execution results publishing skipped')
            return
        self.report_publish()


def pytest_addoption(parser):
    group = parser.getgroup('tm4j', 'Reporting test results to TM4J')
    group.addoption('--tm4j', default=False, action='store_true', help='Report test results to TM4J')
    group.addoption('--tm4j-no-publish', default=False, action='store_true', help='Do not send results to TM4J')

    parser.addini('tm4j_project_prefix', 'TM4J project prefix without trailing dash (e.g. SWDEV)')
    parser.addini('tm4j_api_key', 'TM4J API key')
    parser.addini('tm4j_testcycle_key', 'TM4J existing test cycle key (e.g. R43)')

    tcycle_default = 'autoreport'
    tcycle_prefix_desc = f'TM4J test cycle prefix ("{tcycle_default}" ' \
                         f'makes "{tcycle_default} <14-Jul-2020 16:41:24 UTC>)"'
    parser.addini('tm4j_testcycle_prefix', tcycle_prefix_desc, default=tcycle_default)

    tcycle_desc_param = 'Description for the new test cycle. ' \
                        'A description for the existing test cycle won\'t be changed'
    parser.addini('tm4j_testcycle_description', tcycle_desc_param, default='')

    parser.addini('tm4j_project_webui_host', 'TM4J project webui host (e.g. klika-tech.atlassian.net)')

    result_mapping_desc = 'How to map test result - Pytest vs TM4J. tm4j-default (default) or pytest. see README'
    parser.addini('tm4j_result_mapping', result_mapping_desc, default='tm4j-default')


def pytest_configure(config: Config):
    # Activates the plugin if a --tm4j flag found in pytest cmdline
    if not config.option.tm4j:
        return
    plugin = TM4JReporter(config)
    config._tm4j_report = plugin
    config.pluginmanager.register(plugin)
