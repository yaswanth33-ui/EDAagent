# EDA Agent - Intelligent Data Analysis Assistant

EDA Agent is an intelligent data analysis tool that combines the power of AI with automated exploratory data analysis capabilities. It provides a user-friendly interface for analyzing datasets, generating insights, and visualizing data patterns.

## Features

### Intelligent Data Analysis

- Automated analysis of CSV and Excel files
- AI-powered insights and recommendations
- Natural language interface for data exploration
- Contextual understanding of data patterns

### Advanced Visualization

- Automatic generation of relevant visualizations
- Multiple chart types:
  - Distribution plots
  - Box plots
  - Correlation heatmaps
  - Bar plots
  - Scatter plots
- Smart visualization selection based on data characteristics

### Statistical Analysis

- Comprehensive statistical summaries
- Anomaly detection using IQR method
- Data quality assessment
- Automated cleaning suggestions

### Interactive Chat Interface

- Session-based chat history
- Real-time interaction
- Markdown support
- Responsive design

### Data Management

- Support for CSV and Excel files
- Automatic data cleanup
- Secure storage
- Database integration

## Installation

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/yaswanth33-ui/EDAagent.git
cd EDAagent
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the `server/` directory with:

```
OPENROUTER_API_KEY=your_api_key_here
AIML_API_KEY=your_aiml_key_here
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

5. Start the development server:

```bash
cd server
python app.py
```

### Quick Windows Setup

For Windows users who want to get started quickly without Docker, see the detailed guide: [SETUP_WINDOWS.md](SETUP_WINDOWS.md)

**TL;DR for Windows:**

1. Download/clone the project
2. Create `.env` file in `server/` folder with your API keys
3. Double-click `deploy.bat`
4. Access at `http://localhost:8000`

### Production Deployment

#### Option 1: Direct Deployment (Recommended)

1. Use the deployment scripts:

   - **Windows**: Double-click `deploy.bat` or run:
     ```cmd
     deploy.bat
     ```
   - **Linux/Mac**:
     ```bash
     chmod +x deploy.sh
     ./deploy.sh
     ```

2. Or manually with Gunicorn:

   ```bash
   pip install -r requirements.txt
   cd server
   gunicorn --config ../gunicorn.conf.py app:app
   ```

3. Access the application at `http://localhost:8000`

#### Option 2: Simple Flask Development Server

For quick testing (not recommended for production):

```bash
pip install -r requirements.txt
cd server
python app.py
```

Access at `http://localhost:5000`

#### Option 3: Heroku Deployment

1. Install Heroku CLI and login:

```bash
heroku login
```

2. Create a new Heroku app:

```bash
heroku create your-app-name
```

3. Set environment variables:

```bash
heroku config:set OPENROUTER_API_KEY=your_api_key_here
heroku config:set SECRET_KEY=your_secret_key_here
heroku config:set FLASK_ENV=production
```

4. Deploy:

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### Option 4: Docker Deployment (Optional)

If Docker is available, the application can be containerized:

```bash
docker-compose up --build
```

#### Option 5: Cloud Platforms (AWS, GCP, Azure)

The application is containerized and can be deployed on any cloud platform that supports Docker containers. Use the provided Dockerfile and configure environment variables accordingly.

## Environment Variables

| Variable             | Description                          | Required           |
| -------------------- | ------------------------------------ | ------------------ |
| `OPENROUTER_API_KEY` | API key for OpenRouter service       | Yes                |
| `AIML_API_KEY`       | API key for AIML service             | No                 |
| `SECRET_KEY`         | Flask secret key for sessions        | Yes                |
| `FLASK_ENV`          | Environment (development/production) | No                 |
| `PORT`               | Port to run the application          | No (default: 5000) |
| `GUNICORN_WORKERS`   | Number of Gunicorn workers           | No (default: 2)    |

## Usage

1. Access the web application in your browser
2. Upload your dataset (CSV or Excel file)
3. Interact with the chat interface to:
   - Ask questions about your data
   - Request statistical analysis
   - Get insights and recommendations
   - Generate visualizations

## API Endpoints

- `GET /` - Home page
- `POST /upload` - Upload dataset
- `POST /chat` - Chat interface
- `GET /history` - Analysis history
- `GET /analysis/<id>` - View specific analysis
- `DELETE /analysis/<id>` - Delete analysis

## Project Structure

```
EDAagent/
├── data/                   # Database storage
├── frontend/
│   ├── static/             # Static assets
│   │   └── plots/          # Generated visualizations
│   └── templates/          # HTML templates
├── server/
│   ├── uploads/            # Uploaded files
│   ├── app.py              # Main Flask application
│   ├── database.py         # Database operations
│   ├── utils.py            # Utility functions
│   └── .env                # Environment variables
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── gunicorn.conf.py        # Gunicorn configuration
└── README.md               # This file
```

## Configuration

### Production Settings

- Debug mode is automatically disabled in production
- File upload size limited to 16MB
- Logging configured with rotation
- Database connections properly managed
- Security headers implemented

### Performance Tuning

- Gunicorn with multiple workers
- Static file serving optimized
- Database query optimization
- Memory usage monitoring

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your OpenRouter API key is set correctly in the `.env` file
2. **File Upload Errors**: Check file size (max 16MB) and format (CSV/Excel only)
3. **Port Conflicts**: Change the PORT environment variable if default port is occupied
4. **Database Issues**: Delete `eda_agent.db` to reset the database

### Logs

Check application logs:

- Development: Console output
- Production: `server.log` file
- Docker: `docker-compose logs eda-agent`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For support, email yaswanthreddypanem@gmail.com or create an issue on GitHub.
