"""
in order to validate a json-report produced by the tm4j-reporter plugin
this module should be executed from test_common.py
"""


def test_T1701_one(tm4j_r):
    tm4j_r.summary = 'test one summary'
    tm4j_r.step('test one step A')
    tm4j_r.step('test one step B')


def test_T1702_two(tm4j_r):
    tm4j_r.summary = 'test two summary. should fail'
    tm4j_r.step('test two step A')
    tm4j_r.step('test two step B')
    assert False


def test_withoutTm4jId_two(tm4j_r):
    tm4j_r.summary = 'has no TM4J ID and should be listed in STDOUT as WARNING'
    tm4j_r.step('test three step A')
    tm4j_r.step('test three step B')
