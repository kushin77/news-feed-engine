# ElevatedIQ News Feed Engine - Security Testing Suite

This directory contains comprehensive security tests for the News Feed Engine.

## Overview

| Test Category | Tests | Description |
|---------------|-------|-------------|
| Input Validation | 6 | SQL injection, XSS, path traversal detection |
| Authentication | 4 | Password strength, token security, JWT |
| Data Protection | 4 | Sensitive data detection, encryption |
| API Security | 4 | CORS, headers, rate limiting |
| Dependency Security | 2 | Vulnerable patterns, secure random |
| File Security | 3 | Path traversal, extensions, size limits |
| Configuration | 4 | Debug mode, cookies, database |
| Logging | 1 | Sensitive data redaction |

## Quick Start

```bash
# Run all security tests
pytest tests/security/ -v -m security

# Run with coverage
pytest tests/security/ -v --cov=processor --cov-report=term-missing

# Run specific test class
pytest tests/security/test_security.py::TestInputValidation -v
```bash

## Test Categories

### 1. Input Validation Tests

Tests for detecting malicious input patterns:

```python
# SQL Injection patterns
"'; DROP TABLE users; --"
"1 OR 1=1"
"UNION SELECT * FROM passwords"

# XSS patterns
"<script>alert('XSS')</script>"
"<img src=x onerror=alert('XSS')>"
"javascript:alert('XSS')"

# Path Traversal patterns
"../../../etc/passwd"
"%2e%2e%2f%2e%2e%2fetc%2fpasswd"

# Command Injection patterns
"; cat /etc/passwd"
"| ls -la"
"$(cat /etc/passwd)"
```bash

### 2. Authentication Security Tests

```python
# Password strength validation
# Requires: 8+ chars, upper, lower, digit, special char
strong_password = "K9#mP2$xL5@nQ8!w"

# Token generation randomness
token = secrets.token_urlsafe(32)

# Timing-safe comparison
hmac.compare_digest(secret, provided)
```bash

### 3. Data Protection Tests

```python
# Sensitive data patterns detected:
- Credit card numbers: 4111-1111-1111-1111
- SSN: 123-45-6789
- API keys: api_key: sk_live_...
- AWS keys: AWS_FAKE_IOSFODNN7EXAMPLE (fake pattern)
- JWT tokens: eyJhbG...

# Secure hash algorithms
hashlib.sha256(data).hexdigest()
```bash

### 4. API Security Tests

```python
# Required security headers
{
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000",
    "Content-Security-Policy": "default-src 'self'"
}

# Rate limiting configuration
rate_limits = {
    "default": 100,  # requests per minute
    "search": 30,
    "ai_analysis": 10,
}
```bash

### 5. File Security Tests

```python
# Safe file path validation
def is_safe_path(base: str, filename: str) -> bool:
    full_path = os.path.normpath(os.path.join(base, filename))
    return full_path.startswith(os.path.normpath(base))

# Allowed extensions
allowed = {".pdf", ".png", ".jpg", ".json"}

# File size limits
max_file_size = 10 * 1024 * 1024  # 10MB
```bash

## Security Scanning Tools

### Bandit (Python Security Linter)

```bash
# Run Bandit on processor code
bandit -r processor/ -f json -o reports/bandit-report.json

# Run with severity filter
bandit -r processor/ -ll  # Only medium and higher
```bash

### Safety (Dependency Checker)

```bash
# Check for vulnerable dependencies
safety check -r requirements.txt

# Generate JSON report
safety check -r requirements.txt --json > reports/safety-report.json
```bash

## Integration with CI/CD

### GitHub Actions Example

```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Run security tests
      run: pytest tests/security/ -v -m security

    - name: Run Bandit
      run: bandit -r processor/ -f json -o bandit.json

    - name: Check dependencies
      run: safety check -r requirements.txt
```bash

## Makefile Targets

```bash
# Run security tests
make security-test

# Run Bandit scan
make security-scan

# Check dependencies
make security-deps

# Full security audit
make security-audit
```bash

## Adding New Security Tests

1. Add test to appropriate class in `test_security.py`
2. Mark with `@pytest.mark.security`
3. Document the vulnerability being tested
4. Add to this README

Example:

```python
class TestNewSecurityCategory:
    """Test new security category."""

    def test_new_vulnerability_detection(self):
        """Test detection of new vulnerability pattern."""
        dangerous_input = "malicious_pattern"
        pattern = re.compile(r"malicious_pattern")
        assert pattern.search(dangerous_input)
```bash

## Security Baselines

### Minimum Requirements

| Metric | Target |
|--------|--------|
| Security test coverage | 100% of OWASP Top 10 |
| Bandit issues (high) | 0 |
| Bandit issues (medium) | 0 |
| Known vulnerabilities | 0 |
| Password entropy | 80+ bits |
| Token length | 256+ bits |

### Response Times

| Security Check | Max Time |
|----------------|----------|
| Input validation | <1ms |
| Token verification | <10ms |
| Full security scan | <60s |

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
