# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in XARF Python Parser, please report it responsibly.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, report security vulnerabilities by:

1. **Email**: Send details to security@xarf.org
2. **Private Advisory**: Use GitHub's [private security advisory feature](https://github.com/xarf/xarf-python/security/advisories/new)

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Affected versions
- Potential impact assessment
- Any proof-of-concept code (if applicable)
- Your name/handle for credit (optional)

### Response Timeline

- **Acknowledgment**: Within 48 hours of report
- **Initial Assessment**: Within 5 business days
- **Status Updates**: Every 7 days until resolution
- **Fix Timeline**: Critical issues within 30 days, others within 90 days

### Disclosure Policy

- We will coordinate public disclosure with you
- Security advisories will be published after fixes are released
- We credit security researchers in advisories (unless you prefer to remain anonymous)

## Security Features

This project implements multiple security layers:

### Automated Scanning

- **CodeQL Analysis**: Deep semantic security analysis (weekly + on PRs)
- **Dependency Review**: PR-based vulnerability scanning
- **Dependabot**: Automated dependency security updates
- **Secret Scanning**: Detects committed credentials
- **Bandit**: Python-specific security linter in CI

### Code Quality Gates

All pull requests must pass:

- Static security analysis (Bandit)
- Type safety checks (MyPy strict mode)
- Dependency vulnerability scans
- Code complexity limits (Radon)

### Security Best Practices

Our codebase follows:

- Strict type hints for safety
- Input validation via Pydantic models
- No hardcoded credentials
- Principle of least privilege
- Regular dependency updates

## Known Security Considerations

### XARF Report Processing

When processing XARF reports:

1. **Input Validation**: All reports are validated against JSON schema
2. **Email Parsing**: Uses python-email-validator for safe email processing
3. **Date Handling**: Uses python-dateutil for timezone-aware parsing
4. **No Code Execution**: Parser does not execute any user-provided code

### Dependencies

We actively monitor and update dependencies for security issues:

- Automated Dependabot updates for vulnerabilities
- Grouped minor/patch updates for development dependencies
- Individual PRs for production dependency major updates

## Security Updates

Security updates are released as:

- **Critical**: Immediate patch release
- **High**: Patch release within 7 days
- **Moderate**: Included in next minor release
- **Low**: Included in next release cycle

Subscribe to [GitHub Security Advisories](https://github.com/xarf/xarf-python/security/advisories) for notifications.

## Responsible Disclosure

We are committed to working with security researchers under responsible disclosure guidelines:

1. Allow reasonable time for fixes before public disclosure
2. Avoid privacy violations and data destruction
3. Do not exploit vulnerabilities beyond proof-of-concept
4. Respect user privacy and data protection regulations

## Security Hall of Fame

We recognize security researchers who help improve our security:

<!-- Security researchers will be listed here after coordinated disclosure -->

---

For general inquiries or questions about this policy, contact: security@xarf.org
