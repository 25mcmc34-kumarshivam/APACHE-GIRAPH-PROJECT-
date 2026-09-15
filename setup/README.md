# Setup

Use the [complete installation guide](../docs/INSTALLATION.md) to reproduce the Ubuntu, Java 8, Hadoop 2.7.7, and Giraph environment.

For normal daily work after installation, follow the
[daily lab startup checklist](../docs/DAILY-LAB-STARTUP.md), including dynamic
IP discovery, account roles, service startup, verification, recovery, and
clean shutdown.

After setup, run:

```bash
chmod +x scripts/check_environment.sh
./scripts/check_environment.sh
```

Planned additions:

- [ ] Sanitized copies of the four verified Hadoop XML files
- [ ] Verified shell environment example
- [ ] Giraph Guava shade-plugin patch
- [ ] Version manifest and file checksums

Do not store passwords, SSH keys, live Hadoop data, or machine-specific secrets here.
