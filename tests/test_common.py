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
    cmd = 'pytest common/report_tests.py'.split()
    run(cmd).check_returncode()

    with open(f'test_data/{report_fname}') as orig_obj:
        orig = load(orig_obj)
    with open(report_fname) as rcvd_obj:
        rcvd = load(rcvd_obj)

    assert orig == rcvd, f'result json does not match\n' \
                         f'original: {orig}\n' \
                         f'received: {rcvd}'
