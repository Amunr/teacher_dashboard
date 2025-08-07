# KEF - Student Assessment Dashboard

A comprehensive Flask web application for managing student assessments and educational layouts.

## 🏗️ Project Structure

```
KEF/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── models/            # Database models and data access
│   │   ├── __init__.py
│   │   └── database.py    # Database models and operations
│   ├── routes/            # Route blueprints
│   │   ├── __init__.py
│   │   ├── dashboard.py   # Dashboard routes
│   │   └── layout.py      # Layout management routes
│   ├── services/          # Business logic layer
│   │   ├── __init__.py
│   │   └── layout_service.py
│   └── utils/             # Utility functions and helpers
│       ├── __init__.py
│       ├── exceptions.py  # Custom exceptions
│       ├── validators.py  # Data validation
│       └── helpers.py     # Helper functions
├── config/                # Configuration management
│   ├── __init__.py
│   └── config.py         # Environment configurations
├── templates/             # Jinja2 templates
│   ├── layout.html       # Base template
│   ├── homepage.html     # Dashboard homepage
│   ├── layout_view.html  # Layout list view
│   ├── layout_viewer.html # Layout detail view
│   ├── layout_builder.html # Layout creation/editing
│   ├── layout_updater.html # Layout in-place editing
│   └── error.html        # Error page template
├── static/               # Static assets
│   └── js/
│       └── chart.js
├── logs/                 # Application logs (created automatically)
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
├── .env.example        # Environment configuration template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🚀 Features

### Core Functionality
- **Layout Management**: Create, edit, update, and delete assessment layouts
- **Dashboard**: Student assessment overview and metrics
- **Data Validation**: Comprehensive input validation and sanitization
- **Error Handling**: Robust error handling with user-friendly messages
- **Logging**: Comprehensive application logging for monitoring and debugging

### Technical Features
- **MVC Architecture**: Clean separation of concerns with models, views, and controllers
- **Blueprint Organization**: Modular route organization using Flask blueprints
- **Service Layer**: Business logic separated from route handlers
- **Database Abstraction**: Clean database operations with connection pooling
- **Configuration Management**: Environment-based configuration system
- **Security**: Input sanitization, CSRF protection ready, security headers
- **Type Hints**: Full type annotation for better code maintainability

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KEF
   ```

2. **Create virtual environment**
   ```bash
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
CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Write meaningful commit messages

## 📈 Performance Optimization

- Database connection pooling enabled
- Efficient query patterns
- Minimal template rendering overhead
- Static file caching headers

## 🐛 Troubleshooting

### Common Issues
1. **Database locked**: Ensure no other processes are using the database
2. **Port already in use**: Change the port in configuration
3. **Template not found**: Check template paths in blueprint registration
4. **Import errors**: Verify Python path and virtual environment activation

### Debug Mode
Enable debug mode for detailed error information:
```bash
set FLASK_DEBUG=True  # Windows
export FLASK_DEBUG=True  # macOS/Linux
```

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the logs for error details
- Review the configuration settings

## 📄 License

[Add your license information here]

## 🔄 Version History

- **v2.0.0**: Complete restructure with MVC architecture, blueprints, and enhanced security
- **v1.0.0**: Initial Flask application with basic layout management 