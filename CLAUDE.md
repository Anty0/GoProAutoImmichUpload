# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See README.md for architectural overview, setup instructions, known limitations/workarounds, etc.
This file contains Claude-specific implementation details not covered in the README.

### Notes

- **Docker Constraints**: The service is designed to run in a read-only Docker container. All file I/O operations (COHN credentials, etc.) use in-memory storage. The container requires `/run/dbus` mounted read-only to communicate with BlueZ on the host.
