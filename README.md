# AirQualityDataVisualization
🌍 Air Quality Dashboard - India (2015-2024)
# Air Quality Dashboard - India (2015-2024)

Interactive dashboard analyzing air quality data across major Indian cities.

## Features
- PM2.5 and PM10 trend analysis
- Seasonal patterns and hourly variations
- City-wise pollutant comparison
- AQI category distribution
- Correlation analysis

## Requirements
- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python dashboard_generator.py
```

Open `dashboard.html` in your browser to view the dashboard.

## Data Source
Air Quality Data from Indian cities (2015-2024)
```

### **Create requirements.txt:**
```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
```

### **Create .gitignore:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Data files (if they're too large)
# *.csv

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
