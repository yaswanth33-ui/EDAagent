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

1. Clone the repository:
```bash
git clone https://github.com/yaswanth33-ui/EDAagent.git
cd server
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
Create a `.env` file in the root directory with:
```
OPENROUTER_API_KEY=your_api_key_here
```


## Usage

1. Start the server:
```bash
python server/app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload your dataset (CSV or Excel file)

4. Interact with the chat interface to:
   - Ask questions about your data
   - Request information about data
   - General chat
   - Get insights and recommendations

## Project Structure

```
EDAagent/
├── server/
│   ├── static/
│   │   └── plots/
│   ├── templates/
│   ├── uploads/
│   ├── app.py
│   ├── database.py
│   └── utils.py
├── requirements.txt
├── .env
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask for the web framework
- Pandas for data manipulation
- Matplotlib/Seaborn for visualizations
- OpenRouter API for AI model integration 

Contact For any inquiries or support, please reach out at yaswanthreddypanem@gmail.com .