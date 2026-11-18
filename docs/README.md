# Documentation index

The [root README](../README.md) is the runbook for this Python testing foundation.
This index maps the implemented capabilities to source code and verification.

## Implemented capabilities

| Capability | Implementation | Unit checks | Integration checks |
| --- | --- | --- | --- |
| UI client lifecycle, named clients, and cleanup | [UIClient](../src/clients/ui_client.py), [UIClientPool](../src/clients/client_pool.py) | [Client lifecycle/error cases](../tests/unit/test_clients.py) | [Configured client and evidence](../tests/integration/test_configuration_and_evidence.py), [real Chrome workflows](../tests/integration/test_local_browser.py) |
| YAML configuration, defaults, environment overrides, and path boundaries | [Configuration models](../src/models/configuration.py), [loader](../src/config/loader.py), [default YAML](../config/default.yaml), [.env example](../.env.example) | [Defaults and invalid/safe paths](../tests/unit/test_configuration.py) | [YAML/environment/filesystem integration](../tests/integration/test_configuration_and_evidence.py) |
| Chrome setup, headless options, and download configuration | [Driver factory](../src/webdriver/factory.py), [Chrome options](../src/webdriver/chrome_options.py) | [Options, unsupported browsers, and explicit driver service](../tests/unit/test_webdriver_and_assertions.py) | [Real form and download checks](../tests/integration/test_local_browser.py) |
| Page objects, explicit waits, and useful assertion failures | [BasePage](../src/pages/base_page.py), [assertions](../src/assertions/page_assertions.py), [example page](../src/pages/sauce_demo_home_page.py), [example locators](../src/locators/sauce_demo_locators.py) | [Timeout diagnostic regression](../tests/unit/test_webdriver_and_assertions.py) | [Real page interaction and missing-element failure](../tests/integration/test_local_browser.py) |
| Named steps and controlled screenshots | [UIClient steps and evidence](../src/clients/ui_client.py) | [Disabled screenshots and screenshot failures](../tests/unit/test_clients.py) | [Persisted evidence](../tests/integration/test_configuration_and_evidence.py), [real PNG validation](../tests/integration/test_local_browser.py) |
| Failure diagnostics and execution logs | [Evidence helpers](../src/evidence/pytest_logging.py), [pytest fixtures/hook](../tests/conftest.py) | [Independent diagnostics and failed attachment sink](../tests/unit/test_evidence.py) | [Buffered log flush before attachment](../tests/integration/test_configuration_and_evidence.py) |
| Safe generated-file cleanup | [Path validation](../src/models/configuration.py), [artifact cleanup](../src/evidence/artifacts.py) | [Protected paths](../tests/unit/test_configuration.py), [markers and sibling data](../tests/unit/test_artifacts.py) | [Static inputs preserved during configured cleanup](../tests/integration/test_configuration_and_evidence.py) |

Integration checks in `test_configuration_and_evidence.py` exercise real YAML,
environment variables, files, and logging, while substituting browser/report
boundaries where appropriate. `test_local_browser.py` uses actual headless Chrome
and an HTTP server on `127.0.0.1`. They verify framework behavior without the public
example application.

## Test suite entry points

| Suite | Marker expression | Command |
| --- | --- | --- |
| Framework unit tests (37) | `unit` | `python -m pytest -m unit -q` |
| Framework component integration, without Chrome (7) | `integration and not ui` | `python -m pytest -m "integration and not ui" -q` |
| All framework integration, including real Chrome (10) | `integration` | `python -m pytest -m integration --run-ui --headless -q` |
| Local browser integration (3) | `integration and ui` | `python -m pytest -m "integration and ui" --run-ui --headless -q` |
| All framework capabilities (47) | `framework` | `python -m pytest -m framework --run-ui --headless -q` |
| Local functional checks (2) | `functional and framework` | `python -m pytest -m "functional and framework" --run-ui --headless -q` |
| Public application UI example (1) | `example` | `python -m pytest -m example --run-ui --headless -q` |

Markers control selection; directories only organize source files. See the
[marker reference and classification rules](../README.md#test-markers) for the full
taxonomy, overlaps, and how to mark new tests. All existing framework checks carry
`framework` and either `unit` or `integration`; browser checks also carry `ui`.

The example application test remains a separate `ui`/`example`/`functional`/`smoke` test. It
demonstrates how a project consumes the framework. It is not required to verify
the framework against the local fixture. The `e2e` marker is registered for complete
user journeys; no such journey is implemented yet. An empty selection exits with
code 5. Use `python -m pytest --collect-only -m framework -q` to preview selection.

## Setup, configuration, and evidence

- [pip setup and restricted-network installation](../README.md#setup-with-pip),
  [project metadata](../pyproject.toml), [runtime requirements](../requirements.txt),
  [development requirements](../requirements-dev.txt), and [constraints](../constraints.txt).
- [Native Linux service commands and prerequisites](native-linux.md).
- [Configuration values and precedence](../README.md#configuration),
  [runtime defaults](../config/default.yaml), and [project-relative paths](../src/project.py).
- [Logs, screenshots, cleanup, Allure report commands, and limitations](../README.md#evidence-and-reports).
- [pytest markers](../pytest.ini) and [shared fixture/option definitions](../tests/conftest.py).
- [Synthetic local HTML fixture](../data/fixtures/ui_sandbox.html) and
  [expected download content](../data/fixtures/sample.txt).
- [CI explanation](../README.md#continuous-integration),
  [baseline workflow](../.github/workflows/baseline.yml),
  [public-example workflow](../.github/workflows/ui-tests.yml), and
  [optional pre-commit checks](../.pre-commit-config.yaml).

## Planned extensions

The [next-task table](../README.md#what-the-next-tasks-add) separates current
capabilities from the independent client, evidence and parallel additions. The new clients do not exist
in this starting baseline. Keep their future unit tests and integration checks
separate from application UI examples, and register new markers before using them.
