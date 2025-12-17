# 🔒 Security Policy

This document outlines the security policy for the Autom8 platform. We take security seriously and appreciate your help in improving the safety of our software.

---

## 🚨 Reporting a Vulnerability

**Do not open a public issue on GitHub.**

If you discover a security vulnerability, please report it immediately via email:
> **Email:** [security@example.com](mailto:security@example.com)

Please include:
* Description of the vulnerability
* Steps to reproduce
* Potential impact

We will respond within 48 hours and work with you to resolve the issue.

---

## 📋 Security Guidelines

### 1. Secrets Management
**Critical Rule:** NEVER commit secrets (API keys, passwords, certificates) to Git.

*   **Use Environment Variables:** Store all sensitive config in `.env` files.
*   **Template:** Use `.env.example` as a template for required variables.
*   **Verification:** Ensure `.env` is listed in `.gitignore`.

```bash
# Example: Generating a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Authentication & Authorization
*   **JWT Tokens:** All API endpoints (except health/login) require valid JWT tokens.
*   **Role-Based Access:** Verify user roles before granting access to sensitive resources.
*   **Least Privilege:** Grant the minimum necessary permissions.

### 3. API Security
*   **Rate Limiting:** Enabled by default to prevent abuse (e.g., 100 req/min).
*   **Input Validation:** Sanitize and validate all incoming data using `autom8.security` utilities.
*   **Headers:** Standard security headers (HSTS, X-Frame-Options) are automatically injected.

### 4. Data Protection
*   **Encryption:** Sensitive data at rest should be encrypted using the configured `ENCRYPTION_KEY`.
*   **HTTPS:** Production deployments must use HTTPS.
*   **Database:** Use parameterized queries (SQLAlchemy ORM handles this) to prevent SQL injection.

---

## 🛠️ Security Development Lifecycle

1.  **Develop:** Write secure code using established patterns.
2.  **Scan:** Run `bandit` and `pip-audit` locally before committing.
3.  **Test:** Ensure security tests (`test_security.py`) pass.
4.  **Review:** All code changes require peer review.
5.  **Monitor:** Check logs for `security_event` entries.

---

## 🔄 Incident Response Plan

In the event of a security breach:
1.  **Identify:** Confirm the breach and isolate affected systems.
2.  **Mitigate:** Rotate compromised keys immediately.
3.  **Restore:** Deploy patched software.
4.  **Notify:** Inform stakeholders if data was exposed.
5.  **Review:** Conduct a post-mortem to prevent recurrence.
