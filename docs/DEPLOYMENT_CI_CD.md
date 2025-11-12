# Aletheia Research Agent - Production Deployment Guide

## Table of Contents
1. [Local Development Testing](#local-development-testing)
2. [OVHcloud Public VM Deployment](#ovhcloud-public-vm-deployment)
3. [Docker Compose Deployment](#docker-compose-deployment)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development Testing

### Quick Start

1. **Clone and Setup**:
```bash
git clone <your-repo>
cd aletheia-research-agent

# Install Python dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Node.js dependencies
cd ../frontend
npm install  # or pnpm install
```

2. **Environment Configuration**:

Create `backend/.env`:
```env
# Supabase (obtained from supabase_auth toolkit)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# API Keys (REQUIRED for full functionality)
MINIMAX_API_KEY=your_minimax_api_key
TAVILY_API_KEY=your_tavily_api_key

# Redis (for local dev, use docker)
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=dev_secret_key_change_in_production
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Start Services**:

Terminal 1 - Redis (for rate limiting):
```bash
docker run -d --name redis-dev -p 6379:6379 redis:7.2-alpine
```

Terminal 2 - Backend:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 3 - Frontend:
```bash
cd frontend
npm run dev
```

4. **Access Application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Testing Different Scenarios

#### 1. API Key Testing

**Without API Keys** (Fallback mode):
```bash
# Start without MINIMAX_API_KEY or TAVILY_API_KEY
# Application will run with mock responses and clear instructions
```

**With MiniMax API Only**:
```bash
# Set MINIMAX_API_KEY in backend/.env
# Application will use real LLM but mock search results
```

**With Both APIs** (Full functionality):
```bash
# Set both MINIMAX_API_KEY and TAVILY_API_KEY
# Complete research functionality available
```

#### 2. Database Testing

**Local Testing**:
```bash
# Supabase provides local development with CLI
npx supabase start
```

**Production Testing**:
```bash
# Test against production Supabase project
# Ensure all tables exist and RLS policies are active
```

#### 3. Performance Testing

**Load Testing** (optional - install k6):
```javascript
// load-test.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const response = http.post('http://localhost:8000/api/chat/send', {
    message: 'Test research query',
    user_id: 'test-user-id'
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2000ms': (r) => r.timings.duration < 2000,
  });
}
```

Run with: `k6 run load-test.js`

---

## OVHcloud Public VM Deployment

### Prerequisites

- OVHcloud Public VM instance (Ubuntu 22.04 LTS recommended)
- Domain name (optional, for SSL)
- Access to DNS management

### Step 1: Server Setup

1. **Connect to VM**:
```bash
ssh root@your-server-ip
```

2. **Update System**:
```bash
apt update && apt upgrade -y
apt install -y curl wget git unzip htop nano docker.io docker-compose
```

3. **Create User**:
```bash
adduser aletheia
usermod -aG sudo,docker aletheia
su - aletheia
```

### Step 2: Application Deployment

1. **Clone Repository**:
```bash
git clone <your-git-repo> /opt/aletheia
cd /opt/aletheia
```

2. **Setup Environment Variables**:
```bash
# Backend environment
cat > backend/.env << 'EOF'
# Supabase Configuration
SUPABASE_URL=your_production_supabase_url
SUPABASE_ANON_KEY=your_production_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_production_supabase_service_role_key

# API Keys (REQUIRED)
MINIMAX_API_KEY=your_minimax_api_key
TAVILY_API_KEY=your_tavily_api_key

# Security
JWT_SECRET_KEY=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20
REDIS_URL=redis://redis:6379/0

# Environment
ENVIRONMENT=production
EOF

# Frontend environment
cat > frontend/.env.production << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=your_production_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_production_supabase_anon_key
NEXT_PUBLIC_API_URL=https://your-domain.com
EOF
```

3. **Docker Compose Deployment**:
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: aletheia-backend
    restart: unless-stopped
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      - redis
    networks:
      - aletheia-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    container_name: aletheia-frontend
    restart: unless-stopped
    env_file:
      - ./frontend/.env.production
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - aletheia-network

  redis:
    image: redis:7.2-alpine
    container_name: aletheia-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - aletheia-network

  nginx:
    image: nginx:alpine
    container_name: aletheia-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - aletheia-network

volumes:
  redis-data:

networks:
  aletheia-network:
    driver: bridge
```

4. **Nginx Configuration**:
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=20r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Auth endpoints with stricter rate limiting
        location /api/auth/ {
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Step 3: SSL Certificate (Let's Encrypt)

1. **Install Certbot**:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

2. **Generate Certificate**:
```bash
sudo certbot --nginx -d your-domain.com
```

3. **Auto-renewal Setup**:
```bash
sudo crontab -e
# Add line:
0 12 * * * /usr/bin/certbot renew --quiet
```

### Step 4: Deploy Application

```bash
# Build and start services
docker-compose -f docker-compose.production.yml up -d --build

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Check service status
docker-compose -f docker-compose.production.yml ps
```

### Step 5: Monitoring Setup

1. **Log Rotation**:
```bash
# /etc/logrotate.d/aletheia
/opt/aletheia/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 aletheia aletheia
}
```

2. **Health Check Script**:
```bash
#!/bin/bash
# health-check.sh

API_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"

# Check backend
if curl -f $API_URL >/dev/null 2>&1; then
    echo "Backend: OK"
else
    echo "Backend: FAIL"
    docker-compose -f docker-compose.production.yml restart backend
fi

# Check frontend
if curl -f $FRONTEND_URL >/dev/null 2>&1; then
    echo "Frontend: OK"
else
    echo "Frontend: FAIL"
    docker-compose -f docker-compose.production.yml restart frontend
fi
```

3. **Systemd Service for Health Checks**:
```bash
sudo tee /etc/systemd/system/aletheia-health.service > /dev/null <<EOF
[Unit]
Description=Aletheia Health Check
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=aletheia
Group=aletheia
ExecStart=/opt/aletheia/health-check.sh

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable aletheia-health
sudo systemctl start aletheia-health

# Add to crontab for regular checks
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/aletheia/health-check.sh >> /var/log/aletheia-health.log 2>&1") | crontab -
```

---

## Docker Compose Deployment

### Development Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    env_file:
      - ./backend/.env
    depends_on:
      - redis
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    env_file:
      - ./frontend/.env.local
    depends_on:
      - backend
    command: npm run dev

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
```

### Production Commands

```bash
# Start production services
docker-compose -f docker-compose.production.yml up -d

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Update services
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# Backup database
docker exec aletheia-postgres pg_dump -U postgres aletheia > backup-$(date +%Y%m%d).sql

# Scale backend for load
docker-compose -f docker-compose.production.yml up -d --scale backend=3
```

---

## 🚀 Production Deployment Options

### Option 1: Vercel + Railway (Recommended)

**Frontend Deployment (Vercel):**
```bash
# Build and deploy frontend
cd frontend
npm run build
vercel --prod

# Configure environment variables in Vercel dashboard:
NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
```

**Backend Deployment (Railway):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
cd backend
railway deploy

# Set environment variables in Railway dashboard:
MINIMAX_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DATABASE_URL=your_supabase_url
```

**Supabase Configuration:**
- Database: Already configured
- Storage: Already set up
- Auth: Already configured
- Edge Functions: Ready for deployment

---

### Option 2: Docker Compose (Self-Hosted)

**OVH Cloud Deployment:**

1. **Provision Ubuntu 22.04 Server**
   - Minimum: 4 vCPU, 8GB RAM
   - Open ports: 80, 443, 3000, 8000

2. **Run Setup Script:**
```bash
#!/bin/bash
set -e

echo "=== Aletheia Research Agent - OVH Setup ==="

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose-plugin

# Install Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Clone repository
git clone https://github.com/yourorg/aletheia-research-agent.git
cd aletheia-research-agent

# Create environment file
cat > .env << EOF
# API Keys - Get these from respective platforms
MINIMAX_API_KEY=your_minimax_key_here
TAVILY_API_KEY=your_tavily_key_here

# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/aletheia
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)

# Application
APP_ENV=production
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com
EOF

# Create production environment
sudo tee /etc/nginx/sites-available/aletheia << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for real-time features
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location /static {
        alias /var/www/aletheia/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/aletheia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com \
    --non-interactive --agree-tos --email admin@yourdomain.com

# Start services
docker compose -f docker-compose.prod.yml up -d

# Setup monitoring
docker compose -f docker-compose.monitoring.yml up -d

echo "=== Setup Complete ==="
echo "Access your app at: https://yourdomain.com"
echo "API Docs: https://yourdomain.com/docs"
```

3. **Configure DNS:**
```
A Record: yourdomain.com → YOUR_OVH_IP
CNAME: www.yourdomain.com → yourdomain.com
```

4. **SSL Certificate Auto-Renewal:**
```bash
# Add to crontab
0 12 * * * /usr/bin/certbot renew --quiet
```

---

### Option 3: Kubernetes (Enterprise)

**Helm Chart:**

Create `aletheia-helm-chart/values.yaml`:

```yaml
# Global configuration
global:
  domain: "yourdomain.com"
  ingressClassName: "nginx"
  
# Frontend (Next.js)
frontend:
  image:
    repository: yourorg/aletheia-frontend
    tag: "latest"
  replicas: 2
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  env:
    - name: NEXT_PUBLIC_API_URL
      value: "https://api.yourdomain.com"

# Backend (FastAPI)
backend:
  image:
    repository: yourorg/aletheia-backend
    tag: "latest"
  replicas: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 1024Mi
  env:
    - name: MINIMAX_API_KEY
      valueFrom:
        secretKeyRef:
          name: aletheia-secrets
          key: minimax-api-key
    - name: TAVILY_API_KEY
      valueFrom:
        secretKeyRef:
          name: aletheia-secrets
          key: tavily-api-key

# Database (PostgreSQL)
postgres:
  enabled: true
  auth:
    postgresPassword: "securepassword"
  primary:
    persistence:
      enabled: true
      size: 20Gi
  metrics:
    enabled: true

# Redis
redis:
  enabled: true
  master:
    persistence:
      enabled: true
      size: 5Gi

# Ingress
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "20"
  hosts:
    - host: yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: aletheia-tls
      hosts:
        - yourdomain.com
```

**Deploy:**
```bash
# Install Aletheia
helm install aletheia ./aletheia-helm-chart \
  --set global.domain=yourdomain.com

# Update
helm upgrade aletheia ./aletheia-helm-chart

# Uninstall
helm uninstall aletheia
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

### .github/workflows/ci.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Testing
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
        node-version: [18, 20]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    # Backend tests
    - name: Install backend dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov black flake8 mypy
    
    - name: Lint backend code
      run: |
        cd backend
        black --check .
        flake8 .
        mypy .
    
    - name: Run backend tests
      run: |
        cd backend
        pytest --cov=. --cov-report=xml --cov-report=term
    
    - name: Upload backend coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
    
    # Frontend tests
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Lint frontend code
      run: |
        cd frontend
        npm run lint
        npm run type-check
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm run test -- --coverage --watchAll=false
    
    - name: Upload frontend coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info
        flags: frontend

  # Security scanning
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  # Build and push images
  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta-frontend
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ${{ steps.meta-frontend.outputs.tags }}
        labels: ${{ steps.meta-frontend.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Extract metadata
      id: meta-backend
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: ${{ steps.meta-backend.outputs.tags }}
        labels: ${{ steps.meta-backend.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # Deploy to staging
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        RAILWAY_SERVICE_ID: ${{ secrets.RAILWAY_STAGING_SERVICE }}
      run: |
        railway deploy --service ${{ env.RAILWAY_SERVICE_ID }}
    
    - name: Run integration tests
      env:
        STAGING_URL: ${{ secrets.STAGING_URL }}
      run: |
        npm install -g @playwright/test
        cd tests/e2e
        npx playwright install
        npx playwright test --config=staging.config.js

  # Deploy to production
  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        RAILWAY_SERVICE_ID: ${{ secrets.RAILWAY_PROD_SERVICE }}
      run: |
        railway deploy --service ${{ env.RAILWAY_SERVICE_ID }}
    
    - name: Health check
      env:
        PRODUCTION_URL: ${{ secrets.PRODUCTION_URL }}
      run: |
        curl -f ${{ env.PRODUCTION_URL }}/api/health
    
    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        text: |
          Aletheia Research Agent deployed to production
          URL: ${{ secrets.PRODUCTION_URL }}
      if: always()
```

---

## 📋 Environment Configuration

### Production Environment Variables

**Backend (.env):**
```env
# API Keys
MINIMAX_API_KEY=sk-your-minimax-key
TAVILY_API_KEY=your-tavily-key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/aletheia_prod
REDIS_URL=redis://user:pass@redis-host:6379/0

# Security
JWT_SECRET_KEY=your-jwt-secret-key
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_ENV=production
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20
RATE_LIMIT_PER_HOUR=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# External Services
SENTRY_DSN=your-sentry-dsn
SENTRY_ENVIRONMENT=production
```

**Frontend (.env.production):**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_SENTRY_DSN=your-frontend-sentry-dsn
```

---

## 🔧 Monitoring & Observability

### Docker Compose with Monitoring

**docker-compose.monitoring.yml:**
```yaml
version: '3.9'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"

volumes:
  grafana-storage:
```

---

## 🛡️ Security Checklist

- [ ] HTTPS enforced (Let's Encrypt)
- [ ] API rate limiting configured (20/minute)
- [ ] JWT tokens with short expiry (15 min)
- [ ] Input sanitization (XSS prevention)
- [ ] CORS properly configured
- [ ] Database RLS enabled (Supabase)
- [ ] Secrets rotated regularly
- [ ] Security headers configured
- [ ] Regular dependency updates
- [ ] Vulnerability scanning enabled

---

## 📊 Performance Optimization

**Frontend:**
- Next.js static optimization
- Image optimization
- Bundle size monitoring
- CDN configuration
- Service worker caching

**Backend:**
- Database indexing
- Redis caching strategy
- Connection pooling
- Async task processing (Celery)
- API response compression

**Infrastructure:**
- Load balancing
- Auto-scaling
- Health checks
- Monitoring alerts
- Log aggregation

---

## 🚨 Troubleshooting

### Common Issues

**1. API Keys Not Working:**
```bash
# Check environment variables
docker compose exec backend env | grep API_KEY

# Restart services
docker compose restart backend
```

**2. Database Connection Failed:**
```bash
# Check Supabase connection
docker compose exec backend python -c "import os; print(os.getenv('DATABASE_URL'))"

# Test connection
docker compose exec backend python -c "from backend.database.connection import test_connection; print(test_connection())"
```

**3. Web Search Not Working:**
- Verify Tavily API key quota
- Check network connectivity
- Review rate limiting logs

**4. Frontend Build Failed:**
```bash
# Clear cache and rebuild
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Monitoring Commands

```bash
# View application logs
docker compose logs -f backend
docker compose logs -f frontend

# Monitor resource usage
docker stats

# Check service health
curl -f http://localhost:8000/api/health
curl -f http://localhost:3000/api/health

# Database migrations
docker compose exec backend python -m alembic upgrade head
```

---

## 📞 Support & Maintenance

**Regular Maintenance:**
- Weekly dependency updates
- Monthly security patches
- Quarterly performance review
- Annual security audit

**Backup Strategy:**
- Database: Automated daily backups (Supabase)
- Files: Supabase storage replication
- Configuration: Git version control

**Monitoring Alerts:**
- API response time >2s
- Error rate >1%
- Database connection failures
- Memory usage >80%
- Disk usage >85%

---

This deployment guide ensures your Aletheia Research Agent runs reliably in production with enterprise-grade security, monitoring, and scalability.