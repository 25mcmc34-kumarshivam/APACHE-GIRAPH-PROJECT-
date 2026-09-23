# Setup

For a new Ubuntu 22.04 laptop, use the [from-scratch, check-before-install guide](UBUNTU-22.04-FROM-SCRATCH.md). It includes the verified Hadoop XML examples and the pinned Giraph compatibility patch. The [older lab installation notes](../docs/INSTALLATION.md) are useful historical context, but are not a complete clean-machine procedure.

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
- `patches/`: Guava compatibility patch for pinned Giraph revision `14a74297378dc1584efbb698054f0e8bff4f90bc`.
- `UBUNTU-22.04-FROM-SCRATCH.md`: conditional installation and smoke-test procedure.

Do not store passwords, SSH keys, live Hadoop data, or machine-specific secrets here.
