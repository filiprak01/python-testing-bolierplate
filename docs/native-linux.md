# Native Linux services

These commands support a supplied Linux VM or runner. They do not use a container
runtime. The Python library still needs Python 3.12+; inspect the actual image first.

## Preflight

```bash
python3 --version
python3 -m pip --version
command -v ssh
command -v sftp
command -v ssh-keygen
command -v pg_isready
command -v psql
test -x /usr/sbin/sshd
```

Missing service tools do not mean the Python client is broken. On a Debian/Ubuntu
machine with permitted package installation and administrative access:

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends openssh-server openssh-client postgresql postgresql-client
```

Skip installation for services already supplied. Record package/privilege/network
blockers rather than replacing a real-service test with a claimed mock pass.

## Existing PostgreSQL task

Keep its current implementation and SQL fixture. Prefer an existing service:

```bash
sudo service postgresql start
pg_isready -h 127.0.0.1 -p 5432 -t 5
```

If systemd is available, `sudo systemctl start postgresql` is an alternative.
Readiness only proves the server responds; separately verify authentication,
the synthetic seed row and the read-only role with the task's actual tests.
Do not drop existing databases or change other users' authentication configuration.
Use task-specific database/role names and retain only synthetic fixtures.

## OpenSSH and SFTP

Use an authorized host/service or an isolated loopback fixture. For a supplied
system service, `sudo service ssh start` starts OpenSSH on Debian/Ubuntu.
Some distributions use the service name `sshd`; use the image's actual service.
Configure key authentication for a dedicated test identity and verify the known
host key from a trusted fixture or administrator. Do not copy personal keys.

For an isolated fixture, keep its config, host/client keys, PID, logs and data
under an ignored `.local/ssh-fixture/` directory. Use a separate high port and
`ListenAddress 127.0.0.1`; do not replace `/etc/ssh/sshd_config`. The agreed fixture
must define `Subsystem sftp internal-sftp` and an authorized test account.
Validate its generated config before starting:

```bash
sudo /usr/sbin/sshd -t -f "$PWD/.local/ssh-fixture/sshd_config"
```

The remaining SSH/SFTP task must deliver the exact fixture startup/readiness/stop
commands and test account/key provisioning for the evaluation image. The client
and fixture are proposed feature work, not implemented in this baseline. A
non-systemd image can run a dedicated sshd process with `-D -f CONFIG -E LOG`.
Stop only the PID owned by that fixture and remove only its task-owned scratch data.

## Remote processing contract

The SSH/SFTP client task uploads synthetic input into a unique task-owned remote
directory, runs an agreed finite processing command, captures exit status plus
bounded stdout/stderr, downloads the result and verifies its bytes/checksum.
An SSH channel timeout alone does not prove a remote process was killed. Agree
the remote process deadline and cleanup mechanism explicitly and verify it.
