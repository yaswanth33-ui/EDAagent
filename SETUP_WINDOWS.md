# Quick Setup Guide for Windows (No Docker Required)

## Prerequisites

- Python 3.11+ installed
- Git installed (optional, for cloning)

## Step-by-Step Setup

### 1. Download/Clone the Project

```cmd
git clone https://github.com/yaswanth33-ui/EDAagent.git
cd EDAagent
```

Or download and extract the ZIP file.

### 2. Set Up Environment Variables

1. Navigate to the `server` folder
2. Copy the `.env` file and update it with your API keys:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   SECRET_KEY=your_secret_key_here
   FLASK_ENV=production
   ```

### 3. Install Dependencies

Open Command Prompt or PowerShell in the project directory:

```cmd
pip install -r requirements.txt
```

### 4. Run the Application

#### Option A: Using the Deploy Script (Recommended)

Double-click `deploy.bat` or run:

```cmd
deploy.bat
```

#### Option B: Manual Start with Gunicorn (Production)

```cmd
cd server
gunicorn --config ../gunicorn.conf.py app:app
```

Access at: http://localhost:8000

#### Option C: Development Server (Quick Testing)

```cmd
cd server
python app.py
```

Access at: http://localhost:5000

## Troubleshooting

### Common Issues:

1. **"pip is not recognized"**: Install Python with "Add to PATH" option
2. **Permission errors**: Run Command Prompt as Administrator
3. **Port already in use**: Kill the process or change PORT in .env file
4. **Module not found**: Ensure you're in the correct directory and dependencies are installed

### Getting API Keys:

1. **OpenRouter API Key**: Visit https://openrouter.ai/ and create an account
2. **Secret Key**: Generate a random string for Flask sessions

## Production Notes:

- Use Option A or B for production deployment
- Option C is only for development/testing
- Ensure your firewall allows the application port
- Consider using a reverse proxy (nginx) for production
