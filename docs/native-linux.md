# Evaluation environment and supplied services

## Confirmed tool contract

The target supplies Python 3.12, Node 22/npm, git, Chrome and Playwright,
plus PostgreSQL, MariaDB, Redis and SQLite. Python/npm packages come from the
environment's mirror, which may lack newer or unusual releases.
Other supplied tools include gcc, clang, CMake, Rust/cargo, Go standard library,
Java 21/Maven/Gradle, .NET 8, gdb, tmux and vim. These tasks use Python and the
existing Node UI; the other language stacks are unnecessary.

System package installation, containers, Go modules, NuGet, Ruby gems and native
desktop toolkits are outside this toolset. Do not add those prerequisites.

## Preflight without installation

```bash
python3 --version
python3 scripts/environment_probe.py
python3 -m pip --version
node --version
npm --version
```

Run the probe in the actual target. It reports installed packages/commands only,
without downloading, changing services or reading credentials. Use the supplied
mirror; do not replace it with another index or disable TLS validation.

`requirements.txt` is the newer reference profile; `requirements-compatible.txt`
is a separate older profile. Do not mix their pins/constraints. Install the
chosen profile, run pip check, record pip freeze and rerun the actual tests.
Neither profile guarantees that every dependency exists on the target mirror.
Ruff/pre-commit are optional development tools, not mandatory task dependencies.

## Provided databases

Keep the PostgreSQL work already in progress. Use supplied connection information
and the platform's service controls. A tool being installed does not guarantee
an already running daemon, a particular port, or administrative service access.

```bash
pg_isready -h "$PGHOST" -p "$PGPORT" -t 5
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -c 'SELECT 1;'
```

Set these variables from the actual environment. Verify authentication, synthetic
seed data and read-only permissions separately. Do not alter other users' data.
The two operator-UI ideas use the existing file-backed API and need no database.

## Chrome, Playwright and Selenium

Locate the supplied Playwright binding/CLI and reuse the installed browser.
With its Python binding, `p.chromium.launch(channel="chrome", headless=True)`
uses installed Chrome. Do not download another browser or system dependencies.

ChromeDriver is not guaranteed by the tool list. Existing Selenium UI checks
need a compatible driver; inspect the probe before enabling --run-ui. The factory
accepts driver_path for a provided driver. Do not count a Playwright check as a
Selenium WebDriver pass. If a driver is unavailable and resolver downloads are
blocked, report that UI lane as blocked. The 37 unit and 7 non-UI component checks
remain separate. Do not require driver downloads from outside the allowed source.

## SSH/SFTP eligibility

An SSH server is not guaranteed. Before selecting the task, check for an
authorized endpoint and an available mirrored client library. Paramiko is one
client choice. A mirrored AsyncSSH package can provide both client and loopback
SSH/SFTP server functionality in ordinary Python processes, without a system
daemon or administrative package installation.

Keep a Python fixture small: disposable keys, loopback listener on an available
port, a test-owned directory, real SFTP, and a finite synthetic processor reading
the uploaded files. Delegate the SSH/SFTP protocols to the library. Verify host
key rejection, actual transfers/output and owned-process shutdown.

Only an existing authorized endpoint or a working mirrored-library fixture
qualifies as real SSH/SFTP integration. If neither is available, record the
environment blocker. Unit mocks do not substitute for that integration result.

## Parallel and frontend checks

Check pytest-xdist on the mirror before choosing parallel execution; do not build
a replacement runner if missing. Real Selenium parallel checks also depend on
the driver preflight. For the React UI ideas, use Node 22's built-in node --test
for focused helper tests after compiling with the existing TypeScript compiler.
Use the provided Playwright/Chrome for browser checks. No additional test framework
is required. Retain the committed npm lockfile and record mirror failures.
