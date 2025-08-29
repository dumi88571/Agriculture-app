# AI Agriculture Application

An intelligent farming solution that leverages data science and machine learning to help farmers increase productivity while preserving the environment. This application is built with Flask in a single Python file for simplicity and ease of deployment.

## Features

1. **Crop Yield Prediction** - Predict expected yield based on historical data, weather patterns, soil conditions, and farming practices
2. **Pest and Disease Detection** - Early identification of crop pests and diseases using image recognition
3. **Irrigation Optimization** - Smart water usage recommendations to conserve water while maximizing crop health
4. **Soil Health Monitoring** - Analysis of soil composition and nutrient levels with improvement recommendations
5. **Weather Pattern Analysis** - Hyperlocal weather forecasting for optimal farming decisions
6. **Market Price Prediction** - Predictive analytics for crop market prices to optimize selling times
7. **Sustainability Tracking** - Carbon footprint monitoring and environmental impact assessment

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite (for simplicity in single-file deployment)
- **Machine Learning**: scikit-learn for traditional ML algorithms
- **Frontend**: HTML/CSS/JavaScript with Bootstrap


## Application Structure

The entire application is contained in a single file (`app.py`) which includes:
- Flask web server
- Database models using SQLite
- Machine learning models for agricultural predictions
- Web interface for farmer interaction
- Data visualization components

## Machine Learning Models

- Crop yield prediction using Random Forest Regression
- Pest and disease detection using simple classification algorithms
- Irrigation optimization using rule-based systems with ML enhancements
- Soil health analysis using clustering algorithms
- Market price prediction using time series forecasting

## Database Schema

The application uses SQLite with the following tables:
- Farmers: Farmer information
- Farms: Farm details and location
- SoilData: Soil composition and nutrient levels
- WeatherData: Weather conditions and forecasts
- CropData: Crop planting, growth, and yield data
- PestDiseaseData: Records of pest and disease occurrences
- IrrigationData: Water usage and irrigation scheduling
- MarketData: Historical crop prices
- SustainabilityData: Environmental impact metrics

