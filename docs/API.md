# 📡 API Reference - Autom8

Complete REST API documentation for the Autom8 automation platform.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
6. [Data Models](#data-models)
7. [Examples](#examples)

---

## Overview

**Base URL**: `http://localhost:5000/api/v1`

**API Version**: v1

**Content Type**: `application/json`

**Character Encoding**: UTF-8

---

## Authentication

### JWT Token Authentication (Development Reference)

The Autom8 system includes JWT token infrastructure for future authentication implementation. 
Currently, **no endpoints enforce authentication**, but the infrastructure is available for developers.

**Token Structure** (if implemented):
```http
Authorization: Bearer <your_jwt_token>
```

### Token Reference Implementation

See `/api/v1/auth/protected` endpoint for an example of how to verify JWT tokens in your own implementation.

This endpoint demonstrates:
- Extracting tokens from Authorization headers
- Verifying token signatures
- Decoding token claims

**Note**: To implement real authentication, you will need to:
1. Create a User model in `autom8/models.py`
2. Implement credential verification
3. Add token verification decorators to endpoints that require authentication

---

## Rate Limiting

**Default Rate Limit**: 5,000 requests per minute

**Governance**: Rate limits are enforced at the system boundary to ensure enterprise-grade stability.

**Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp)

**Rate Limit Exceeded Response**:
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

---

## Error Handling

### Standard Error Response

Autom8 follows a sanitized error policy. In production, detailed stack traces are logged internally, while the API returns generic, safe messages.

```json
{
  "error": "Error Type",
  "message": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Sanitized server error |

---

## Endpoints

### Discovery & Status

#### GET /api/v1/info

Check API information, versioning, and governance notices.

**Authentication**: Not required

**Response**:
```json
{
  "name": "Autom8",
  "version": "1.0.0",
  "environment": "production",
  "licensed": true,
  "integrity": "verified",
  "security": {
    "rate_limiting": true,
    "cors_enabled": true,
    "https_only": false
  },
  "notices": [
    "v1 is stable but we recommend monitoring for future v2 announcements."
  ],
  "documentation": "https://github.com/..."
}
```

---

#### GET /api/v1/health

Check API health status.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "service": "Autom8 API",
  "version": "1.0.0",
  "environment": "production"
}
```

---

#### GET /metrics

Get system metrics.

**Authentication**: Not required

**Response**:
```json
{
  "cpu_percent": 15.5,
  "memory_percent": 45.2,
  "disk_percent": 60.0,
  "timestamp": "2025-12-20T14:42:00Z"
}
```

---

### Contacts

#### GET /api/v1/contacts

Retrieve a paginated list of contacts.

**Query Parameters**:
- `limit` (integer, optional): Number of items to return (default: 100)
- `offset` (integer, optional): Number of items to skip (default: 0)

**Example Request**:
```http
GET /api/v1/contacts?limit=10&offset=0
```

**Response** (200 OK):
```json
{
  "contacts": [
    {
      "id": 1,
      "name": "John Doe",
      "phone": "0701234567",
      "email": "john@example.com",
      "created_at": "2025-12-20T10:00:00Z",
      "updated_at": "2025-12-20T10:00:00Z"
    }
  ],
  "meta": {
    "total": 45,
    "limit": 10,
    "offset": 0
  }
}
```

---

#### GET /api/v1/contacts/{id}

Retrieve a specific contact by ID.

**Response**: Contact object (200 OK) or error (404 Not Found)

---

#### POST /api/v1/contacts

Create a new contact.

**Request Body**:
```json
{
  "name": "John Doe",
  "phone": "0701234567",
  "email": "john@example.com"
}
```

**Validation Rules**:
- `name`: Required, sanitized string.
- `phone`: Required, valid formats: `07...`, `+2547...`, `2547...`, `01...`.
- `email`: Optional, valid format.

**Response**: Newly created contact (201 Created)

---

### Task Logs

#### GET /api/v1/task_logs

Retrieve a list of task execution logs.

**Query Parameters**:
- `task_type` (string, optional): Filter by task type
- `status` (string, optional): Filter by status
- `limit` (integer, optional): Number of items to return (default: 50)

**Response** (200 OK):
```json
{
  "count": 1,
  "logs": [
    {
      "id": 123,
      "task_type": "BackupTask",
      "task_name": "Daily Backup",
      "status": "completed",
      "started_at": "2026-01-14T01:00:00Z",
      "completed_at": "2026-01-14T01:05:00Z",
      "result": "Backup successful",
      "error": null
    }
  ]
}
```

---

#### GET /api/v1/task_logs/stats

Get task execution statistics.

**Response** (200 OK):
```json
{
  "total_executions": 100,
  "completed": 95,
  "failed": 5,
  "running": 0,
  "success_rate": 95.0
}
```

---

#### POST /tasks/{id}/run

Manually trigger a task.

**Authentication**: Required

**Path Parameters**:
- `id` (string, required): Task ID

**Response** (200 OK):
```json
{
  "message": "Task 'cleanup_logs' started successfully",
  "job_id": "abc123"
}
```

---

#### PUT /tasks/{id}/toggle

Enable or disable a task.

**Authentication**: Required

**Path Parameters**:
- `id` (string, required): Task ID

**Request Body**:
```json
{
  "enabled": false
}
```

**Response** (200 OK):
```json
{
  "id": "cleanup_logs",
  "enabled": false,
  "message": "Task disabled successfully"
}
```

---

## Data Models

### Contact

```json
{
  "id": 1,
  "name": "string (2-100 chars)",
  "phone": "string (10 digits, starts with 07)",
  "email": "string (valid email, optional)",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

**Notes**:
- `phone` and `email` are encrypted at rest
- `id` is auto-generated
- `created_at` and `updated_at` are auto-managed

---

### Task

```json
{
  "id": "string (unique identifier)",
  "name": "string",
  "schedule": "string (cron expression)",
  "enabled": "boolean",
  "last_run": "ISO 8601 datetime",
  "next_run": "ISO 8601 datetime",
  "status": "string (success|failed|running)"
}
```

---

### Metric

```json
{
  "metric_type": "string (cpu|memory|disk|custom)",
  "value": "float",
  "unit": "string (percent|mb|count)",
  "timestamp": "ISO 8601 datetime"
}
```

---

## Examples

### Complete Workflow Example

#### 1. Create Contact

```bash
curl -X POST http://localhost:5000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "phone": "0703456789",
    "email": "alice@example.com"
  }'
```

#### 2. List Contacts

```bash
curl -X GET http://localhost:5000/api/v1/contacts
```

#### 3. Get Specific Contact

```bash
curl -X GET http://localhost:5000/api/v1/contacts/1
```

#### 4. Update Contact

```bash
curl -X PUT http://localhost:5000/api/v1/contacts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson Updated",
    "phone": "0703456789",
    "email": "alice.new@example.com"
  }'
```

#### 5. Delete Contact

```bash
curl -X DELETE http://localhost:5000/api/v1/contacts/1
```

---

### Python SDK Example

```python
import requests

# Base configuration
BASE_URL = "http://localhost:5000/api/v1"
headers = {"Content-Type": "application/json"}

# 1. Create contact
contact_data = {
    "name": "Bob Wilson",
    "phone": "0704567890",
    "email": "bob@example.com"
}
response = requests.post(
    f"{BASE_URL}/contacts",
    json=contact_data,
    headers=headers
)
contact = response.json()
print(f"Created contact: {contact['id']}")

# 2. Get all contacts
response = requests.get(f"{BASE_URL}/contacts", headers=headers)
contacts = response.json()["contacts"]
for contact in contacts:
    print(f"{contact['name']}: {contact['phone']}")

# 3. Get specific contact
contact_id = 1
response = requests.get(f"{BASE_URL}/contacts/{contact_id}", headers=headers)
contact = response.json()
print(contact)

# 4. Update contact
update_data = {"name": "Bob Wilson Updated"}
response = requests.put(
    f"{BASE_URL}/contacts/{contact_id}",
    json=update_data,
    headers=headers
)

# 5. Delete contact
response = requests.delete(f"{BASE_URL}/contacts/{contact_id}", headers=headers)
print(f"Status: {response.status_code}")
```

---

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api/v1';

async function main() {
  // 1. Create contact
  const contactData = {
    name: 'Charlie Brown',
    phone: '0705678901',
    email: 'charlie@example.com'
  };
  
  const createResponse = await axios.post(
    `${BASE_URL}/contacts`,
    contactData
  );
  
  const contactId = createResponse.data.id;
  console.log(`Created contact: ${contactId}`);
  
  // 2. Get all contacts
  const listResponse = await axios.get(`${BASE_URL}/contacts`);
  console.log('Contacts:', listResponse.data.contacts);
  
  // 3. Update contact
  const updateResponse = await axios.put(
    `${BASE_URL}/contacts/${contactId}`,
    { name: 'Charlie Brown Updated' }
  );
  
  // 4. Delete contact
  await axios.delete(`${BASE_URL}/contacts/${contactId}`);
  console.log('Contact deleted');
}

main().catch(console.error);
```
    contactData,
    { headers }
  );
  console.log('Created:', createResponse.data);
  
  // 3. Get all contacts
  const listResponse = await axios.get(`${BASE_URL}/contacts`, { headers });
  console.log('Contacts:', listResponse.data.contacts);
  
  // 4. Get system metrics
  const metricsResponse = await axios.get(`${BASE_URL}/metrics`);
  console.log('Metrics:', metricsResponse.data);
}

main().catch(console.error);
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Response Format**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Filtering and Sorting

### Filtering

Use query parameters to filter results:

```http
GET /api/v1/contacts?name=John&email=@example.com
```

### Sorting

Use `sort` and `order` parameters:

```http
GET /api/v1/contacts?sort=created_at&order=desc
```

**Sortable Fields**:
- `id`
- `name`
- `created_at`
- `updated_at`

---

### Metrics & Monitoring

#### GET /api/v1/metrics

Get application-level metrics (request counts, latency per endpoint).

**Authentication**: Not required

---

#### GET /api/v1/metrics/system

Get system-level metrics (CPU, Memory, Disk).

**Authentication**: Not required

---

#### GET /api/v1/logs/errors

Retrieve recent system error logs (internal visibility).

**Authentication**: Required

---

## API Versioning

The API uses URL-based versioning (`/api/v1/`). 

**Current Version**: `v1` (FROZEN)

**Governance Policy**:
- Existing fields in `v1` are never removed or renamed.
- New features are added in an additive, non-breaking manner.
- Breaking changes require the launch of `/api/v2`.

**Deprecation Readiness**:
- The system supports Header-Based signaling for planned deprecation.
- Human-readable notices are broadcast via the `/api/v1/info` endpoint.

---

## Security Best Practices

1. **Authentication**: All data-modifying requests require a valid JWT.
2. **Integrity**: Monitor the `X-Autom8-Integrity` header to ensure system health.
3. **Rate Limits**: Respect the 5,000 req/min limit to ensure shared stability.
4. **Sanitization**: All input is sanitized; all output is shaped by serializers to prevent data leakage.

---

## Support

For API issues or questions:
- **Email**: orenyalphy256@gmail.com
- **Maintainer**: Alphonce Liguori Oreny (Agent ALO)

---

*Last Updated: January 14, 2026*
