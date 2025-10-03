# KEF Teacher Dashboard

A comprehensive Flask web application for managing student assessments with Google Sheets integration and automated background polling.

## 🏗️ Project Structure

```
KEF/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory and initialization
│   ├── models/                  # Database models and data access
│   │   ├── __init__.py
│   │   └── database.py          # Database models and operations
│   ├── routes/                  # Route blueprints
│   │   ├── __init__.py
│   │   ├── dashboard.py         # Dashboard and API routes
│   │   └── layout.py            # Layout management routes
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── background_poller.py # Background Google Sheets polling
│   │   ├── dashboard_service.py # Dashboard data processing
│   │   ├── layout_service.py    # Layout management logic
│   │   └── sheets_service.py    # Google Sheets integration
│   └── utils/                   # Utility functions and helpers
│       ├── __init__.py
│       ├── exceptions.py        # Custom exceptions
│       ├── helpers.py           # Helper functions
│       └── validators.py        # Data validation
├── config/                      # Configuration management
│   ├── __init__.py
│   └── config.py               # Environment configurations
├── static/                     # Static assets
│   └── js/
│       └── chart.js           # Dashboard charting
├── templates/                  # Jinja2 templates
│   ├── layout.html            # Base template
│   ├── homepage.html          # Dashboard homepage
│   ├── layout_*.html          # Layout management pages
│   └── error.html             # Error page template
├── tests.py                   # Comprehensive test suite
├── clear_responses.py         # Database maintenance utility
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
├── data.db                    # SQLite database
├── .env.example              # Environment configuration template
└── .gitignore                # Git ignore rules
```

## 🚀 Features

### Core Functionality
- **Student Assessment Dashboard**: Real-time metrics and analytics
- **Google Sheets Integration**: Automatic data import with background polling
- **Layout Management**: Create and manage assessment layouts
- **Maintenance Interface**: Service management and data monitoring
- **Background Processing**: Automated polling with configurable intervals

### Technical Features
- **Flask-based Architecture**: Clean MVC pattern with blueprints
- **Background Threading**: In-app polling system (no external processes)
- **Real-time Status Updates**: Service monitoring with countdown timers
- **Database Management**: SQLite with migration support
- **Configuration-driven**: Environment-based settings
- **Security**: Input sanitization and security headers
- **Comprehensive Logging**: Application monitoring and debugging

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd KEF
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or: source venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   copy .env.example .env  # Windows
   # or: cp .env.example .env  # macOS/Linux
   # Edit .env with your settings
   ```

4. **Initialize database**
   ```bash
   python run.py  # This will create and initialize the database
   ```

5. **Access the application**
   - Open browser to `http://localhost:5000`
   - Access maintenance interface at `http://localhost:5000/maintenance`

## 🔧 Configuration

### Environment Variables (.env)
```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///data.db
SECRET_KEY=your-secret-key-here
GOOGLE_SHEETS_URL=your-google-sheets-csv-url
```

### Google Sheets Setup
1. Make your Google Sheet public for CSV export
2. Get the CSV export URL
3. Configure it in the maintenance interface or .env file

## 🎯 Usage

### Running the Application
```bash
python run.py
```

### Background Polling Service
The application includes an integrated background polling service:

1. **Start Service**: Use the maintenance interface to start automatic polling
2. **Configure Interval**: Set polling frequency (default: 5 minutes)
3. **Monitor Status**: View real-time status and next poll countdown
4. **Manual Import**: Force immediate data import from Google Sheets

### Maintenance Operations
Access `/maintenance` for:
- Service start/stop controls
- Data import statistics
- Failed import monitoring
- Database cleanup utilities
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Environment configuration**
   ```bash
   # Copy example environment file
   copy .env.example .env  # Windows
   cp .env.example .env    # macOS/Linux
   
   # Edit .env file with your configuration
   ```

6. **Initialize database**
   ```bash
   python -c "from app import create_app; app = create_app(); print('Database initialized')"
   ```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
python run.py
```

### Production Mode
```bash
# Set environment variables
set FLASK_ENV=production  # Windows
export FLASK_ENV=production  # macOS/Linux

python run.py
```

### Using Flask CLI
```bash
# Set Flask app
set FLASK_APP=run.py  # Windows
export FLASK_APP=run.py  # macOS/Linux

# Run development server
flask run --host=0.0.0.0 --port=5000
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Application environment (development/production/testing) |
| `FLASK_DEBUG` | `True` | Enable debug mode |
| `FLASK_HOST` | `0.0.0.0` | Server host |
| `FLASK_PORT` | `5000` | Server port |
| `SECRET_KEY` | `dev-key-change-in-production` | Flask secret key |
| `DATABASE_URL` | `sqlite:///data.db` | Database connection URL |
| `LOG_LEVEL` | `INFO` | Logging level |

### Configuration Environments

- **Development**: Debug enabled, verbose logging, relaxed security
- **Production**: Debug disabled, file logging, strict security
- **Testing**: In-memory database, minimal logging

## 📊 Database Schema

### Tables

1. **questions**: Layout questions and metadata
   - `id`: Primary key
   - `layout_id`: Layout identifier
   - `layout_name`: Layout name
   - `Domain`: Question domain
   - `SubDomain`: Question subdomain
   - `Index_ID`: Question index
   - `Name`: Question name
   - `year_start`, `year_end`: Validity period
   - `Date edited`: Last modification date

2. **responses**: Student assessment responses
   - `id`: Primary key
   - `res-id`: Response batch ID
   - Student metadata (School, Grade, Teacher, Assessment, Name, Date)
   - `Index_ID`: Question reference
   - `Response`: Response value

3. **subDomains**: Domain organization (legacy)
   - Domain and subdomain structure

## 🔗 API Endpoints

### Dashboard Routes
- `GET /` - Main dashboard
- `GET /health` - Health check endpoint

### Layout Management Routes
- `GET /layout/` - List all layouts
- `GET /layout/view/<id>` - View specific layout
- `GET /layout/edit/new` - Create new layout form
- `GET /layout/edit/<id>` - Edit layout (clone mode)
- `GET /layout/update/<id>` - Update layout (in-place mode)
- `POST /layout/delete/<id>` - Delete layout
- `POST /layout/submit` - Save new layout
- `POST /layout/update/<id>/submit` - Save layout updates

### CRUD Operations
- `POST /layout/add_domain` - Add domain
- `POST /layout/delete_domain/<id>` - Delete domain
- `POST /layout/add_subdomain/<domain_id>` - Add subdomain
- `POST /layout/delete_subdomain/<domain_id>/<subdomain_id>` - Delete subdomain
- `POST /layout/add_question/<domain_id>/<subdomain_id>` - Add question
- `POST /layout/delete_question/<domain_id>/<subdomain_id>/<question_id>` - Delete question

## 🧪 Testing

### Manual Testing
1. Start the application
2. Navigate to `http://localhost:5000`
3. Test layout creation, editing, and deletion
4. Verify data persistence across sessions

### Automated Testing
```bash
# Set testing environment
set FLASK_ENV=testing  # Windows
export FLASK_ENV=testing  # macOS/Linux

# Run tests (when test suite is implemented)
python -m pytest tests/
```

## 🔒 Security Features

- **Input Sanitization**: All user inputs are sanitized
- **CSRF Protection**: Ready for CSRF token implementation
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **Session Security**: Secure session configuration
- **SQL Injection Prevention**: Parameterized queries only

## 📝 Logging

Logs are written to:
- **Development**: Console output
- **Production**: `logs/kef_app.log` with rotation

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🔄 Database Migrations

Currently using SQLAlchemy table definitions. For production deployments:
1. Backup existing database
2. Update table definitions in `app/models/database.py`
3. Deploy new code
4. Verify data integrity

## 🚀 Deployment

### Production Deployment Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up production database
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Set up SSL/TLS certificates
- [ ] Configure logging and monitoring
- [ ] Set up backup procedures

### Docker Deployment (Future Enhancement)
```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
## 🧪 Testing

### Run All Tests
```bash
python tests.py
```

### Run Specific Tests
```bash
python tests.py database_connection
python tests.py sheets_integration
python tests.py grade_assessment_fix
python tests.py all
```

### Available Tests
- `database_connection` - Database connectivity and tables
- `date_logic` - Date handling and validation
- `response_data_integrity` - Data validation and integrity
- `layout_functionality` - Layout management features
- `sheets_integration` - Google Sheets import/export
- `dashboard_service` - Dashboard data processing
- `grade_assessment_fix` - Grade assessment calculations
- `polling_service_status` - Background polling service
- `sheets_configuration` - Google Sheets configuration
- `metadata_mapping` - Data mapping validation

## 🔒 Security Features

- **Input Sanitization**: All user inputs validated and sanitized
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **Session Security**: Secure session configuration
- **SQL Injection Prevention**: Parameterized queries only
- **CSRF Protection**: Ready for CSRF token implementation

## 📊 Database Management

### Clear Response Data
```bash
python clear_responses.py
```

### Database Structure
- **layouts**: Assessment layout definitions
- **questions**: Question metadata and mappings
- **responses**: Student response data
- **student_counts**: Enrollment statistics
- **sheets_config**: Google Sheets configuration
- **failed_imports**: Import error tracking

## � Deployment

### Production Setup
1. **Set production environment**
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

3. **Configure reverse proxy** (nginx example)
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:5000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

## 📝 API Documentation

### Key Endpoints
- `GET /` - Dashboard homepage
- `GET /maintenance` - Maintenance interface
- `POST /api/sheets/service/start` - Start polling service
- `POST /api/sheets/service/stop` - Stop polling service
- `GET /api/sheets/service/status` - Get service status
- `POST /api/sheets/import` - Manual data import
- `GET /api/sheets/stats` - Dashboard statistics

## 🔍 Monitoring & Logging

### Application Logs
- **Development**: Console output
- **Production**: File-based logging with rotation

### Service Monitoring
- Real-time service status in maintenance interface
- Background polling health checks
- Import success/failure tracking
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests.py`
5. Submit a pull request

## 📄 License

[Specify your license here]

## 🆘 Support

For issues and support:
1. Check the maintenance interface for service status
2. Run `python tests.py` to verify system health
3. Check application logs for detailed error information
4. Review the Google Sheets URL configuration

---

**Ready for Production**: This application is deployment-ready with integrated background services, comprehensive testing, and production configurations.

- **v2.0.0**: Complete restructure with MVC architecture, blueprints, and enhanced security
- **v1.0.0**: Initial Flask application with basic layout management 