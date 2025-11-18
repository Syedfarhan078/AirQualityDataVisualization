# ------------------------------------------------------------
# Enhanced Air Quality Data Visualization Dashboard
# Major Indian Cities (2015–2024)
# ------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os, io, base64
from datetime import datetime

sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 100

# ------------------------------------------------------------
# Function to load CSV safely
# ------------------------------------------------------------
def safe_read(file):
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        print(f"⚠️ File not found: {file}")
        return pd.DataFrame()

# ------------------------------------------------------------
# 1️⃣ Load datasets
# ------------------------------------------------------------
city_day = safe_read("city_day.csv")
city_hour = safe_read("city_hour.csv")
station_day = safe_read("station_day.csv")

# ------------------------------------------------------------
# 2️⃣ Enhanced Preprocessing
# ------------------------------------------------------------
for df in [city_day, city_hour, station_day]:
    if not df.empty and 'City' in df.columns:
        df['City'] = df['City'].astype(str).str.strip().str.title()

city_day['Datetime'] = pd.to_datetime(city_day.get('Datetime'), errors='coerce')
city_day.dropna(subset=['Datetime'], inplace=True)
city_day['Year'] = city_day['Datetime'].dt.year
city_day['Month'] = city_day['Datetime'].dt.month
city_day['Season'] = city_day['Month'].apply(
    lambda x: 'Winter' if x in [12, 1, 2] else 
              'Summer' if x in [3, 4, 5] else 
              'Monsoon' if x in [6, 7, 8, 9] else 'Autumn'
)

city_hour['Datetime'] = pd.to_datetime(city_hour.get('Datetime'), errors='coerce')
city_hour['Hour'] = city_hour['Datetime'].dt.hour

pollutants = ['PM2.5','PM10','NO2','NH3','SO2','CO','O3','Benzene','Toluene','Xylene']
city_day[pollutants] = city_day[pollutants].fillna(city_day[pollutants].mean())

for col in pollutants:
    if col in city_day.columns:
        city_day = city_day[city_day[col] < city_day[col].quantile(0.99)]

# AQI Category function
def get_aqi_category(pm25):
    if pm25 <= 30: return 'Good'
    elif pm25 <= 60: return 'Satisfactory'
    elif pm25 <= 90: return 'Moderate'
    elif pm25 <= 120: return 'Poor'
    elif pm25 <= 250: return 'Very Poor'
    else: return 'Severe'

city_day['AQI_Category'] = city_day['PM2.5'].apply(get_aqi_category)

# Utility: convert figure to base64 string
def fig_to_base64():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    img = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close()
    return img

images = {}
stats = {}

# Calculate key statistics
stats['avg_pm25'] = city_day['PM2.5'].mean()
stats['max_pm25'] = city_day['PM2.5'].max()
stats['total_cities'] = city_day['City'].nunique()
stats['date_range'] = f"{city_day['Datetime'].min().strftime('%Y')} - {city_day['Datetime'].max().strftime('%Y')}"

# ------------------------------------------------------------
# 3️⃣ Visualization 1: Enhanced Yearly PM2.5 Trends
# ------------------------------------------------------------
plt.figure(figsize=(14, 7))
yearly_avg = city_day.groupby(['City', 'Year'])['PM2.5'].mean().reset_index()
top_cities = city_day.groupby('City')['PM2.5'].mean().nlargest(8).index
yearly_filtered = yearly_avg[yearly_avg['City'].isin(top_cities)]

for city in top_cities:
    city_data = yearly_filtered[yearly_filtered['City'] == city]
    plt.plot(city_data['Year'], city_data['PM2.5'], marker='o', linewidth=2.5, label=city)

plt.title('PM2.5 Trends in Top 8 Polluted Cities (2015–2024)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Year', fontsize=12, fontweight='bold')
plt.ylabel('Average PM2.5 (µg/m³)', fontsize=12, fontweight='bold')
plt.legend(loc='best', frameon=True, shadow=True)
plt.grid(True, alpha=0.3)
plt.tight_layout()
images['trend'] = fig_to_base64()

# ------------------------------------------------------------
# 4️⃣ Visualization 2: AQI Category Distribution
# ------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

aqi_counts = city_day['AQI_Category'].value_counts()
colors = ['#00E400', '#FFFF00', '#FF7E00', '#FF0000', '#8F3F97', '#7E0023']
category_order = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']
aqi_counts = aqi_counts.reindex(category_order, fill_value=0)

ax1.pie(aqi_counts, labels=aqi_counts.index, autopct='%1.1f%%',
        startangle=90, colors=colors[:len(aqi_counts)], textprops={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title('Air Quality Distribution (2015–2024)', fontsize=14, fontweight='bold', pad=20)

avg_pollutants = city_day[pollutants].mean().sort_values(ascending=False)
ax2.pie(avg_pollutants, labels=avg_pollutants.index, autopct='%1.1f%%',
        startangle=90, colors=sns.color_palette("viridis", len(avg_pollutants)),
        textprops={'fontsize': 10})
ax2.set_title('Pollutant Composition Breakdown', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
images['pie'] = fig_to_base64()

# ------------------------------------------------------------
# 5️⃣ Visualization 3: Seasonal Analysis
# ------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

seasonal_avg = city_day.groupby('Season')['PM2.5'].mean().sort_values(ascending=False)
season_colors = {'Winter': '#3498db', 'Summer': '#f39c12', 'Monsoon': '#2ecc71', 'Autumn': '#e74c3c'}
colors_sorted = [season_colors[s] for s in seasonal_avg.index]

ax1.bar(seasonal_avg.index, seasonal_avg.values, color=colors_sorted, edgecolor='black', linewidth=1.5)
ax1.set_title('Average PM2.5 by Season', fontsize=14, fontweight='bold', pad=20)
ax1.set_ylabel('PM2.5 (µg/m³)', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

delhi_hour = city_hour[city_hour['City'] == 'Delhi']
hourly_avg = delhi_hour.groupby('Hour')['PM2.5'].mean()

ax2.plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2.5, color='#e74c3c', markersize=8)
ax2.fill_between(hourly_avg.index, hourly_avg.values, alpha=0.3, color='#e74c3c')
ax2.set_title('24-Hour PM2.5 Pattern in Delhi', fontsize=14, fontweight='bold', pad=20)
ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
ax2.set_ylabel('PM2.5 (µg/m³)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xticks(range(0, 24, 2))

plt.tight_layout()
images['seasonal'] = fig_to_base64()

# ------------------------------------------------------------
# 6️⃣ Visualization 4: City Comparison
# ------------------------------------------------------------
plt.figure(figsize=(14, 8))
city_avg = city_day.groupby('City')[['PM2.5', 'PM10', 'NO2']].mean().nlargest(12, 'PM2.5')

x = np.arange(len(city_avg))
width = 0.25

plt.bar(x - width, city_avg['PM2.5'], width, label='PM2.5', color='#e74c3c', edgecolor='black')
plt.bar(x, city_avg['PM10'], width, label='PM10', color='#3498db', edgecolor='black')
plt.bar(x + width, city_avg['NO2'], width, label='NO2', color='#2ecc71', edgecolor='black')

plt.xlabel('Cities', fontsize=12, fontweight='bold')
plt.ylabel('Concentration (µg/m³)', fontsize=12, fontweight='bold')
plt.title('Top 12 Cities - Major Pollutant Comparison', fontsize=16, fontweight='bold', pad=20)
plt.xticks(x, city_avg.index, rotation=45, ha='right')
plt.legend(frameon=True, shadow=True)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
images['comparison'] = fig_to_base64()

# ------------------------------------------------------------
# 7️⃣ Visualization 5: Delhi Station Analysis
# ------------------------------------------------------------
if not station_day.empty:
    delhi_stations = station_day[station_day['City'] == 'Delhi']
    station_avg = delhi_stations.groupby('Station')['PM2.5'].mean().sort_values(ascending=False).head(12)

    plt.figure(figsize=(14, 8))
    colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(station_avg)))
    bars = plt.barh(station_avg.index, station_avg.values, color=colors, edgecolor='black', linewidth=1.2)
    
    for i, (bar, val) in enumerate(zip(bars, station_avg.values)):
        plt.text(val + 2, i, f'{val:.1f}', va='center', fontweight='bold', fontsize=10)
    
    plt.xlabel('Average PM2.5 (µg/m³)', fontsize=12, fontweight='bold')
    plt.title('Top 12 Most Polluted Monitoring Stations in Delhi', fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    images['stations'] = fig_to_base64()

# ------------------------------------------------------------
# 8️⃣ Visualization 6: Enhanced Correlation Heatmap
# ------------------------------------------------------------
plt.figure(figsize=(12, 10))
corr = city_day[pollutants].corr()

mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm', fmt='.2f', 
            linewidths=2, cbar_kws={"shrink": 0.8}, vmin=-1, vmax=1,
            square=True, linecolor='white')
plt.title('Pollutant Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
images['heatmap'] = fig_to_base64()

# ------------------------------------------------------------
# 9️⃣ Create Enhanced HTML Dashboard
# ------------------------------------------------------------
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Air Quality Dashboard India</title>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    min-height: 100vh;
}}

.container {{
    max-width: 1400px;
    margin: 0 auto;
}}

header {{
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    margin-bottom: 30px;
    text-align: center;
}}

h1 {{
    color: #2c3e50;
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}}

.subtitle {{
    color: #7f8c8d;
    font-size: 1.2em;
    margin-bottom: 20px;
}}

.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}}

.stat-card {{
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.stat-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}}

.stat-value {{
    font-size: 2.5em;
    font-weight: bold;
    color: #3498db;
    margin: 10px 0;
}}

.stat-label {{
    color: #7f8c8d;
    font-size: 1em;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.card {{
    background: white;
    padding: 30px;
    margin: 20px 0;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    transition: transform 0.3s ease;
}}

.card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.2);
}}

.card h2 {{
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.8em;
    border-left: 5px solid #3498db;
    padding-left: 15px;
}}

img {{
    width: 100%;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}}

footer {{
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-top: 30px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    color: #7f8c8d;
}}

.timestamp {{
    font-size: 0.9em;
    color: #95a5a6;
    margin-top: 10px;
}}

.info-section {{
    margin: 30px 0;
}}

.info-card {{
    background: white;
    padding: 30px;
    margin: 20px 0;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}}

.info-card h3 {{
    color: #2c3e50;
    font-size: 1.6em;
    margin-bottom: 15px;
    border-left: 5px solid #e74c3c;
    padding-left: 15px;
}}

.info-card p {{
    color: #34495e;
    line-height: 1.8;
    margin-bottom: 20px;
    font-size: 1.1em;
}}

.info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}}

.info-item {{
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #3498db;
    line-height: 1.7;
    color: #2c3e50;
}}

.info-item strong {{
    color: #e74c3c;
    display: block;
    margin-bottom: 8px;
    font-size: 1.1em;
}}

.aqi-info {{
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}}

.aqi-table {{
    display: grid;
    gap: 12px;
}}

.aqi-row {{
    padding: 15px 20px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
}}

.aqi-row:hover {{
    transform: translateX(5px);
}}

.aqi-category {{
    font-weight: bold;
    font-size: 1.1em;
    min-width: 180px;
}}

.aqi-desc {{
    flex: 1;
    text-align: right;
    font-size: 0.95em;
}}

@media (max-width: 768px) {{
    h1 {{
        font-size: 1.8em;
    }}
    
    .stat-value {{
        font-size: 2em;
    }}
    
    .card {{
        padding: 20px;
    }}
    
    .info-grid {{
        grid-template-columns: 1fr;
    }}
    
    .aqi-row {{
        flex-direction: column;
        text-align: center;
        gap: 10px;
    }}
    
    .aqi-desc {{
        text-align: center;
    }}
}}
</style>
</head>

<body>
<div class="container">
    <header>
        <h1>🌍 Air Quality Analysis Dashboard</h1>
        <div class="subtitle">Indian Cities Environmental Monitoring ({stats['date_range']})</div>
    </header>

    <div class="info-section">
        <div class="info-card">
            <h3>🔬 About PM2.5</h3>
            <p><strong>PM2.5</strong> refers to fine particulate matter with a diameter of 2.5 micrometers or less - about 30 times smaller than a human hair.</p>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Sources:</strong> Vehicle emissions, industrial processes, construction activities, biomass burning, and natural sources like dust storms
                </div>
                <div class="info-item">
                    <strong>Health Impact:</strong> Can penetrate deep into lungs and bloodstream, causing respiratory diseases, cardiovascular problems, and premature death
                </div>
                <div class="info-item">
                    <strong>Safe Limit:</strong> WHO guideline: 15 µg/m³ (annual average) | Indian Standard: 40 µg/m³ (annual average)
                </div>
            </div>
        </div>

        <div class="info-card">
            <h3>🔬 About PM10</h3>
            <p><strong>PM10</strong> refers to coarse particulate matter with a diameter of 10 micrometers or less - about the width of a single human hair.</p>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Sources:</strong> Road dust, construction sites, agricultural activities, pollen, mold spores, and industrial emissions
                </div>
                <div class="info-item">
                    <strong>Health Impact:</strong> Affects upper respiratory tract, causes asthma, bronchitis, and aggravates existing lung conditions
                </div>
                <div class="info-item">
                    <strong>Safe Limit:</strong> WHO guideline: 45 µg/m³ (annual average) | Indian Standard: 60 µg/m³ (annual average)
                </div>
            </div>
        </div>

        <div class="info-card aqi-info">
            <h3>📊 AQI Categories & Health Implications</h3>
            <div class="aqi-table">
                <div class="aqi-row" style="background: #00E400;">
                    <span class="aqi-category">Good (0-50)</span>
                    <span class="aqi-desc">Air quality is satisfactory, minimal health impact</span>
                </div>
                <div class="aqi-row" style="background: #FFFF00;">
                    <span class="aqi-category">Satisfactory (51-100)</span>
                    <span class="aqi-desc">Acceptable air quality, sensitive people may experience minor issues</span>
                </div>
                <div class="aqi-row" style="background: #FF7E00; color: white;">
                    <span class="aqi-category">Moderate (101-200)</span>
                    <span class="aqi-desc">May cause breathing discomfort to sensitive groups</span>
                </div>
                <div class="aqi-row" style="background: #FF0000; color: white;">
                    <span class="aqi-category">Poor (201-300)</span>
                    <span class="aqi-desc">Breathing discomfort to most people on prolonged exposure</span>
                </div>
                <div class="aqi-row" style="background: #8F3F97; color: white;">
                    <span class="aqi-category">Very Poor (301-400)</span>
                    <span class="aqi-desc">Respiratory illness on prolonged exposure</span>
                </div>
                <div class="aqi-row" style="background: #7E0023; color: white;">
                    <span class="aqi-category">Severe (401+)</span>
                    <span class="aqi-desc">Affects healthy people and seriously impacts those with existing diseases</span>
                </div>
            </div>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Average PM2.5</div>
            <div class="stat-value">{stats['avg_pm25']:.1f}</div>
            <div class="stat-label">µg/m³</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Peak PM2.5</div>
            <div class="stat-value">{stats['max_pm25']:.0f}</div>
            <div class="stat-label">µg/m³</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Cities Monitored</div>
            <div class="stat-value">{stats['total_cities']}</div>
            <div class="stat-label">Locations</div>
        </div>
    </div>

    <div class="card">
        <h2>📈 PM2.5 Trends Across Major Cities</h2>
        <img src="data:image/png;base64,{images['trend']}" alt="PM2.5 Trends">
    </div>

    <div class="card">
        <h2>🎯 Air Quality & Pollutant Distribution</h2>
        <img src="data:image/png;base64,{images['pie']}" alt="Air Quality Distribution">
    </div>

    <div class="card">
        <h2>🌡️ Seasonal & Hourly Analysis</h2>
        <img src="data:image/png;base64,{images['seasonal']}" alt="Seasonal Analysis">
    </div>

    <div class="card">
        <h2>🏙️ City-wise Pollutant Comparison</h2>
        <img src="data:image/png;base64,{images['comparison']}" alt="City Comparison">
    </div>

    {"<div class='card'><h2>📍 Delhi Station-wise Analysis</h2><img src='data:image/png;base64," + images['stations'] + "' alt='Delhi Stations'></div>" if 'stations' in images else ""}

    <div class="card">
        <h2>🔗 Pollutant Correlation Matrix</h2>
        <img src="data:image/png;base64,{images['heatmap']}" alt="Correlation Heatmap">
    </div>

    <footer>
        <strong>Air Quality Dashboard</strong> | Data Analysis & Visualization
        <div class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
    </footer>
</div>
</body>
</html>
"""

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Enhanced dashboard generated: dashboard.html")
print(f"📊 Analyzed {stats['total_cities']} cities from {stats['date_range']}")
print(f"📈 Average PM2.5: {stats['avg_pm25']:.1f} µg/m³")
print(f"🔴 Peak PM2.5: {stats['max_pm25']:.0f} µg/m³")