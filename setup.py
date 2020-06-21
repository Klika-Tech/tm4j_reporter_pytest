from setuptools import setup, find_packages

setup(
    name='pytest-tm4j-reporter',
    description='generate a JSON report for publishing to TM4J',
    version='0.0.1',
    packages=find_packages(),
    entry_points={'pytest11': ['tm4j_reporter = tm4j_reporter.reporter']},
    install_requires=['pytest', 'pytest-json-report'],
    classifiers=['Framework :: Pytest'],
)
