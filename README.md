### Project summary
[TM4J]((https://support.smartbear.com/tm4j-cloud/docs/index.html))
is a Test Management for Jira

The plugin uploads test results to TM4J test cycle using its API


### How to build
    python setup.py sdist

### How to install
    # PyPi
    pip install pytest-tm4j-reporter
    # Git
    pip install git+ssh://git@gitlab.klika-tech.com/qa/tm4j_reporter_pytest.git

### How to run
Run pytest with '--tm4j' argument: this will generate a report AND upload it to TM4J

### Plugin configuration
pytest.ini "pytest" section  
All parameters are mandatory if "optional" is not specified 

**Parameter**: tm4j_project_prefix  
**Description**: TM4J project prefix without trailing dash  
**Example**: QT  
  
**Parameter**: tm4j_api_key  
**How to get**: open Jira - "Your profile and settings" button at upper-right - Test Management for Jira API keys - Create access key  
**Example**: a JWT token  

**Parameter**: tm4j_testcycle_key (optional)  
**Description**: TM4J existing test cycle key. A new test cycle created if not specified  
**Example**: R40  

**Parameter**: tm4j_testcycle_prefix (optional. default = autoreport)  
**Description**: TM4J test cycle prefix for creating a new testcycle when no existing one specified
**Example**: "autoreport" makes autoreport-<UNIX epoch time>
 
**Parameter**: tm4j_project_webui_host (optional)  
**Description**: TM4J project webui host. If specified, a URL for testrun added to pytest output
**Example**: klika-tech.atlassian.net  

The same parameters can be passed via sys env vars (the name is the same)  
Sys env vars override the same values in pytest.ini

### Result
* .report.json file created in CWD
* The file is overwritten each time
* Execution result is uploaded to TM4J

### Developer notes
* Line wrapping border = 120 chars
