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

### JWT Token Authentication

Most endpoints require JWT authentication. Include the token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
```

### Obtaining Tokens

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

### Refreshing Tokens

```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

---

## Rate Limiting

**Default Rate Limit**: 200 requests per minute

**Override Rate Limit**: 5000 requests per minute (for specific endpoints)

**Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp)

**Rate Limit Exceeded Response**:
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  },
  "timestamp": "2025-12-20T14:42:00Z"
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
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Endpoints

### Health & Status

#### GET /health

Check API health status.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-20T14:42:00Z",
  "version": "1.0.0",
  "uptime": 3600
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

#### GET /contacts

Retrieve all contacts.

**Authentication**: Required

**Query Parameters**:
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 20, max: 100)
- `sort` (string, optional): Sort field (default: "created_at")
- `order` (string, optional): Sort order - "asc" or "desc" (default: "desc")

**Example Request**:
```http
GET /api/v1/contacts?page=1&per_page=10&sort=name&order=asc
Authorization: Bearer <token>
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
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 45,
    "pages": 5
  }
}
```

---

#### GET /contacts/{id}

Retrieve a specific contact by ID.

**Authentication**: Required

**Path Parameters**:
- `id` (integer, required): Contact ID

**Example Request**:
```http
GET /api/v1/contacts/1
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "0701234567",
  "email": "john@example.com",
  "created_at": "2025-12-20T10:00:00Z",
  "updated_at": "2025-12-20T10:00:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "Not Found",
  "message": "Contact with ID 1 not found"
}
```

---

#### POST /contacts

Create a new contact.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "Jane Smith",
  "phone": "0702345678",
  "email": "jane@example.com"
}
```

**Validation Rules**:
- `name`: Required, 2-100 characters
- `phone`: Required, valid phone format (10 digits starting with 07)
- `email`: Optional, valid email format

**Response** (201 Created):
```json
{
  "id": 2,
  "name": "Jane Smith",
  "phone": "0702345678",
  "email": "jane@example.com",
  "created_at": "2025-12-20T14:42:00Z",
  "updated_at": "2025-12-20T14:42:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Validation Error",
  "message": "Invalid input data",
  "details": {
    "phone": "Phone number must be 10 digits starting with 07"
  }
}
```

**Error Response** (409 Conflict):
```json
{
  "error": "Conflict",
  "message": "Contact with phone 0702345678 already exists"
}
```

---

#### PUT /contacts/{id}

Update an existing contact.

**Authentication**: Required

**Path Parameters**:
- `id` (integer, required): Contact ID

**Request Body**:
```json
{
  "name": "Jane Smith Updated",
  "phone": "0702345678",
  "email": "jane.new@example.com"
}
```

**Response** (200 OK):
```json
{
  "id": 2,
  "name": "Jane Smith Updated",
  "phone": "0702345678",
  "email": "jane.new@example.com",
  "created_at": "2025-12-20T14:42:00Z",
  "updated_at": "2025-12-20T15:00:00Z"
}
```

---

#### DELETE /contacts/{id}

Delete a contact.

**Authentication**: Required

**Path Parameters**:
- `id` (integer, required): Contact ID

**Response** (204 No Content):
```
(No content)
```

**Error Response** (404 Not Found):
```json
{
  "error": "Not Found",
  "message": "Contact with ID 999 not found"
}
```

---

### Performance

#### GET /performance/stats

Get performance statistics.

**Authentication**: Not required

**Response** (200 OK):
```json
{
  "request_count": 1523,
  "average_response_time": 45.2,
  "p50_response_time": 38.5,
  "p95_response_time": 95.3,
  "p99_response_time": 150.7,
  "error_rate": 0.02,
  "cache_hit_rate": 0.85
}
```

---

#### GET /performance/profile

Get detailed performance profile.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "endpoints": [
    {
      "path": "/api/v1/contacts",
      "method": "GET",
      "avg_time": 42.5,
      "call_count": 450,
      "error_count": 2
    }
  ],
  "slowest_queries": [
    {
      "query": "SELECT * FROM contacts WHERE...",
      "duration": 125.3,
      "count": 5
    }
  ]
}
```

---

### Tasks (Scheduler)

#### GET /tasks

List all scheduled tasks.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "cleanup_logs",
      "name": "Log Cleanup",
      "schedule": "0 2 * * *",
      "enabled": true,
      "last_run": "2025-12-20T02:00:00Z",
      "next_run": "2025-12-21T02:00:00Z",
      "status": "success"
    }
  ]
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

#### 1. Authenticate

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

#### 2. Create Contact

```bash
curl -X POST http://localhost:5000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Alice Johnson",
    "phone": "0703456789",
    "email": "alice@example.com"
  }'
```

#### 3. List Contacts

```bash
curl -X GET http://localhost:5000/api/v1/contacts \
  -H "Authorization: Bearer <token>"
```

#### 4. Update Contact

```bash
curl -X PUT http://localhost:5000/api/v1/contacts/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Alice Johnson Updated",
    "phone": "0703456789",
    "email": "alice.new@example.com"
  }'
```

#### 5. Delete Contact

```bash
curl -X DELETE http://localhost:5000/api/v1/contacts/1 \
  -H "Authorization: Bearer <token>"
```

---

### Python SDK Example

```python
import requests

# Base configuration
BASE_URL = "http://localhost:5000/api/v1"
headers = {"Content-Type": "application/json"}

# 1. Authenticate
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "password"}
)
token = response.json()["access_token"]
headers["Authorization"] = f"Bearer {token}"

# 2. Create contact
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

# 3. Get all contacts
response = requests.get(f"{BASE_URL}/contacts", headers=headers)
contacts = response.json()["contacts"]
for contact in contacts:
    print(f"{contact['name']}: {contact['phone']}")

# 4. Get specific contact
contact_id = 1
response = requests.get(f"{BASE_URL}/contacts/{contact_id}", headers=headers)
contact = response.json()
print(contact)

# 5. Update contact
update_data = {"name": "Bob Wilson Updated"}
response = requests.put(
    f"{BASE_URL}/contacts/{contact_id}",
    json=update_data,
    headers=headers
)

# 6. Delete contact
response = requests.delete(f"{BASE_URL}/contacts/{contact_id}", headers=headers)
print(f"Status: {response.status_code}")
```

---

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api/v1';

async function main() {
  // 1. Authenticate
  const authResponse = await axios.post(`${BASE_URL}/auth/login`, {
    username: 'admin',
    password: 'password'
  });
  
  const token = authResponse.data.access_token;
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
  
  // 2. Create contact
  const contactData = {
    name: 'Charlie Brown',
    phone: '0705678901',
    email: 'charlie@example.com'
  };
  
  const createResponse = await axios.post(
    `${BASE_URL}/contacts`,
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

## Webhooks (Future Feature)

*Coming soon: Webhook support for real-time notifications*

---

## API Versioning

The API uses URL-based versioning (`/api/v1/`). When breaking changes are introduced, a new version will be released (`/api/v2/`) while maintaining backward compatibility with v1.

**Current Version**: v1
**Deprecation Policy**: Versions are supported for 12 months after deprecation notice

---

## Security Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (never in localStorage for web apps)
3. **Implement token refresh** before expiration
4. **Validate all input** on client side
5. **Handle errors gracefully**
6. **Respect rate limits**
7. **Use environment variables** for sensitive data

---

## Support

For API issues or questions:
- **Documentation**: [Full Docs](../README.md)
- **Issues**: [GitHub Issues](https://github.com/orenyalphy256-glitch/op-alpha-systems-automation/issues)
- **Email**: orenyalphy256@gmail.com

---

*Last Updated: December 20, 2025*
