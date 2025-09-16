# Testing duplicity

## Introduction

Duplicity's tests are code, unit, and functional tests contained in the /testing folder of the main repository.  
There is one containers for each version of Python that we actively support.

## Running tests on your branch

The recommended approach is to test duplicity using Docker, to ensure that you are running tests in a known-good
environment. You can run tests on your branch as follows:

1. Install Docker
2. cd [BRANCH FOLDER]/testing/docker/dupCI
3. `./build.sh` to build and to start the containers.  
4. `docker compose up` to start the tests.  Results will show on the screen.
5. `docker compose logs -n1` to show the last line of each containers logs.
6. When you are finished, exit the Docker container and run `docker compose down` to delete the containers.

Please test your branch using this method and ensure all tests pass before submitting a merge request.

The decorator `@unittest.expectedFailure` can be used to commit a known-failing test case without breaking the test 
suite, for example to exhibit the behaviour in a bug report before it has been fixed.

## Manual testing and running individual tests

1. Docker containers
Even if you wish to run tests manually, we recommend that you do this inside the provided Docker container to ensure
that you have a clean and reproducible environment with all required dependencies for executing these. Please follow
steps 4 and 5 of the above section titled _Running tests on your branch_.  For running a single test, set 
`PYTEST_ARGS` either with an export like `export PYTEST_ARGS=testing/test_code.py` or a temporary setting like 
`PYTEST_ARGS=testing/test_code.py docker compose up`.
2. Use `pytest` locally if you want to test code on your machine.  You will need to have installed See 
https://docs.pytest.org/en/stable/contents.html for complete instructions on using `pytest`.
See _Dependencies for testing_ to setyp your environment.

## Dependencies for testing
If you should prefer to execute the tests locally without using Docker, see the Dockerfile in
`testing/docker/dupCI/Dockerfile.py3*` for requirements to correctly set up your environment.
