from setuptools import setup, find_packages


def get_reqs():
    with open('requirements.txt') as reqs_obj:
        return [i.strip('\n') for i in reqs_obj if not i.startswith('#')]


setup(
    author="Ilya Pollyak",
    author_email="ipollyak@klika-tech.com",
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
    description="TM4J ",
    entry_points={'pytest11': ["tm4j_reporter = pytest_tm4j_reporter.reporter"]},
    install_requires=get_reqs(),
    keywords="python pytest tm4j jira test testmanagement report",
    license="MIT",
    name="pytest-tm4j-reporter",
    packages=find_packages(),
    platforms="any",
    python_requires=">=3.7",
    url="https://github.com/Klika-Tech/tm4j_reporter_pytest",
    version='0.0.1',
)
