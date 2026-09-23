# Setup

For a new Ubuntu 22.04 laptop, use the [from-scratch, check-before-install guide](UBUNTU-22.04-FROM-SCRATCH.md). It includes Hadoop XML examples, the pinned Giraph shading patch, an HTTPS Maven settings file, and a NodeManager compatibility wrapper. The build and jobs were validated on a second Ubuntu 22.04 PC in an isolated installation; the exact two-account install has not yet been trialled end-to-end on a blank laptop. The [older lab installation notes](../docs/INSTALLATION.md) are historical context, not a complete clean-machine procedure.

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
- `UBUNTU-22.04-FROM-SCRATCH.md`: conditional installation and smoke-test procedure.

Do not store passwords, SSH keys, live Hadoop data, or machine-specific secrets here.
