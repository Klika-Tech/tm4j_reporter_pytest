from configparser import ConfigParser
from json import load
from os import remove, path, environ
from pathlib import Path
from re import match
from subprocess import run
from typing import Union

from pytest import mark

report_fname = '.report.json'


def teardown_module():
    if path.isfile(report_fname):
        remove(report_fname)


def get_plugin_cfg(key: str) -> str:
    c = ConfigParser()
    c.read('./pytest.ini')
    return c['pytest'][key]


def run_test(exp_rc: int = 0, environment: Union[dict, None] = None, publish=True) -> str:
    """
    args: list of pytest cmdline arguments
    :param publish: publish results to TM4J
    :param exp_rc: expected return code
    :param environment: sys env vars
    """
    if path.isfile(report_fname):
        remove(report_fname)
    cmd = 'pytest --tm4j'.split()
    if not publish:
        cmd.append('--tm4j-no-publish')
    cmd.append('common/report_tests.py')
    new_env = environ.copy()
    plugin_location = Path.cwd().parent.as_posix()
    new_env['PYTHONPATH'] = plugin_location

    if environment:
        new_env.update(environment)

    cmd_run = run(cmd, capture_output=True, env=new_env)

    output = cmd_run.stdout.decode()
    err = cmd_run.stderr.decode()
    assert err == '', print(err)
    assert cmd_run.returncode == exp_rc, f'got stdout:\n{output}\ngot stderr:\n{err}'
    return output


def test_verify_output_json_structure():
    output = run_test(exp_rc=1, publish=False)
    print('CHECK: tests without a TM4J ID are listed as warning in stdout')
    expected_ptrn = 'tests affected:.*report_tests.py::test_withoutTm4jId_two'
    for line in output.split('\n'):
        if match(expected_ptrn, line):
            break
    else:
        raise AssertionError('a test without TM4J ID is not listed in warning message')

    with open('test_data/report.json') as orig_obj:
        orig = load(orig_obj)
    with open(report_fname) as rcvd_obj:
        rcvd = load(rcvd_obj)

    print('CHECK: JSON-output matches expected')
    assert orig == rcvd, f'result json does not match\n' \
                         f'original: {orig}\n' \
                         f'received: {rcvd}'


def test_publish_existing_testcycle():
    project_prefix = get_plugin_cfg('tm4j_project_prefix')
    tcycle_key = 'R40'
    env = {'tm4j_testcycle_key': tcycle_key}
    output = run_test(exp_rc=1, environment=env)
    print('CHECK: publish result reported')
    # no real check because the api client does not return result
    # todo: api client to return result
    expected = f'[TM4J] Using existing test cycle: key={project_prefix}-{tcycle_key}'
    assert expected in output, f'got: {output}'

    expected = f'[TM4J] Report published. Project: {project_prefix}. Test cycle key: {tcycle_key}'
    assert expected in output, f'got: {output}'


def test_publish_create_testcycle():
    project_prefix = get_plugin_cfg('tm4j_project_prefix')
    tcycle_desc = get_plugin_cfg('tm4j_testcycle_description')

    output = run_test(exp_rc=1)
    exp1 = '[TM4J] Created a new test cycle'
    exp2_raw = r'\[TM4J\] Report published\. Project: project_prefix\. Test cycle key: R\d+'
    exp2 = exp2_raw.replace('project_prefix', project_prefix)
    assert exp1 in output, f'\nexpected: {exp1}\ngot: {output}'
    for line in output.split('\n'):
        if match(exp2, line):
            break
    else:
        raise AssertionError(f'\n{exp2} not found in output:\n{output}')

    exp3 = f'[TM4J] Test cycle description: {tcycle_desc}'
    assert exp3 in output, f'got: {output}'


@mark.xfail
def test_tm4j_unavailable():
    print('handling not implemented in API client')
    assert False


@mark.xfail
def test_tm4j_api_key_invalid():
    print('handling not implemented in API client')
    assert False


@mark.xfail
def test_tm4j_project_not_exist():
    print('handling not implemented in API client')
    assert False


@mark.xfail
def test_tm4j_test_cycle_specified_but_not_exist():
    print('handling not implemented in API client')
    assert False
