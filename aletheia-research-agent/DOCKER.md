# Docker Deployment Guide

This guide covers how to run Aletheia Research Agent with the Agent Discovery System using Docker Compose.

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual API keys
nano .env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access Applications

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **Backend Health**: http://localhost:8001/health
- **pgAdmin** (optional): http://localhost:5050
- **Redis Commander** (optional): http://localhost:8081

## Docker Compose Services

### Core Services

#### Frontend (Next.js)
- **Port**: 3001
- **Auto-reload**: Yes (in development)
- **Volumes**: Mounted source code

#### Backend (FastAPI)
- **Port**: 8001
- **Auto-reload**: Yes (in development)
- **Volumes**: Mounted source code

#### Redis
- **Port**: 6379
- **Purpose**: Caching & rate limiting
- **Data**: Persisted in volume `redis-data`

#### PostgreSQL (Local Development)
- **Port**: 5432
- **Database**: aletheia
- **User**: aletheia
- **Password**: aletheia
- **Data**: Persisted in volume `postgres-data`

### Optional Services

#### Discovery Scheduler
Runs automated agent discovery jobs daily at 2 AM.

```bash
# Start with scheduler
docker-compose --profile scheduler up -d

# View scheduler logs
docker-compose -f docker-compose.yml --profile scheduler logs -f discovery-scheduler
```

#### pgAdmin
PostgreSQL management interface.

```bash
# Start with pgAdmin
docker-compose --profile admin up -d

# Access at http://localhost:5050
# Login: admin@aletheia.com / admin
# Add connection:
#   Host: postgres
#   Port: 5432
#   Database: aletheia
#   User: aletheia
#   Password: aletheia
```

#### Redis Commander
Redis management interface.

```bash
# Start with Redis Commander
docker-compose --profile admin up -d

# Access at http://localhost:8081
```

## Development Mode

For development with hot reload:

```bash
# Use development override
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Required
- `MINIMAX_API_KEY` - LLM provider
- `SUPABASE_URL` - Database URL
- `SUPABASE_ANON_KEY` - Public API key
- `SUPABASE_SERVICE_ROLE_KEY` - Admin API key
- `TAVILY_API_KEY` - Web search

### Optional (Agent Discovery)
- `GROK_API_KEY` - Fast web search (get from x.ai)
- `FIRECRAWL_API_KEY` - Deep scraping (get from firecrawl.dev)

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Service
```bash
docker-compose restart backend
```

### Rebuild Services
```bash
docker-compose up -d --build

# Force rebuild
docker-compose up -d --build --force-recreate
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (deletes all data!)
docker-compose down -v

# Remove everything
docker-compose down -v --rmi all
```

### Database Operations

#### Run Migration
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U aletheia -d aletheia

# Run schema
docker-compose exec postgres psql -U aletheia -d aletheia -f /docker-entrypoint-initdb.d/01-schema.sql
```

#### Backup Database
```bash
docker-compose exec postgres pg_dump -U aletheia aletheia > backup.sql
```

#### Restore Database
```bash
cat backup.sql | docker-compose exec -T postgres psql -U aletheia aletheia
```

## Production Deployment

### 1. Update Environment
```bash
ENVIRONMENT=production
# Use secure JWT secret
JWT_SECRET_KEY=$(openssl rand -base64 32)
```

### 2. Disable Debug
```bash
ENVIRONMENT=production
```

### 3. Use External Services
- **PostgreSQL**: Use managed service (Supabase, RDS, etc.)
- **Redis**: Use managed Redis (Upstash, Redis Cloud, etc.)

### 4. Deploy
```bash
# Build without dev dependencies
docker-compose -f docker-compose.yml up -d --build
```

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing .env file
# - Invalid API keys
# - Port already in use
```

### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Verify connection
docker-compose exec backend python -c "from config import supabase; print('OK')"
```

### Redis connection errors
```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Frontend not connecting to backend
```bash
# Verify backend is running
curl http://localhost:8001/health

# Check environment
docker-compose exec frontend env | grep NEXT_PUBLIC_API_URL
```

### Discovery system not working
```bash
# Check if enabled
docker-compose exec backend python -c "from config import settings; print(settings.discovery_enabled)"

# Check API keys
docker-compose exec backend env | grep -E "(GROK|FIRECRAWL)"
```

## Network Architecture

```
┌─────────────────────────────────────┐
│         Docker Network              │
│         (172.20.0.0/16)             │
│                                     │
│  ┌──────────────┐  ┌──────────────┐│
│  │   Frontend   │  │    Backend   ││
│  │   :3001      │  │    :8001     ││
│  └──────┬───────┘  └──────┬───────┘│
│         │                  │         │
│  ┌──────▼───────┐  ┌──────▼───────┐│
│  │   Redis      │  │  PostgreSQL  ││
│  │   :6379      │  │    :5432     ││
│  └──────────────┘  └──────────────┘│
└─────────────────────────────────────┘
```

## Volumes

- `postgres-data` - PostgreSQL database files
- `redis-data` - Redis persistence
- `pgadmin-data` - pgAdmin configuration

## Security Notes

⚠️ **Important for Production**:
1. Change default passwords
2. Use secure JWT secrets
3. Enable HTTPS/SSL
4. Use secrets management (Docker Swarm, Kubernetes, etc.)
5. Update CORS origins
6. Use managed database services
7. Enable database SSL
8. Regular security updates

## Performance Tuning

### Backend
```yaml
environment:
  - RATE_LIMIT_PER_MINUTE=100
  - PYTHONUNBUFFERED=1
```

### Frontend
```yaml
environment:
  - NODE_OPTIONS=--max-old-space-size=4096
```

### PostgreSQL
```yaml
command: postgres -c shared_buffers=256MB -c effective_cache_size=1GB
```

### Redis
```yaml
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend
docker-compose up -d --scale backend=3

# Use nginx or similar for load balancing
```

### Database
- Use external managed PostgreSQL for production
- Enable connection pooling (pgBouncer)
- Read replicas for scaling reads

### Redis
- Redis Cluster for high availability
- Redis Sentinel for failover

## Monitoring

### Logs
```bash
# Centralized logging
docker-compose logs -f --tail=100

# JSON logs for parsing
docker-compose logs -f --format=json
```

### Health Checks
All services have health checks defined:
```bash
# Check health
docker-compose ps

# Inspect health status
docker inspect aletheia-backend | grep -A 10 Health
```

### Metrics
Consider adding:
- Prometheus metrics endpoint
- Grafana dashboard
- Application performance monitoring (APM)
