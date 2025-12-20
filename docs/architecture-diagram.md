# 📐 Architecture Diagrams - Autom8

Visual representation of the Autom8 system architecture.

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        CLI[CLI Tool]
        MOBILE[Mobile App]
        API_CLIENT[API Client]
    end
    
    subgraph "API Gateway"
        NGINX[Nginx Load Balancer]
    end
    
    subgraph "Application Layer"
        API1[API Server 1]
        API2[API Server 2]
        SCHEDULER[Scheduler Service]
    end
    
    subgraph "Business Logic"
        CONTACT[Contact Service]
        TASK[Task Service]
        METRICS[Metrics Service]
        SECURITY[Security Service]
        PERF[Performance Monitor]
    end
    
    subgraph "Data Layer"
        CACHE[Cache Layer<br/>LRU + TTL]
        DB[(PostgreSQL<br/>Database)]
        REDIS[(Redis<br/>Cache)]
    end
    
    subgraph "Infrastructure"
        LOGS[Log Files]
        BACKUP[Backup Storage]
    end
    
    WEB --> NGINX
    CLI --> NGINX
    MOBILE --> NGINX
    API_CLIENT --> NGINX
    
    NGINX --> API1
    NGINX --> API2
    
    API1 --> CONTACT
    API1 --> TASK
    API1 --> METRICS
    API2 --> CONTACT
    API2 --> TASK
    API2 --> METRICS
    
    SCHEDULER --> TASK
    
    CONTACT --> SECURITY
    TASK --> SECURITY
    CONTACT --> PERF
    TASK --> PERF
    
    CONTACT --> CACHE
    TASK --> CACHE
    METRICS --> CACHE
    
    CACHE --> DB
    CACHE --> REDIS
    
    API1 --> LOGS
    API2 --> LOGS
    SCHEDULER --> LOGS
    
    DB --> BACKUP
```

## Request Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant Nginx
    participant API
    participant Auth
    participant RateLimit
    participant Cache
    participant DB
    
    Client->>Nginx: HTTP Request
    Nginx->>API: Forward Request
    API->>Auth: Validate JWT
    Auth-->>API: User Context
    API->>RateLimit: Check Limit
    RateLimit-->>API: OK
    API->>Cache: Check Cache
    alt Cache Hit
        Cache-->>API: Cached Data
    else Cache Miss
        API->>DB: Query Database
        DB-->>API: Data
        API->>Cache: Store in Cache
    end
    API-->>Nginx: Response
    Nginx-->>Client: HTTP Response
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "API Layer"
        FLASK[Flask App]
        ROUTES[Route Handlers]
        MIDDLEWARE[Middleware]
    end
    
    subgraph "Security Layer"
        JWT[JWT Manager]
        ENCRYPT[Encryption Service]
        RATELIMIT[Rate Limiter]
    end
    
    subgraph "Business Layer"
        CONTACT_SVC[Contact Service]
        TASK_SVC[Task Service]
        METRIC_SVC[Metrics Service]
    end
    
    subgraph "Data Layer"
        ORM[SQLAlchemy ORM]
        MODELS[Data Models]
        CACHE_MGR[Cache Manager]
    end
    
    FLASK --> ROUTES
    ROUTES --> MIDDLEWARE
    MIDDLEWARE --> JWT
    MIDDLEWARE --> RATELIMIT
    
    ROUTES --> CONTACT_SVC
    ROUTES --> TASK_SVC
    ROUTES --> METRIC_SVC
    
    CONTACT_SVC --> ENCRYPT
    CONTACT_SVC --> ORM
    TASK_SVC --> ORM
    METRIC_SVC --> ORM
    
    ORM --> MODELS
    ORM --> CACHE_MGR
```

## Data Flow Diagram

```mermaid
flowchart TD
    START([Client Request]) --> AUTH{Authenticated?}
    AUTH -->|No| LOGIN[Login Required]
    AUTH -->|Yes| RATE{Rate Limit OK?}
    RATE -->|No| RATE_ERR[429 Error]
    RATE -->|Yes| VALIDATE{Valid Input?}
    VALIDATE -->|No| VAL_ERR[400 Error]
    VALIDATE -->|Yes| CACHE_CHECK{Cache Hit?}
    CACHE_CHECK -->|Yes| CACHE_RETURN[Return Cached]
    CACHE_CHECK -->|No| DB_QUERY[Query Database]
    DB_QUERY --> ENCRYPT{Needs Decryption?}
    ENCRYPT -->|Yes| DECRYPT[Decrypt Data]
    ENCRYPT -->|No| FORMAT[Format Response]
    DECRYPT --> FORMAT
    FORMAT --> CACHE_STORE[Store in Cache]
    CACHE_STORE --> RESPONSE([Return Response])
    CACHE_RETURN --> RESPONSE
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        TLS[TLS/HTTPS Layer]
        HEADERS[Security Headers]
        AUTH[Authentication Layer]
        AUTHZ[Authorization Layer]
        ENCRYPT[Encryption Layer]
        AUDIT[Audit Logging]
    end
    
    subgraph "Security Components"
        JWT_MGR[JWT Manager]
        PASS_HASH[Password Hasher]
        AES[AES-256 Encryption]
        RATE[Rate Limiter]
        SANITIZE[Input Sanitizer]
    end
    
    TLS --> HEADERS
    HEADERS --> AUTH
    AUTH --> JWT_MGR
    AUTH --> PASS_HASH
    AUTH --> AUTHZ
    AUTHZ --> ENCRYPT
    ENCRYPT --> AES
    ENCRYPT --> SANITIZE
    SANITIZE --> RATE
    RATE --> AUDIT
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer<br/>Nginx]
        
        subgraph "Application Tier"
            APP1[API Server 1<br/>Docker Container]
            APP2[API Server 2<br/>Docker Container]
            APP3[API Server 3<br/>Docker Container]
        end
        
        subgraph "Data Tier"
            DB_PRIMARY[(PostgreSQL<br/>Primary)]
            DB_REPLICA[(PostgreSQL<br/>Read Replica)]
            REDIS_CLUSTER[Redis Cluster]
        end
        
        subgraph "Monitoring"
            LOGS[Centralized Logging]
            METRICS[Metrics Collection]
            ALERTS[Alert Manager]
        end
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> DB_PRIMARY
    APP2 --> DB_PRIMARY
    APP3 --> DB_PRIMARY
    
    APP1 --> DB_REPLICA
    APP2 --> DB_REPLICA
    APP3 --> DB_REPLICA
    
    APP1 --> REDIS_CLUSTER
    APP2 --> REDIS_CLUSTER
    APP3 --> REDIS_CLUSTER
    
    APP1 --> LOGS
    APP2 --> LOGS
    APP3 --> LOGS
    
    LOGS --> METRICS
    METRICS --> ALERTS
```

## Database Schema Diagram

```mermaid
erDiagram
    CONTACT ||--o{ AUDIT_LOG : "triggers"
    TASK ||--o{ TASK_EXECUTION : "has"
    METRIC ||--o{ METRIC_AGGREGATE : "aggregates to"
    
    CONTACT {
        int id PK
        string name
        string phone_encrypted
        string email_encrypted
        datetime created_at
        datetime updated_at
    }
    
    TASK {
        int id PK
        string name
        string schedule
        boolean enabled
        datetime last_run
        datetime next_run
        string status
    }
    
    METRIC {
        int id PK
        string metric_type
        float value
        string unit
        datetime timestamp
    }
    
    AUDIT_LOG {
        int id PK
        string action
        string user
        string resource_type
        int resource_id
        string details
        datetime timestamp
    }
    
    TASK_EXECUTION {
        int id PK
        int task_id FK
        datetime started_at
        datetime completed_at
        string status
        string error_message
    }
    
    METRIC_AGGREGATE {
        int id PK
        string metric_type
        float avg_value
        float min_value
        float max_value
        datetime period_start
        datetime period_end
    }
```

## Caching Strategy Diagram

```mermaid
graph TD
    REQUEST[API Request] --> L1{L1 Cache<br/>In-Memory LRU}
    L1 -->|Hit| RETURN1[Return Cached]
    L1 -->|Miss| L2{L2 Cache<br/>Redis TTL}
    L2 -->|Hit| STORE_L1[Store in L1]
    STORE_L1 --> RETURN2[Return Cached]
    L2 -->|Miss| DB[Query Database]
    DB --> STORE_L2[Store in L2]
    STORE_L2 --> STORE_L1
    
    style L1 fill:#90EE90
    style L2 fill:#87CEEB
    style DB fill:#FFB6C1
```

## Scheduler Architecture

```mermaid
graph TB
    SCHEDULER[APScheduler] --> JOBSTORE[(Job Store<br/>Database)]
    SCHEDULER --> EXECUTOR1[Thread Executor 1]
    SCHEDULER --> EXECUTOR2[Thread Executor 2]
    SCHEDULER --> EXECUTOR3[Thread Executor 3]
    
    EXECUTOR1 --> JOB1[Cleanup Job]
    EXECUTOR2 --> JOB2[Metrics Job]
    EXECUTOR3 --> JOB3[Backup Job]
    
    JOB1 --> MONITOR[Job Monitor]
    JOB2 --> MONITOR
    JOB3 --> MONITOR
    
    MONITOR --> ALERT{Job Failed?}
    ALERT -->|Yes| NOTIFY[Send Alert]
    ALERT -->|No| LOG[Log Success]
```

## Monitoring Architecture

```mermaid
graph LR
    subgraph "Application"
        APP[Autom8 API]
        METRICS_COL[Metrics Collector]
        LOG_WRITER[Log Writer]
    end
    
    subgraph "Collection"
        LOGS[Log Aggregator]
        METRICS_DB[(Metrics Store)]
    end
    
    subgraph "Visualization"
        DASHBOARD[Monitoring Dashboard]
        ALERTS[Alert System]
    end
    
    APP --> METRICS_COL
    APP --> LOG_WRITER
    
    METRICS_COL --> METRICS_DB
    LOG_WRITER --> LOGS
    
    METRICS_DB --> DASHBOARD
    LOGS --> DASHBOARD
    
    DASHBOARD --> ALERTS
```

## Network Topology

```mermaid
graph TB
    INTERNET([Internet]) --> FIREWALL[Firewall]
    FIREWALL --> DMZ[DMZ]
    
    subgraph DMZ
        LB[Load Balancer<br/>Public IP]
    end
    
    DMZ --> PRIVATE[Private Network]
    
    subgraph PRIVATE
        APP_SUBNET[Application Subnet<br/>10.0.1.0/24]
        DB_SUBNET[Database Subnet<br/>10.0.2.0/24]
        
        APP_SUBNET --> API1[API Server 1<br/>10.0.1.10]
        APP_SUBNET --> API2[API Server 2<br/>10.0.1.11]
        
        DB_SUBNET --> DB[PostgreSQL<br/>10.0.2.10]
        DB_SUBNET --> REDIS[Redis<br/>10.0.2.11]
    end
    
    API1 --> DB
    API2 --> DB
    API1 --> REDIS
    API2 --> REDIS
```

## CI/CD Pipeline Flow

```mermaid
graph LR
    COMMIT[Git Commit] --> TRIGGER[Pipeline Trigger]
    TRIGGER --> LINT[Lint Code]
    LINT --> TEST[Run Tests]
    TEST --> SECURITY[Security Scan]
    SECURITY --> BUILD[Build Docker Image]
    BUILD --> DEPLOY_STAGE[Deploy to Staging]
    DEPLOY_STAGE --> SMOKE[Smoke Tests]
    SMOKE --> APPROVE{Manual Approval}
    APPROVE -->|Yes| DEPLOY_PROD[Deploy to Production]
    APPROVE -->|No| ROLLBACK[Rollback]
    DEPLOY_PROD --> VERIFY[Verify Deployment]
```

---

## Legend

### Colors
- 🟢 Green: Cache/Fast operations
- 🔵 Blue: Services/Components
- 🔴 Red: Database/Persistent storage
- 🟡 Yellow: Security components
- 🟣 Purple: Monitoring/Logging

### Symbols
- `[]` Rectangle: Process/Service
- `()` Rounded: Start/End points
- `{}` Diamond: Decision points
- `[(Database)]` Cylinder: Data storage

---

*For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)*
