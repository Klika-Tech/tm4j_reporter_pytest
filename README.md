# Project summary
[TM4J]((https://support.smartbear.com/tm4j-cloud/docs/index.html))
is a Test Management for Jira

The plugin allows to upload pytest execution result to TM4J Cloud version. Plugin works on the top of the `json-reporter` pytest plugin and `tm4j_reporter_api` library.

# Install and setup
## How to build
    python setup.py sdist

## How to install
    # PyPi
    pip install pytest-tm4j-reporter
    # Git
    pip install git+ssh://git@gitlab.klika-tech.com/qa/tm4j_reporter_pytest.git

### Plugin configuration

Create `pytest.ini` within your project and put the variables there (see below table)

| Param                   | Mandatory | Description                                                                                                                                            | Example                  |
|-------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| tm4j_project_prefix     | Yes       | Jira / TM4J project prefix without trailing dash                                                                                                       | QT                       |
| tm4j_api_key            | Yes       | API key to access TM4j. To get it see  [Instruction](https://support.smartbear.com/tm4j-cloud/docs/api-and-test-automation/generating-access-keys.html)|                          |
| tm4j_testcycle_key      | No        | TM4J existing test cycle key. A new test cycle created if not specified                                                                                | R40                      |
| tm4j_testcycle_prefix   | No        | Prefix for new test cycle. Default: autoreport. Full test cycle name is <prefix>-<UNIX epoch time>                                                     | Login autotests          |
| tm4j_project_webui_host | No        | Jira server base host. If provided will generate a link to a newly created test cycle                                                                  | klika-tech.atlassian.net |

Example:

```ini
[pytest]
tm4j_project_prefix = QT
tm4j_api_key = eyJ0eXAiOiJKV1QiLCJhb
tm4j_testcycle_key = R40
tm4j_testcycle_prefix = login tests
tm4j_project_webui_host = klika-tech.atlassian.net
```

# Usage

### How to run
Run pytest with '--tm4j' argument: this will generate a report AND upload it to TM4J

TODO

### Metadata
It is possible to add and report additional metadata using `tm4j` fixture. Currently supported only `comment`. Example:

```python
def test_T1701_my_test(tm4j_r):
    tm4j_r.comment = 'Here might be some comment for this test'

```
Please note that if you use `tm4j_r` fixture you won't be able to run test without enabling plugin `--tm4j`

### Result
* .report.json file created in CWD
* The file is overwritten each time
* Execution result is uploaded to TM4J

# Developer notes
* Line wrapping border = 120 chars
