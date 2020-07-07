# Project summary
Pytest plugin which allows to upload test execution result to [TM4J Cloud](https://support.smartbear.com/tm4j-cloud/docs/index.html) version. Plugin works on the top of the `json-reporter` pytest plugin and `tm4j_reporter_api` library.


# Install and setup
## How to build
    python setup.py sdist

## How to install
    # PyPi
    pip install pytest-tm4j-reporter
    # Git
    pip install git+ssh://git@github.com:Klika-Tech/tm4j_reporter_pytest.git

## Plugin configuration

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

## Writing the tests
To be able to report your test to TM4J your test names should follow convetion: `test_T<TM4J test id>_the_rest_of_test_name.`
So workflow will be:
*  Create test case in TM4J (from UI)
*  Notice it's unique id
*  Create test in pytest with TM4J prefix in name.

Let's say in TM4J project with project key `QT` full test key is `QT-T1234`. In this case in pytest it should be created like

```python
def test_T1234_login_as_user():
    ...test code goes here
```

## Metadata
It is possible to add and report additional metadata using `tm4j` fixture. Currently supported only `comment`. Example:

```python
def test_T1701_my_test(tm4j_r):
    tm4j_r.comment = 'Here might be some comment for this test'

```
Please note that if you use `tm4j_r` fixture you won't be able to run the test without enabling plugin `--tm4j`

## How to run
Finally we're ready to run our test(s) with reporting to TM4J. It is simple as just run pytest with `--tm4j` option

```bash
pytest --tm4j
```

## Result
* .report.json file created in CWD
* The file is overwritten each time
* Execution result is uploaded to TM4J

# Developer notes
* Line wrapping border = 120 chars

# License
This software is licensed under the [MIT License](http://en.wikipedia.org/wiki/MIT_License)
