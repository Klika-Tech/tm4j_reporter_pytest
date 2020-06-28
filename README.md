DEVELOPER NOTES:
* line wrapping border = 120 chars 

HOW TO BUILD:
python setup.py sdist

HOW TO INSTALL:
* PyPi: pip install pytest-tm4j-reporter
* Git: pip install git+ssh://git@gitlab.klika-tech.com/qa/tm4j_reporter_pytest.git

HOW TO RUN:
run pytest with '--tm4j' argument: this will generate a report AND upload it to TM4J

RESULT:
.report.json file created in CWD
