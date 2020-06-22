from setuptools import setup, find_packages

with open('requirements.txt') as reqs_obj:
    reqs = [i.strip('\n') for i in reqs_obj]

setup(
    name='pytest-tm4j-reporter',
    description='Generate a JSON report for publishing to TM4J',
    version='0.0.1',
    packages=find_packages(),
    entry_points={'pytest11': ['tm4j_reporter = tm4j_reporter.reporter']},
    install_requires=reqs,
    classifiers=['Framework :: Pytest'],
)
