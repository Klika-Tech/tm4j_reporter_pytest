from re import match
from json import load
from subprocess import run
from os import remove, path

report_fname = '.report.json'


def teardown_module():
    if path.isfile(report_fname):
        remove(report_fname)


def test_common():
    if path.isfile(report_fname):
        remove(report_fname)

    cmd = 'pytest --tm4j common/report_tests.py'.split()
    cmd_run = run(cmd, capture_output=True)
    output = cmd_run.stdout.decode()

    print('some tests should fail, so code 1 returned by pytest')
    assert cmd_run.returncode == 1

    print('CHECK: tests without a TM4J ID are listed as warning in stdout')
    expected_ptrn = 'tests affected:.*report_tests.py::test_withoutTm4jId_two'
    for line in output.split('\n'):
        if match(expected_ptrn, line):
            break
    else:
        raise AssertionError('a test without TM4J ID is not listed in warning message')

    with open(f'test_data/report.json') as orig_obj:
        orig = load(orig_obj)
    with open(report_fname) as rcvd_obj:
        rcvd = load(rcvd_obj)

    print('CHECK: JSON-output matches expected')
    assert orig == rcvd, f'result json does not match\n' \
                         f'original: {orig}\n' \
                         f'received: {rcvd}'


def test_tm4j_unavailable():
    print('to be added after integration w TM4J API client')
