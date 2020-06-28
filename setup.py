from setuptools import setup, find_packages


def get_reqs():
    with open('requirements.txt') as reqs_obj:
        return [i.strip('\n') for i in reqs_obj if not i.startswith('#')]


setup(
    name='pytest-tm4j-reporter',
    description='Generate a JSON report for publishing to TM4J',
    version='0.0.1',
    packages=find_packages(),
    entry_points={'pytest11': ['tm4j_reporter = pytest_tm4j_reporter.reporter']},
    install_requires=get_reqs(),
    classifiers=['Framework :: Pytest'],
)
