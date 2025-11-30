# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

The XARF project takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:

**contact@xarf.org**

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., injection, XSS, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity and complexity

### Security Update Process

1. **Triage**: We'll confirm the vulnerability and assess severity
2. **Fix Development**: We'll develop and test a fix
3. **Disclosure**: We'll coordinate disclosure timing with you
4. **Release**: We'll release a security update
5. **Announcement**: We'll publish a security advisory

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest stable version
2. **Validate Input**: Never trust user-provided XARF reports without validation
3. **Size Limits**: Enforce size limits on evidence payloads (default: 5MB per item, 15MB total)
4. **Email Validation**: Use strict mode for email validation when processing reports from untrusted sources
5. **Network Exposure**: Don't expose XARF parser directly to the internet without proper validation

### For Developers

1. **Input Validation**: The parser validates all fields against JSON schema
2. **Email Validation**: Uses `email-validator` library for RFC-compliant validation
3. **Date Validation**: Validates timestamps against ISO 8601 format
4. **Size Limits**: Built-in limits prevent DoS via large payloads
5. **Type Safety**: Full type hints and Pydantic validation

## Known Security Considerations

### 1. Evidence Payload Size

XARF reports can include evidence payloads. The parser enforces:
- Maximum 5MB per evidence item
- Maximum 15MB total evidence per report

### 2. Email Address Validation

The parser uses `email-validator` for email validation. In strict mode, it performs DNS MX record checks.

### 3. Timestamp Handling

All timestamps must be in ISO 8601 format with timezone information. The parser validates format but does not check if timestamps are in the future.

### 4. Schema Validation

All reports are validated against JSON schema. Invalid reports are rejected.

### 5. V3 Compatibility Mode

When processing XARF v3 reports:
- Automatic conversion is performed
- Deprecation warnings are issued
- Original v3 data is preserved in metadata

## Vulnerability Disclosure Policy

We follow a **coordinated disclosure** model:

1. **Private Disclosure**: Report sent to contact@xarf.org
2. **Acknowledgment**: We confirm receipt within 48 hours
3. **Investigation**: We investigate and develop a fix
4. **Fix Release**: We release a security update
5. **Public Disclosure**: We publish advisory 7 days after fix release

## Security Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

<!-- Security researchers will be listed here -->

*No vulnerabilities reported yet.*

## Bug Bounty Program

Currently, we do not offer a bug bounty program. However, we deeply appreciate security research and will publicly acknowledge your contribution.

## Contact

- **Security Email**: contact@xarf.org
- **PGP Key**: Not yet available
- **GitHub Security Advisories**: https://github.com/xarf/xarf-python/security/advisories

## Additional Resources

- [XARF Specification](https://xarf.org)
- [XARF Python Parser Documentation](https://github.com/xarf/xarf-python)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Last Updated**: 2025-11-30
