"""
in order to validate a json-report produced by the tm4j-reporter plugin
this module should be executed from test_common.py
"""


def test_T303_one(tm4j_r):
    tm4j_r.summary = 'test one summary'
    tm4j_r.step('test one step A')
    tm4j_r.step('test one step B')


def test_T304_two(tm4j_r):
    tm4j_r.summary = 'test two summary'
    tm4j_r.step('test two step A')
    tm4j_r.step('test two step B')


def test_withoutTm4jId_two(tm4j_r):
    tm4j_r.summary = 'test three summary'
    tm4j_r.step('test three step A')
    tm4j_r.step('test three step B')
