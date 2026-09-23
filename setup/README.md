# Setup

Choose by how the machine will be used:

- [One-account Ubuntu laptop guide](UBUNTU-22.04-SINGLE-ACCOUNT.md): one person runs Hadoop and Giraph from one login, in an isolated home-directory installation. This closely matches the second-PC validation and does not create extra user accounts.
- [Two-account shared-server guide](UBUNTU-22.04-FROM-SCRATCH.md): `hduser` runs Hadoop services and `mca2025` develops and submits jobs. Use when separate roles or multiple students need access. The exact two-account sequence has not yet been trialled end-to-end on a blank laptop.

Both guides include a pinned Giraph shading patch, HTTPS Maven settings, and a NodeManager compatibility wrapper. The [older lab installation notes](../docs/INSTALLATION.md) are historical context, not a complete clean-machine procedure.

For normal daily work after installation, follow the
[daily lab startup checklist](../docs/DAILY-LAB-STARTUP.md), including dynamic
IP discovery, account roles, service startup, verification, recovery, and
clean shutdown.

After setup, run:

```bash
chmod +x scripts/check_environment.sh
./scripts/check_environment.sh
```

Included here:

- `config/`: sanitized single-node Hadoop XML files for the fresh-install profile.
- `patches/`: Guava shading patch for pinned Giraph revision `14a74297378dc1584efbb698054f0e8bff4f90bc`.
- `maven-settings-https.xml`: build-time HTTPS Maven Central mirror for the archived Giraph POM.
- `compat/kill`: NodeManager-only workaround for Hadoop 2.7.7's process-group signal command on Ubuntu 22.04.
- `single-account/`: one-user environment and isolated Hadoop configuration helper.
- `UBUNTU-22.04-FROM-SCRATCH.md`: conditional installation and smoke-test procedure.

Do not store passwords, SSH keys, live Hadoop data, or machine-specific secrets here.
