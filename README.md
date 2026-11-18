# Python Testing Boilerplate

A Python 3.12 testing foundation built around pytest, Selenium Chrome sessions,
page objects, YAML configuration, and Allure evidence. Use it as a starting point
for a testing project and extend the existing layers as new capabilities are needed.

Repository: [filiprak01/python-testing-bolierplate](https://github.com/filiprak01/python-testing-bolierplate).
The distribution installed by pip is named `python-testing-boilerplate`.

## Documentation

Start with the [documentation index and capability map](docs/README.md). It links
the implemented behavior to its source files and unit/integration coverage.

| Reference | Contents |
| --- | --- |
| [Current capabilities](#current-capabilities) | What this baseline already implements. |
| [Next task additions](#what-the-next-tasks-add) | Independent REST, PostgreSQL, evidence, SSH/SFTP, and parallel-execution extensions. |
| [pip setup](#setup-with-pip) | Runtime checks, requirements, editable installation, and restricted-network use. |
| [Framework tests and UI examples](#run-and-verify) | Marker expressions for unit, integration, functional, and application example checks. |
| [Test markers](#test-markers) | Classification, current test counts, and conventions for new tests. |
| [Configuration reference](#configuration) | YAML, environment overrides, precedence, and supported values. |
| [Source layout and extension points](#layout-and-extension-points) | Where to add clients, configuration, tests, and application coverage. |
| [Evidence and reports](#evidence-and-reports) | Logs, screenshots, cleanup, Allure commands, and current limitations. |
| [Continuous integration](#continuous-integration) | Required baseline checks and optional public UI runs. |

## Current capabilities

- Named, independently owned UI clients through `UIClientPool`.
- Headed or headless Chrome, explicit waits, page objects, and assertion helpers.
- Validated YAML configuration, `.env` loading, and environment overrides.
- Named Allure steps, optional step screenshots, and execution logging.
- Screenshot, page source, browser log, and execution log attachments for failed test bodies.
- Generated artifact cleanup that rejects paths overlapping source or static inputs.
- Unit tests, component integration tests, and real local-browser integration tests.
- A separate, optional public Shopify demo homepage smoke test.

REST API clients, database/SSH clients, SFTP processing, and parallel execution are extension work. They are
not implemented in this baseline. Chrome is the only supported browser.

## What the next tasks add

| Area | Available now | Planned addition |
| --- | --- | --- |
| UI testing | UI clients, Chrome, page objects, waits, screenshots, downloads, and Allure evidence | Reused by the extensions; retain the existing capability tests and application example. |
| REST testing | No REST client | Configured HTTP sessions, authentication, bounded timeouts, JSON/non-JSON responses, safe request evidence, local HTTP integration tests, and opt-in public API checks. |
| Database/SSH testing | No database client or SSH tunnel | Parameterized PostgreSQL reads, direct/tunneled connections, host-key validation, connection cleanup, safe query evidence, and disposable real-service integration tests. |
| Failure diagnostics | One session log and call-phase attachments | Per-test logs and setup/call/teardown evidence, verified with real nested pytest sessions. |
| SSH/SFTP processing | No transfer or remote-processing client | Upload a synthetic file, run a bounded command, retrieve and verify its result using native OpenSSH. |
| Parallel execution | Serial tests with shared artifact directories | Two-worker execution, isolated worker/run artifacts, and safe cleanup ownership. |

This pip preparation branch is `prep/pip-native-linux`. It changes installation
and documentation; the proposed feature clients remain unimplemented. Start each
remaining independent task from the recorded pip baseline. Keep current REST and
PostgreSQL work separate; do not reset those implementations to this source.

## Setup with pip

Use Python 3.12 or later and an existing pip installation. Check the interpreter
before installing: the original testing baseline requires Python 3.12+. This
checkout uses setuptools and plain requirements; no separate package-manager CLI
or container runtime is needed. Chrome is required only for explicit UI tests.

Linux, from the checkout root:

```bash
python3 --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip --version
python -m pip install -r requirements-dev.txt
python -m pip install --no-build-isolation -e .
python -m pip check
```

On Windows create the environment with your installed Python 3.12 interpreter,
activate `.venv\Scripts\Activate.ps1`, then use the same `python -m pip` commands.
Use `python -c "import sys; print(sys.executable)"` to confirm the interpreter.

`requirements.txt` pins direct testing dependencies. `constraints.txt` pins the
previously verified transitive versions without installing unused packages.
`requirements-dev.txt` adds Ruff, optional pre-commit, setuptools and wheel.
The editable install uses those already installed build tools, so it does not
start a second isolated build-tool download. Runtime versions remain those of
the verified baseline; build tools have minimum versions and are checked by pip.

If a dependency is rejected, record its name and the actual error. Use only the
index or wheelhouse supplied by the environment. With an approved local wheelhouse,
the dependency installation can be performed offline:

```bash
python -m pip install --no-index --find-links=/path/to/approved-wheelhouse -r requirements-dev.txt
python -m pip install --no-build-isolation --no-deps -e .
python -m pip check
```

The wheelhouse must contain compatible wheels for this Python/OS and all required
dependencies. The path above is a placeholder, not a bundled wheelhouse. Do not
disable TLS checks, use a different unapproved mirror, or report blocked installs
as a successful verification.

Native Linux services are described in [the service runbook](docs/native-linux.md).
REST/PostgreSQL work already in progress should retain its own current source;
this pip baseline is for the remaining independent tasks.

## Run and verify

Select tests by their explicit pytest markers. Directories organize files; they
do not determine a test's classification or whether it is selected.

| Test area | Marker expression | Current cases | What it verifies |
| --- | --- | --- | --- |
| Framework unit tests | `unit` | 37 | Configuration boundaries, client ownership, browser options, assertions, and evidence error handling. No browser or network service. |
| Framework component integration | `integration and not ui` | 7 | Real YAML, environment variables, filesystem, and logging with substituted browser/report boundaries. |
| Framework browser integration | `integration and ui` | 3 | Local Chrome interaction, screenshots, downloads, and negative assertion diagnostics. |
| All framework capabilities | `framework` | 47 | All unit and integration checks, independent of the public application. |
| Application UI example | `example` | 1 | The public Shopify homepage functional smoke example. |

**Verify framework capabilities only**, including real local Chrome integration:

```text
python -m pytest -m framework --run-ui --headless -q
```

**Run the application UI example only:**

```text
python -m pytest -m example --run-ui --headless -q
```

The `framework` selection excludes the public application example. Markers can be
combined with `and`, `or`, `not`, and parentheses; quote compound expressions.
For example, `-m "unit or integration"` currently selects the same 47 framework checks.
`-m` selects tests; `--run-ui` separately permits browser execution.

Run the default suite. Browser tests are explicitly skipped until `--run-ui` is supplied:

```text
python -m pytest -q
```

Run isolated unit tests or component integration tests without a browser:

```text
python -m pytest -m unit -q
python -m pytest -m "integration and not ui" -q
```

Run every framework integration test, including the local browser checks:

```text
python -m pytest -m integration --run-ui --headless -q
```

Run the complete deterministic baseline, including real headless Chrome tests:

```text
python -m pytest -m framework --run-ui --headless --alluredir=allure-results -q
```

The local browser tests start and stop a temporary HTTP server bound to `127.0.0.1`.
They verify a real form interaction, a saved PNG, a browser download, and a useful
missing-element assertion failure against committed synthetic files. They do not
require an external application.
The component integration tests use real YAML, environment variables, and filesystem
outputs with a substituted browser boundary; the local-browser tests use real Chrome.

Run only those real-browser integration tests:

```text
python -m pytest -m "integration and ui" --run-ui --headless --alluredir=allure-results -q
```

Run the public homepage smoke test separately:

```text
python -m pytest -m "example and smoke" --run-ui --headless --alluredir=allure-results -q
```

The public smoke target is `https://sauce-demo.myshopify.com/`, a Shopify demonstration
store. It is a different application from `saucedemo.com`. Its availability and markup
are controlled externally. A public-site failure does not establish that the local
framework is broken; inspect the attached evidence and reproduce it locally.

Selenium Manager obtains the driver matching your installed Chrome. Its first run
requires network access; subsequent runs can use the cached driver. The factory also
accepts `driver_path` for environments that provide ChromeDriver explicitly.

Other useful commands:

```text
python -m pytest --collect-only -q
python -m pytest --collect-only -m framework -q
python -m pytest -m "functional and framework" --run-ui --headless -q
python -m ruff check src tests
python -m ruff format --check src tests
python -m pip wheel --no-build-isolation --no-deps . --wheel-dir dist
```

The functional framework selection above runs the two local form/download checks.
The default command reports 44 passes and four intentional browser skips. With
`--run-ui --headless`, the complete suite has 48 cases, including the public example.

## Test markers

Markers describe independent properties and can overlap:

| Marker | Meaning | Current cases |
| --- | --- | --- |
| `framework` | Reusable framework capability coverage. Add either `unit` or `integration` as well. | 47 |
| `unit` | Isolated behavior without browsers or network services. | 37 |
| `integration` | Collaborating components or a real local browser. | 10 |
| `functional` | Observable feature behavior: local form, local download, and public homepage. | 3 |
| `e2e` | A complete user journey across multiple functional boundaries. | 0 |
| `ui` | Requires a browser and the explicit `--run-ui` switch. | 4 |
| `example` | Application examples that consume the framework. | 1 |
| `smoke` | A quick core-behavior check; currently the public homepage. | 1 |
| `regression` | Optional label for broader regression coverage. | 0 |
| `slow` | Optional runtime label for slower checks. | 0 |

For example, the form and download checks carry `framework`, `integration`,
`functional`, and `ui`. The public homepage carries `example`, `functional`, `ui`,
and `smoke`. `-m functional --run-ui --headless` includes that public site;
add `and framework` for local-only functional checks.

No current test is marked `e2e`: the homepage smoke check does not verify a complete
business journey. Add `e2e` when implementing one. An expression matching no tests
(currently `-m e2e`) returns pytest exit code 5, not a passing test result.

Declare marks directly on the test or module; moving a file must not change its
classification. A framework integration module using Chrome can declare:

```python
import pytest

pytestmark = [pytest.mark.framework, pytest.mark.integration, pytest.mark.ui]
```

Add `@pytest.mark.functional` to individual feature checks. Keep `framework` and
`example` separate, and choose one of `unit` or `integration` for framework coverage.
Register new markers in `pytest.ini` before using them; strict marker validation is
enabled. Browser tests must carry `ui` so they follow the explicit opt-in.

## Configuration

The default configuration is `config/default.yaml`. The loader resolves relative
paths against the checkout root and loads optional variables from `.env` without
overwriting existing shell variables.

| Variable | Behavior |
| --- | --- |
| `TEST_CONFIG_FILE` | Select another YAML file; a relative path is checkout-relative. |
| `TEST_BASE_URL` | Override `environment.base_url`. |
| `TEST_BROWSER` | Override `browser.name`; currently only `chrome` is implemented. |
| `TEST_HEADLESS` | Override `browser.headless`; accepted values are `true` or `false`. |

Passing `config_path` directly to `load_config()` takes precedence over
`TEST_CONFIG_FILE`. Shell overrides then take precedence over YAML values. YAML
strings can reference variables such as `${MY_TEST_URL}`; define every referenced
variable in your shell or `.env`. A command-line `--headless` always enables headless
mode, even if the YAML or environment says `false`.

Example in PowerShell:

```powershell
$env:TEST_HEADLESS = "true"
python -m pytest -m "integration and ui" --run-ui -q
Remove-Item Env:TEST_HEADLESS
```

## Layout and extension points

```text
config/default.yaml             Runtime defaults
src/project.py                  Checkout-relative paths
src/models/configuration.py     Typed configuration and path validation
src/config/loader.py             YAML, .env, and shell overrides
src/clients/                    Client ownership and session lifecycle
src/webdriver/                  Chrome options and driver creation
src/pages/                      Page objects and explicit UI interactions
src/locators/                   Application selectors
src/flows/                      Place for reusable multi-page workflows
src/assertions/                 Wait-backed UI assertions
src/evidence/                   Allure attachments and artifact cleanup
tests/conftest.py               pytest options, browser fixtures, and failure hook
tests/unit/                     Isolated framework regression coverage
tests/integration/              Component and real local-browser coverage
tests/examples/                 Optional public application UI example
data/fixtures/                  Committed synthetic inputs and local UI fixture
data/uploads/                   Place for committed non-sensitive upload fixtures
```

The [capability map](docs/README.md#implemented-capabilities) links each area to
the corresponding implementation and regression tests.

Reuse `UIClient`, `BasePage`, configuration models, and pytest fixtures when adding
coverage. Put selectors in locators/page objects, reusable behavior in pages/flows,
and expected-state checks in assertions. Add non-UI clients under `src/clients` when
those features are implemented. Cover client error paths with unit tests and verify
collaborating components with integration tests. Keep public-service checks explicit
so the default test command remains reproducible.

The `evidence` package deliberately avoids Python's standard-library `logging`
name. Framework modules use the normal standard-library logger.

## Evidence and reports

Every test session cleans generated files from `logs/`, `screenshots/`,
`allure-results/`, `allure-report/`, and `data/downloads/`. `.gitkeep` files remain.
`data/uploads/` and `data/fixtures/` are preserved. Collection-only runs do not clean
artifacts. Keep generated directories distinct and below the project root; the
configuration rejects source paths, static-input paths, and overlapping outputs.

Set `evidence.screenshot_after_steps: true` to capture every named UI step.
Explicit `UIClient.capture_screenshot_step()` calls work with the default `false`.
Set `screenshots_enabled: false` to disable step screenshots. The failure hook still
attempts browser diagnostics after a failed test body.

The session log is `logs/test-execution.log`. Failure attachments currently cover
the pytest `call` phase, and the baseline uses one log per session. Per-test log
isolation, setup/teardown diagnostics, and parallel workers are future extensions.

`allure-results/` contains raw JSON and attachment files. Inspect these directly
with Python and a text/image viewer; generating a separate HTML report is optional.
If an Allure CLI is already available, `allure serve allure-results` renders it.
Installing Node, Java or a reporting CLI is not required for the task baseline.
Starting another pytest session clears previous generated evidence, so retain
important logs and attachments before continuing.

## Continuous integration

`baseline.yml` installs requirements with pip and checks dependency consistency,
Ruff, package building, and the deterministic unit/integration suite with headless
Chrome on Ubuntu and Windows for pull requests and `main`, `dev`, or
`prep/pip-native-linux` pushes. Unit and integration tests use `-m unit` and `-m integration` in separate
CI steps with separate JUnit reports.
It uploads raw Allure results, JUnit XML, screenshots, and logs even on failures.

`ui-tests.yml` runs the public smoke suite daily at 04:00 UTC or manually. Manual
choices are `smoke` (`example and smoke`), `local` (`integration and ui`), and
`all` (every test). It uploads raw
Allure results and diagnostic files. These workflows require no stored credentials for the current tests.

Install the optional pre-commit checks with `python -m pre_commit install`.
They run Ruff and pytest collection. Collection validates discovery without starting
browsers or deleting the preceding run's evidence.
