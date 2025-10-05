# KEF Teacher Dashboard - Production Deployment Guide

## Quick Start

### Automatic Setup (Recommended)

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Install Python 3.8+**
   - Download from [python.org](https://python.org)
   - Verify: `python --version`

2. **Clone/Download Project**
   ```bash
   # If using git:
   git clone <repository-url>
   cd kef-teacher-dashboard
   
   # Or extract from zip file
   ```

3. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Activate it:
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file and set:
   SECRET_KEY=your-super-secure-random-32-character-key
   ```

6. **Initialize Database**
   ```bash
   python -c "from app import create_app; app = create_app('production'); app.app_context().push(); app.db_manager.init_database()"
   ```

## Running the Application

### Development Mode
```bash
python run.py
```
Access at: http://localhost:5000

### Production Mode (Recommended)
```bash
# Using Gunicorn (Linux/Mac):
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app

# Using Gunicorn (Windows):
python -m gunicorn --bind 0.0.0.0:5000 --workers 4 run:app

# Or using Python (not recommended for production):
FLASK_ENV=production python run.py
```

## Server Deployment

### Option 1: Simple VPS/Cloud Server

1. **Upload files to server**
2. **Run setup script**
3. **Configure reverse proxy (Nginx example):**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Serve static files directly
    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

4. **Create systemd service (Linux):**

```ini
# /etc/systemd/system/kef-dashboard.service
[Unit]
Description=KEF Teacher Dashboard
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
ExecStart=/path/to/your/app/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable kef-dashboard
sudo systemctl start kef-dashboard
```

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p logs instance

ENV FLASK_ENV=production
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data.db:/app/data.db
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secure-secret-key
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

### Option 3: Platform as a Service (PaaS)

**Heroku:**
1. Create `Procfile`:
   ```
   web: gunicorn run:app
   ```
2. Deploy with Heroku CLI

**Railway, Render, etc.:**
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn run:app`
- Set environment variables

## Configuration

### Environment Variables (.env file)

```bash
# Required
SECRET_KEY=your-32-character-secure-random-key
FLASK_ENV=production

# Optional
DATABASE_URL=sqlite:///data.db  # Or PostgreSQL URL for larger deployments
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
LOG_LEVEL=INFO

# For larger deployments
REDIS_URL=redis://localhost:6379/0  # For session storage and rate limiting
```

### Database Options

**SQLite (Default - Good for small to medium use):**
```bash
DATABASE_URL=sqlite:///data.db
```

**PostgreSQL (Recommended for larger deployments):**
```bash
DATABASE_URL=postgresql://username:password@localhost/kef_dashboard
```

## Security Considerations

1. **Change the SECRET_KEY** - Generate a secure random key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use HTTPS** - Configure SSL certificate with your web server

3. **Firewall** - Only expose necessary ports (80, 443)

4. **Regular Updates** - Keep dependencies updated:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

5. **Backup Database** - Regular backups of `data.db` file

## Monitoring and Maintenance

### Log Files
- Application logs: `logs/kef_app.log`
- Access logs: Configure in your web server

### Health Check
- Endpoint: `http://your-domain.com/health`
- Returns JSON with status and database connectivity

### Database Maintenance
- Access maintenance interface: `http://your-domain.com/maintenance`
- Monitor student counts, delete old responses

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   chmod +x setup.sh
   chown -R www-data:www-data /path/to/app
   ```

2. **Database Lock Errors**
   - Ensure only one application instance accesses SQLite
   - Consider PostgreSQL for multiple workers

3. **Static Files Not Loading**
   - Configure web server to serve `/static` directory
   - Check file permissions

4. **Application Won't Start**
   - Check logs: `tail -f logs/kef_app.log`
   - Verify environment variables
   - Test database connectivity

### Getting Help

1. Check application logs
2. Verify configuration
3. Test database connection
4. Ensure all dependencies are installed

## Performance Optimization

### For Higher Traffic

1. **Use PostgreSQL** instead of SQLite
2. **Add Redis** for session storage and caching
3. **Use multiple workers** with Gunicorn
4. **Configure CDN** for static files
5. **Enable gzip compression** in web server
6. **Monitor** with tools like New Relic or DataDog

### Resource Requirements

- **Minimum:** 1 CPU, 512MB RAM, 1GB storage
- **Recommended:** 2 CPU, 2GB RAM, 10GB storage
- **High Traffic:** 4+ CPU, 4GB+ RAM, SSD storage

## File Structure

```
kef-teacher-dashboard/
├── app/                    # Main application code
├── config/                 # Configuration files
├── logs/                   # Application logs
├── static/                 # CSS, JS, images
├── templates/              # HTML templates
├── data.db                 # SQLite database
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── .env                    # Environment configuration
├── setup.sh/.bat           # Setup scripts
└── DEPLOYMENT.md           # This file
```

---

**Note:** This application is production-ready with proper error handling, logging, and security configurations. Follow this guide for a successful deployment.