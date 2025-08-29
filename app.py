import os
import sqlite3
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import json
import datetime

# Initialize Flask app
app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS farmers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT,
                  phone TEXT,
                  location TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS farms
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farmer_id INTEGER,
                  name TEXT NOT NULL,
                  size REAL,
                  location TEXT,
                  FOREIGN KEY (farmer_id) REFERENCES farmers (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS soil_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farm_id INTEGER,
                  date DATE,
                  pH REAL,
                  nitrogen REAL,
                  phosphorus REAL,
                  potassium REAL,
                  organic_matter REAL,
                  FOREIGN KEY (farm_id) REFERENCES farms (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS weather_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farm_id INTEGER,
                  date DATE,
                  temperature REAL,
                  humidity REAL,
                  rainfall REAL,
                  FOREIGN KEY (farm_id) REFERENCES farms (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS crop_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farm_id INTEGER,
                  crop_type TEXT,
                  planting_date DATE,
                  expected_harvest_date DATE,
                  actual_harvest_date DATE,
                  expected_yield REAL,
                  actual_yield REAL,
                  FOREIGN KEY (farm_id) REFERENCES farms (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pest_disease_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farm_id INTEGER,
                  crop_id INTEGER,
                  date DATE,
                  pest_type TEXT,
                  disease_type TEXT,
                  severity TEXT,
                  FOREIGN KEY (farm_id) REFERENCES farms (id),
                  FOREIGN KEY (crop_id) REFERENCES crop_data (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS irrigation_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farm_id INTEGER,
                  date DATE,
                  water_amount REAL,
                  irrigation_method TEXT,
                  FOREIGN KEY (farm_id) REFERENCES farms (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS market_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  crop_type TEXT,
                  date DATE,
                  price REAL,
                  location TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sustainability_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  farm_id INTEGER,
                  date DATE,
                  carbon_footprint REAL,
                  water_usage REAL,
                  energy_usage REAL,
                  FOREIGN KEY (farm_id) REFERENCES farms (id))''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Machine Learning Models
class CropYieldPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def train(self, data):
        # In a real application, this would use actual historical data
        # For this example, we'll generate synthetic training data
        np.random.seed(42)
        X = np.random.rand(1000, 5) * [100, 14, 50, 50, 50]  # [soil_quality, temperature, rainfall, nitrogen, phosphorus]
        y = X[:, 0] * 0.5 + X[:, 1] * 2 + X[:, 2] * 0.8 + X[:, 3] * 0.3 + X[:, 4] * 0.2 + np.random.normal(0, 5, 1000)
        
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, soil_quality, temperature, rainfall, nitrogen, phosphorus):
        if not self.is_trained:
            self.train(None)
        
        features = np.array([[soil_quality, temperature, rainfall, nitrogen, phosphorus]])
        predicted_yield = self.model.predict(features)[0]
        
        # Generate recommendations based on input parameters
        recommendations = []
        
        # Temperature recommendations
        if temperature < 15:
            recommendations.append("Temperature is low for optimal growth. Consider using row covers or greenhouse techniques.")
        elif temperature > 30:
            recommendations.append("Temperature is high. Increase irrigation and consider shade cloth to protect crops.")
        
        # Rainfall recommendations
        if rainfall < 20:
            recommendations.append("Insufficient rainfall. Supplement with irrigation to maintain soil moisture.")
        elif rainfall > 80:
            recommendations.append("Excessive rainfall. Ensure proper drainage to prevent waterlogging.")
        
        # Nitrogen recommendations
        if nitrogen < 20:
            recommendations.append("Nitrogen levels are low. Apply nitrogen-rich fertilizer to promote leaf growth.")
        
        # Phosphorus recommendations
        if phosphorus < 15:
            recommendations.append("Phosphorus levels are low. Apply phosphorus fertilizer to promote root development.")
        
        # Soil quality recommendations
        if soil_quality < 70:
            recommendations.append("Soil quality is suboptimal. Add organic matter and consider soil testing for specific deficiencies.")
        
        # Additional recommendations based on combinations
        if temperature > 25 and rainfall < 30:
            recommendations.append("Hot and dry conditions. Mulch soil to retain moisture and reduce evaporation.")
        
        if soil_quality > 85 and nitrogen > 30 and phosphorus > 20:
            recommendations.append("Excellent growing conditions. Consider increasing planting density for higher yields.")
        
        return {
            "predicted_yield": predicted_yield,
            "recommendations": recommendations
        }

class PestDiseaseDetector:
    def __init__(self):
        # Simple rule-based system for demonstration
        self.rules = {
            "aphids": {"temperature": (15, 30), "humidity": (50, 80)},
            "fungus": {"humidity": (70, 100), "rainfall": (20, 100)},
            "locusts": {"temperature": (25, 35), "rainfall": (0, 30)},
            "mites": {"temperature": (20, 35), "humidity": (30, 60)},
            "caterpillars": {"temperature": (18, 28), "rainfall": (10, 50)},
            "whiteflies": {"temperature": (20, 30), "humidity": (60, 90)},
            "thrips": {"temperature": (25, 35), "humidity": (40, 70)},
            "nematodes": {"temperature": (20, 30), "rainfall": (30, 80)},
            "borers": {"temperature": (15, 25), "rainfall": (20, 60)},
            "weevils": {"temperature": (18, 30), "humidity": (50, 80)}
        }
    
    def detect(self, temperature, humidity, rainfall):
        risks = {}
        recommendations = []
        
        for pest, conditions in self.rules.items():
            risk_score = 0
            risk_factors = []
            
            if "temperature" in conditions and conditions["temperature"][0] <= temperature <= conditions["temperature"][1]:
                risk_score += 1
                risk_factors.append(f"temperature ({conditions['temperature'][0]}-{conditions['temperature'][1]}°C)")
            
            if "humidity" in conditions and conditions["humidity"][0] <= humidity <= conditions["humidity"][1]:
                risk_score += 1
                risk_factors.append(f"humidity ({conditions['humidity'][0]}-{conditions['humidity'][1]}%)")
            
            if "rainfall" in conditions and conditions["rainfall"][0] <= rainfall <= conditions["rainfall"][1]:
                risk_score += 1
                risk_factors.append(f"rainfall ({conditions['rainfall'][0]}-{conditions['rainfall'][1]}mm)")
            
            # Normalize risk score
            max_score = len(conditions)
            risk_value = risk_score / max_score if max_score > 0 else 0
            risks[pest] = risk_value
            
            # Add recommendations for high-risk pests
            if risk_value > 0.5:
                recommendations.append({
                    "pest": pest.title(),
                    "risk_level": "High" if risk_value > 0.7 else "Medium",
                    "risk_factors": ", ".join(risk_factors),
                    "prevention": self._get_prevention_methods(pest)
                })
        
        return {
            "risks": risks,
            "recommendations": recommendations
        }
    
    def _get_prevention_methods(self, pest):
        prevention_methods = {
            "aphids": "Use reflective mulch, introduce ladybugs, apply neem oil",
            "fungus": "Improve air circulation, avoid overhead watering, apply fungicide",
            "locusts": "Install bird perches, use barriers, apply insecticidal soap",
            "mites": "Increase humidity, introduce predatory mites, apply miticide",
            "caterpillars": "Handpick, use Bacillus thuringiensis, install barriers",
            "whiteflies": "Use yellow sticky traps, introduce parasitic wasps, apply insecticidal soap",
            "thrips": "Remove weeds, use blue sticky traps, apply spinosad",
            "nematodes": "Solarize soil, rotate crops, apply beneficial nematodes",
            "borers": "Remove affected plants, use row covers, apply systemic insecticide",
            "weevils": "Clean up debris, use diatomaceous earth, apply beneficial nematodes"
        }
        return prevention_methods.get(pest, "Monitor regularly and apply appropriate treatments")

class IrrigationOptimizer:
    def __init__(self):
        # Crop-specific water requirements (mm/week)
        self.crop_requirements = {
            "wheat": 25,
            "rice": 50,
            "corn": 30,
            "soybean": 20,
            "cotton": 35,
            "potato": 28,
            "tomato": 22,
            "beans": 18,
            "peas": 15,
            "cabbage": 24
        }
    
    def optimize(self, soil_moisture, crop_type, temperature, rainfall):
        # Get crop-specific optimal moisture level
        crop_requirements = {
            "wheat": {"optimal": 60, "sensitive_stage": "heading"},
            "rice": {"optimal": 80, "sensitive_stage": "flowering"},
            "corn": {"optimal": 55, "sensitive_stage": "tasseling"},
            "soybean": {"optimal": 50, "sensitive_stage": "pod_filling"},
            "cotton": {"optimal": 55, "sensitive_stage": "flowering"},
            "potato": {"optimal": 65, "sensitive_stage": "tuber_initiation"},
            "tomato": {"optimal": 60, "sensitive_stage": "fruit_setting"},
            "beans": {"optimal": 50, "sensitive_stage": "flowering"},
            "peas": {"optimal": 45, "sensitive_stage": "flowering"},
            "cabbage": {"optimal": 55, "sensitive_stage": "head_forming"}
        }
        
        # Get crop-specific parameters
        crop_params = crop_requirements.get(crop_type.lower(), {"optimal": 65, "sensitive_stage": "fruiting"})
        optimal_moisture = crop_params["optimal"]
        sensitive_stage = crop_params["sensitive_stage"]
        
        # Calculate water needed
        moisture_deficit = optimal_moisture - soil_moisture
        
        # Adjust based on temperature and rainfall
        temp_factor = 1 + (temperature - 20) / 100
        rainfall_factor = max(0, 1 - rainfall / 50)
        
        water_needed = max(0, moisture_deficit * temp_factor * rainfall_factor)
        
        # Determine irrigation time
        if temperature < 20:
            irrigation_time = "midday"
            time_reason = "Cooler temperatures reduce evaporation"
        elif temperature < 25:
            irrigation_time = "morning"
            time_reason = "Optimal for plant uptake and growth"
        elif temperature < 30:
            irrigation_time = "early morning or late evening"
            time_reason = "Reduces water loss due to evaporation"
        else:
            irrigation_time = "evening"
            time_reason = "Minimizes evaporation during hot periods"
        
        # Determine irrigation method
        if water_needed < 10:
            irrigation_method = "drip irrigation"
            method_reason = "Precise water delivery with minimal waste"
        elif water_needed < 30:
            irrigation_method = "sprinkler system"
            method_reason = "Even water distribution over larger areas"
        else:
            irrigation_method = "furrow irrigation"
            method_reason = "High-volume watering for large water needs"
        
        # Additional recommendations
        recommendations = []
        
        # Temperature-based recommendations
        if temperature > 35:
            recommendations.append("High temperature stress detected. Increase irrigation frequency to prevent water stress.")
        elif temperature < 10:
            recommendations.append("Low temperature. Reduce irrigation to prevent waterlogging and root damage.")
        
        # Rainfall-based recommendations
        if rainfall > 30:
            recommendations.append("Significant rainfall expected. Delay irrigation to avoid overwatering.")
        elif rainfall < 5:
            recommendations.append("Low rainfall. Increase irrigation to maintain soil moisture.")
        
        # Soil moisture-based recommendations
        if soil_moisture < 30:
            recommendations.append("Critical soil moisture level. Immediate irrigation required to prevent crop stress.")
        elif soil_moisture > 85:
            recommendations.append("Excessive soil moisture. Delay irrigation and check drainage to prevent root rot.")
        
        # Crop-specific recommendations
        if crop_type.lower() == "rice":
            recommendations.append(f"Rice requires consistent flooding during {sensitive_stage} stage.")
        elif crop_type.lower() == "corn":
            recommendations.append(f"Corn is sensitive to water stress during {sensitive_stage} stage. Maintain consistent moisture.")
        
        return {
            "water_needed": round(water_needed, 2),
            "irrigation_time": irrigation_time,
            "irrigation_method": irrigation_method,
            "time_reason": time_reason,
            "method_reason": method_reason,
            "recommendations": recommendations,
            "crop_sensitive_stage": sensitive_stage
        }

class SoilHealthAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, pH, nitrogen, phosphorus, potassium, organic_matter):
        # Simple scoring system for soil health
        scores = {}
        
        # pH score (optimal range 6.0-7.0)
        if 6.0 <= pH <= 7.0:
            scores["pH"] = 100
        elif 5.5 <= pH <= 7.5:
            scores["pH"] = 75
        else:
            scores["pH"] = 50
            
        # Nitrogen score (optimal > 20 ppm)
        scores["nitrogen"] = min(100, nitrogen * 4)
        
        # Phosphorus score (optimal > 15 ppm)
        scores["phosphorus"] = min(100, phosphorus * 5)
        
        # Potassium score (optimal > 200 ppm)
        scores["potassium"] = min(100, potassium * 0.4)
        
        # Organic matter score (optimal > 3%)
        scores["organic_matter"] = min(100, organic_matter * 30)
        
        # Overall health score
        overall_score = sum(scores.values()) / len(scores)
        
        # Detailed recommendations with specific actions
        recommendations = []
        detailed_recommendations = []
        
        if scores["pH"] < 75:
            if pH < 5.5:
                recommendations.append("Soil is too acidic. Add lime to raise pH.")
                detailed_recommendations.append({
                    "issue": "Low pH (Acidic Soil)",
                    "severity": "High" if pH < 5.0 else "Medium",
                    "solution": "Add agricultural lime at 1-2 tons/hectare",
                    "application": "Spread evenly and incorporate into soil 2-3 months before planting",
                    "benefits": "Improves nutrient availability and microbial activity"
                })
            elif pH > 7.5:
                recommendations.append("Soil is too alkaline. Add sulfur to lower pH.")
                detailed_recommendations.append({
                    "issue": "High pH (Alkaline Soil)",
                    "severity": "High" if pH > 8.0 else "Medium",
                    "solution": "Add elemental sulfur at 200-500 kg/hectare",
                    "application": "Apply in fall for best results, water thoroughly after application",
                    "benefits": "Enhances micronutrient availability, especially iron and zinc"
                })
        
        if scores["nitrogen"] < 75:
            recommendations.append("Nitrogen levels are low. Add nitrogen-rich fertilizer or compost.")
            detailed_recommendations.append({
                "issue": "Low Nitrogen",
                "severity": "High" if nitrogen < 10 else "Medium",
                "solution": "Apply ammonium nitrate or organic compost",
                "application": "Side-dress crops with 100-150 kg/hectare nitrogen fertilizer",
                "benefits": "Promotes leaf and stem growth, increases protein content"
            })
        
        if scores["phosphorus"] < 75:
            recommendations.append("Phosphorus levels are low. Apply phosphorus fertilizer.")
            detailed_recommendations.append({
                "issue": "Low Phosphorus",
                "severity": "High" if phosphorus < 8 else "Medium",
                "solution": "Apply superphosphate or bone meal",
                "application": "Apply 50-100 kg/hectare and incorporate into soil before planting",
                "benefits": "Promotes root development and flowering"
            })
        
        if scores["potassium"] < 75:
            recommendations.append("Potassium levels are low. Add potassium fertilizer.")
            detailed_recommendations.append({
                "issue": "Low Potassium",
                "severity": "High" if potassium < 100 else "Medium",
                "solution": "Apply muriate of potash (potassium chloride)",
                "application": "Apply 100-200 kg/hectare and side-dress during crop growth",
                "benefits": "Improves disease resistance and water regulation"
            })
        
        if scores["organic_matter"] < 75:
            recommendations.append("Organic matter is low. Incorporate compost or manure.")
            detailed_recommendations.append({
                "issue": "Low Organic Matter",
                "severity": "High" if organic_matter < 1.5 else "Medium",
                "solution": "Add compost, manure, or cover crops",
                "application": "Apply 5-10 tons/hectare of well-aged compost annually",
                "benefits": "Improves soil structure, water retention, and microbial activity"
            })
        
        # Additional recommendations based on combinations of factors
        if scores["nitrogen"] < 50 and scores["organic_matter"] < 50:
            detailed_recommendations.append({
                "issue": "Severely Depleted Soil",
                "severity": "High",
                "solution": "Implement comprehensive soil restoration program",
                "application": "Plant cover crops, add organic amendments, and practice crop rotation",
                "benefits": "Restores soil fertility and structure over 1-2 growing seasons"
            })
        
        return {
            "scores": scores,
            "overall_score": round(overall_score, 2),
            "recommendations": recommendations,
            "detailed_recommendations": detailed_recommendations
        }

class CropRotationPlanner:
    def __init__(self):
        # Crop families and their nutrient requirements/benefits
        self.crop_families = {
            "legumes": ["beans", "peas", "soybeans", "alfalfa"],
            "brassicas": ["cabbage", "broccoli", "cauliflower", "brussels sprouts"],
            "solanaceae": ["tomatoes", "potatoes", "peppers", "eggplants"],
            "cucurbits": ["cucumbers", "squash", "melons", "pumpkins"],
            "grains": ["wheat", "corn", "rice", "barley"],
            "roots": ["carrots", "beets", "radishes", "turnips"]
        }
        
        # Nutrient effects of each family
        self.nutrient_effects = {
            "legumes": {"nitrogen": 20, "phosphorus": 5, "potassium": 5},
            "brassicas": {"nitrogen": -10, "phosphorus": -5, "potassium": -5},
            "solanaceae": {"nitrogen": -15, "phosphorus": -10, "potassium": -5},
            "cucurbits": {"nitrogen": -5, "phosphorus": -5, "potassium": -5},
            "grains": {"nitrogen": -20, "phosphorus": -10, "potassium": -10},
            "roots": {"nitrogen": -5, "phosphorus": -10, "potassium": -5}
        }
    
    def plan_rotation(self, last_crop, soil_nitrogen, soil_phosphorus, soil_potassium):
        # Determine crop family of last crop
        last_family = None
        for family, crops in self.crop_families.items():
            if last_crop.lower() in crops:
                last_family = family
                break
        
        if not last_family:
            # If crop not found, default to grains
            last_family = "grains"
        
        # Calculate soil health score
        soil_score = (soil_nitrogen + soil_phosphorus + soil_potassium) / 3
        
        # Recommend next crops based on rotation principles
        recommendations = []
        
        # Avoid planting from same family consecutively
        for family, crops in self.crop_families.items():
            if family != last_family:
                # Check if this family would benefit soil health
                effects = self.nutrient_effects[family]
                expected_improvement = (
                    effects["nitrogen"] * soil_nitrogen / 100 +
                    effects["phosphorus"] * soil_phosphorus / 100 +
                    effects["potassium"] * soil_potassium / 100
                )
                
                # Add top 3 crops from this family
                for crop in crops[:3]:
                    recommendations.append({
                        "crop": crop.title(),
                        "family": family.title(),
                        "benefit_score": round(expected_improvement, 2),
                        "reason": f"Follows {last_crop.title()} in rotation"
                    })
        
        # Sort by benefit score
        recommendations.sort(key=lambda x: x["benefit_score"], reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations

class FertilizerRecommendationSystem:
    def __init__(self):
        pass
    
    def recommend(self, crop_type, soil_nitrogen, soil_phosphorus, soil_potassium, target_yield):
        # Fertilizer recommendations based on crop type and soil conditions
        recommendations = []
        
        # Nitrogen recommendations
        if soil_nitrogen < 20:
            nitrogen_needed = 50 - soil_nitrogen
            recommendations.append({
                "nutrient": "Nitrogen",
                "amount": round(nitrogen_needed, 2),
                "fertilizer": "Ammonium Nitrate (34-0-0)",
                "application_rate": f"{round(nitrogen_needed * 2, 2)} kg/hectare"
            })
        
        # Phosphorus recommendations
        if soil_phosphorus < 15:
            phosphorus_needed = 25 - soil_phosphorus
            recommendations.append({
                "nutrient": "Phosphorus",
                "amount": round(phosphorus_needed, 2),
                "fertilizer": "Superphosphate (0-46-0)",
                "application_rate": f"{round(phosphorus_needed * 3, 2)} kg/hectare"
            })
        
        # Potassium recommendations
        if soil_potassium < 200:
            potassium_needed = 250 - soil_potassium
            recommendations.append({
                "nutrient": "Potassium",
                "amount": round(potassium_needed, 2),
                "fertilizer": "Muriate of Potash (0-0-60)",
                "application_rate": f"{round(potassium_needed * 2, 2)} kg/hectare"
            })
        
        # Crop-specific recommendations
        crop_factors = {
            "wheat": {"n": 1.2, "p": 1.0, "k": 0.8},
            "rice": {"n": 1.5, "p": 0.8, "k": 1.0},
            "corn": {"n": 1.3, "p": 1.1, "k": 0.9},
            "soybean": {"n": 0.5, "p": 1.2, "k": 1.0},  # Legumes fix nitrogen
            "cotton": {"n": 1.1, "p": 0.9, "k": 1.3},
            "potato": {"n": 0.9, "p": 1.3, "k": 1.1},
            "tomato": {"n": 1.0, "p": 1.2, "k": 1.2}
        }
        
        if crop_type.lower() in crop_factors:
            factors = crop_factors[crop_type.lower()]
            for rec in recommendations:
                if rec["nutrient"] == "Nitrogen":
                    rec["application_rate"] = f"{round(float(rec['application_rate'].split()[0]) * factors['n'], 2)} kg/hectare"
                elif rec["nutrient"] == "Phosphorus":
                    rec["application_rate"] = f"{round(float(rec['application_rate'].split()[0]) * factors['p'], 2)} kg/hectare"
                elif rec["nutrient"] == "Potassium":
                    rec["application_rate"] = f"{round(float(rec['application_rate'].split()[0]) * factors['k'], 2)} kg/hectare"
        
        return recommendations

class DiseaseIdentifier:
    def __init__(self):
        # Simple rule-based disease identification
        self.disease_symptoms = {
            "blight": ["yellowing leaves", "dark spots", "wilting"],
            "rust": ["orange spots", "powdery coating", "leaf drop"],
            "mildew": ["white coating", "leaf curling", "stunted growth"],
            "rot": ["soft spots", "foul odor", "mushy texture"],
            "wilt": ["sudden wilting", "stem discoloration", "yellowing"],
            "scab": ["rough patches", "corky texture", "small lesions"],
            "mosaic": ["mottled leaves", "stunted growth", "yellow patterns"]
        }
    
    def identify(self, symptoms):
        # Match symptoms to possible diseases
        matches = {}
        
        for disease, disease_symptoms in self.disease_symptoms.items():
            match_count = 0
            for symptom in symptoms:
                if symptom.lower() in [s.lower() for s in disease_symptoms]:
                    match_count += 1
            
            if match_count > 0:
                match_score = match_count / len(disease_symptoms)
                matches[disease] = round(match_score, 2)
        
        # Sort by match score
        sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for disease, score in sorted_matches[:5]:  # Top 5 matches
            results.append({
                "disease": disease.title(),
                "confidence": score,
                "treatment": self._get_treatment(disease)
            })
        
        return results
    
    def _get_treatment(self, disease):
        treatments = {
            "blight": "Apply copper-based fungicide and remove affected plants",
            "rust": "Use sulfur-based fungicide and improve air circulation",
            "mildew": "Apply neem oil and reduce humidity",
            "rot": "Improve drainage and apply fungicide",
            "wilt": "Remove affected plants and solarize soil",
            "scab": "Apply fungicide and practice crop rotation",
            "mosaic": "Control insect vectors and remove infected plants"
        }
        return treatments.get(disease.lower(), "Consult agricultural extension service for specific treatment")

# Initialize ML models and advanced features
yield_predictor = CropYieldPredictor()
pest_detector = PestDiseaseDetector()
irrigation_optimizer = IrrigationOptimizer()
soil_analyzer = SoilHealthAnalyzer()
crop_rotation_planner = CropRotationPlanner()
fertilizer_recommender = FertilizerRecommendationSystem()
disease_identifier = DiseaseIdentifier()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    
    # Get farm count
    c.execute('SELECT COUNT(*) FROM farms')
    farm_count = c.fetchone()[0]
    
    # Get recent soil data
    c.execute('''SELECT s.*, f.name as farm_name 
                 FROM soil_data s 
                 JOIN farms f ON s.farm_id = f.id 
                 ORDER BY s.date DESC LIMIT 5''')
    recent_soil_data = c.fetchall()
    
    # Get recent crop data
    c.execute('''SELECT c.*, f.name as farm_name 
                 FROM crop_data c 
                 JOIN farms f ON c.farm_id = f.id 
                 ORDER BY c.planting_date DESC LIMIT 5''')
    recent_crop_data = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                          farm_count=farm_count,
                          recent_soil_data=recent_soil_data,
                          recent_crop_data=recent_crop_data)

@app.route('/farmers')
def farmers():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT * FROM farmers')
    farmers = c.fetchall()
    conn.close()
    return render_template('farmers.html', farmers=farmers)

@app.route('/add_farmer', methods=['GET', 'POST'])
def add_farmer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        location = request.form['location']
        
        conn = sqlite3.connect('agri_ai.db')
        c = conn.cursor()
        c.execute('INSERT INTO farmers (name, email, phone, location) VALUES (?, ?, ?, ?)',
                  (name, email, phone, location))
        conn.commit()
        conn.close()
        
        return redirect(url_for('farmers'))
    
    return render_template('add_farmer.html')

@app.route('/farms')
def farms():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('''SELECT f.*, fm.name as farmer_name 
                 FROM farms f 
                 JOIN farmers fm ON f.farmer_id = fm.id''')
    farms = c.fetchall()
    conn.close()
    return render_template('farms.html', farms=farms)

@app.route('/add_farm', methods=['GET', 'POST'])
def add_farm():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        name = request.form['name']
        size = request.form['size']
        location = request.form['location']
        
        conn = sqlite3.connect('agri_ai.db')
        c = conn.cursor()
        c.execute('INSERT INTO farms (farmer_id, name, size, location) VALUES (?, ?, ?, ?)',
                  (farmer_id, name, size, location))
        conn.commit()
        conn.close()
        
        return redirect(url_for('farms'))
    
    # Get farmers for dropdown
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM farmers')
    farmers = c.fetchall()
    conn.close()
    
    return render_template('add_farm.html', farmers=farmers)

@app.route('/soil_data')
def soil_data():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('''SELECT s.*, f.name as farm_name 
                 FROM soil_data s 
                 JOIN farms f ON s.farm_id = f.id 
                 ORDER BY s.date DESC''')
    soil_data = c.fetchall()
    conn.close()
    return render_template('soil_data.html', soil_data=soil_data)

@app.route('/add_soil_data', methods=['GET', 'POST'])
def add_soil_data():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        date = request.form['date']
        pH = request.form['pH']
        nitrogen = request.form['nitrogen']
        phosphorus = request.form['phosphorus']
        potassium = request.form['potassium']
        organic_matter = request.form['organic_matter']
        
        conn = sqlite3.connect('agri_ai.db')
        c = conn.cursor()
        c.execute('''INSERT INTO soil_data 
                     (farm_id, date, pH, nitrogen, phosphorus, potassium, organic_matter) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (farm_id, date, pH, nitrogen, phosphorus, potassium, organic_matter))
        conn.commit()
        conn.close()
        
        return redirect(url_for('soil_data'))
    
    # Get farms for dropdown
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM farms')
    farms = c.fetchall()
    conn.close()
    
    return render_template('add_soil_data.html', farms=farms)

@app.route('/weather_data')
def weather_data():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('''SELECT w.*, f.name as farm_name 
                 FROM weather_data w 
                 JOIN farms f ON w.farm_id = f.id 
                 ORDER BY w.date DESC''')
    weather_data = c.fetchall()
    conn.close()
    return render_template('weather_data.html', weather_data=weather_data)

@app.route('/add_weather_data', methods=['GET', 'POST'])
def add_weather_data():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        date = request.form['date']
        temperature = request.form['temperature']
        humidity = request.form['humidity']
        rainfall = request.form['rainfall']
        
        conn = sqlite3.connect('agri_ai.db')
        c = conn.cursor()
        c.execute('''INSERT INTO weather_data 
                     (farm_id, date, temperature, humidity, rainfall) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (farm_id, date, temperature, humidity, rainfall))
        conn.commit()
        conn.close()
        
        return redirect(url_for('weather_data'))
    
    # Get farms for dropdown
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM farms')
    farms = c.fetchall()
    conn.close()
    
    return render_template('add_weather_data.html', farms=farms)

@app.route('/crop_data')
def crop_data():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('''SELECT c.*, f.name as farm_name 
                 FROM crop_data c 
                 JOIN farms f ON c.farm_id = f.id 
                 ORDER BY c.planting_date DESC''')
    crop_data = c.fetchall()
    conn.close()
    return render_template('crop_data.html', crop_data=crop_data)

@app.route('/add_crop_data', methods=['GET', 'POST'])
def add_crop_data():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        crop_type = request.form['crop_type']
        planting_date = request.form['planting_date']
        expected_harvest_date = request.form['expected_harvest_date']
        expected_yield = request.form['expected_yield']
        
        conn = sqlite3.connect('agri_ai.db')
        c = conn.cursor()
        c.execute('''INSERT INTO crop_data 
                     (farm_id, crop_type, planting_date, expected_harvest_date, expected_yield) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (farm_id, crop_type, planting_date, expected_harvest_date, expected_yield))
        conn.commit()
        conn.close()
        
        return redirect(url_for('crop_data'))
    
    # Get farms for dropdown
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM farms')
    farms = c.fetchall()
    conn.close()
    
    return render_template('add_crop_data.html', farms=farms)

@app.route('/predict_yield', methods=['GET', 'POST'])
def predict_yield():
    prediction = None
    if request.method == 'POST':
        soil_quality = float(request.form['soil_quality'])
        temperature = float(request.form['temperature'])
        rainfall = float(request.form['rainfall'])
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorus'])
        
        prediction = yield_predictor.predict(soil_quality, temperature, rainfall, nitrogen, phosphorus)
    
    return render_template('predict_yield.html', prediction=prediction)

@app.route('/detect_pests', methods=['GET', 'POST'])
def detect_pests():
    risks = None
    if request.method == 'POST':
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        rainfall = float(request.form['rainfall'])
        
        risks = pest_detector.detect(temperature, humidity, rainfall)
    
    return render_template('detect_pests.html', risks=risks)

@app.route('/optimize_irrigation', methods=['GET', 'POST'])
def optimize_irrigation():
    recommendation = None
    if request.method == 'POST':
        soil_moisture = float(request.form['soil_moisture'])
        crop_type = request.form['crop_type']
        temperature = float(request.form['temperature'])
        rainfall = float(request.form['rainfall'])
        
        recommendation = irrigation_optimizer.optimize(soil_moisture, crop_type, temperature, rainfall)
    
    return render_template('optimize_irrigation.html', recommendation=recommendation)

@app.route('/analyze_soil', methods=['GET', 'POST'])
def analyze_soil():
    analysis = None
    if request.method == 'POST':
        pH = float(request.form['pH'])
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorus'])
        potassium = float(request.form['potassium'])
        organic_matter = float(request.form['organic_matter'])
        
        analysis = soil_analyzer.analyze(pH, nitrogen, phosphorus, potassium, organic_matter)
    
    return render_template('analyze_soil.html', analysis=analysis)

@app.route('/plan_rotation', methods=['GET', 'POST'])
def plan_rotation():
    recommendations = None
    if request.method == 'POST':
        last_crop = request.form['last_crop']
        soil_nitrogen = float(request.form['soil_nitrogen'])
        soil_phosphorus = float(request.form['soil_phosphorus'])
        soil_potassium = float(request.form['soil_potassium'])
        
        recommendations = crop_rotation_planner.plan_rotation(
            last_crop, soil_nitrogen, soil_phosphorus, soil_potassium)
    
    return render_template('plan_rotation.html', recommendations=recommendations)

@app.route('/recommend_fertilizer', methods=['GET', 'POST'])
def recommend_fertilizer():
    recommendations = None
    if request.method == 'POST':
        crop_type = request.form['crop_type']
        soil_nitrogen = float(request.form['soil_nitrogen'])
        soil_phosphorus = float(request.form['soil_phosphorus'])
        soil_potassium = float(request.form['soil_potassium'])
        target_yield = float(request.form['target_yield'])
        
        recommendations = fertilizer_recommender.recommend(
            crop_type, soil_nitrogen, soil_phosphorus, soil_potassium, target_yield)
    
    return render_template('recommend_fertilizer.html', recommendations=recommendations)

@app.route('/identify_disease', methods=['GET', 'POST'])
def identify_disease():
    results = None
    if request.method == 'POST':
        # Get symptoms from form (multiple checkboxes)
        symptoms = request.form.getlist('symptoms')
        # Add any custom symptoms
        custom_symptoms = request.form.get('custom_symptoms')
        if custom_symptoms:
            symptoms.extend(custom_symptoms.split(','))
        
        results = disease_identifier.identify(symptoms)
    
    return render_template('identify_disease.html', results=results)

@app.route('/market_data')
def market_data():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT * FROM market_data ORDER BY date DESC')
    market_data = c.fetchall()
    conn.close()
    return render_template('market_data.html', market_data=market_data)

@app.route('/add_market_data', methods=['GET', 'POST'])
def add_market_data():
    if request.method == 'POST':
        crop_type = request.form['crop_type']
        date = request.form['date']
        price = request.form['price']
        location = request.form['location']
        
        conn = sqlite3.connect('agri_ai.db')
        c = conn.cursor()
        c.execute('INSERT INTO market_data (crop_type, date, price, location) VALUES (?, ?, ?, ?)',
                  (crop_type, date, price, location))
        conn.commit()
        conn.close()
        
        return redirect(url_for('market_data'))
    
    return render_template('add_market_data.html')

@app.route('/sustainability')
def sustainability():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('''SELECT s.*, f.name as farm_name
                 FROM sustainability_data s
                 JOIN farms f ON s.farm_id = f.id
                 ORDER BY s.date DESC''')
    sustainability_data = c.fetchall()
    conn.close()
    return render_template('sustainability.html', sustainability_data=sustainability_data)

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/add_sustainability_data', methods=['GET', 'POST'])
def add_sustainability_data():
    if request.method == 'POST':
        farm_id = request.form['farm_id']
        date = request.form['date']
        carbon_footprint = request.form['carbon_footprint']
        water_usage = request.form['water_usage']
        energy_usage = request.form['energy_usage']
        
        conn = sqlite3.connect('agri_ai.db')
        c = conn.cursor()
        c.execute('''INSERT INTO sustainability_data 
                     (farm_id, date, carbon_footprint, water_usage, energy_usage) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (farm_id, date, carbon_footprint, water_usage, energy_usage))
        conn.commit()
        conn.close()
        
        return redirect(url_for('sustainability'))
    
    # Get farms for dropdown
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM farms')
    farms = c.fetchall()
    conn.close()
    
    return render_template('add_sustainability_data.html', farms=farms)

# API endpoints
@app.route('/api/farms')
def api_farms():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT * FROM farms')
    farms = c.fetchall()
    conn.close()
    
    # Convert to JSON
    farm_list = []
    for farm in farms:
        farm_list.append({
            'id': farm[0],
            'farmer_id': farm[1],
            'name': farm[2],
            'size': farm[3],
            'location': farm[4]
        })
    
    return jsonify(farm_list)

@app.route('/api/soil_data')
def api_soil_data():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT * FROM soil_data')
    soil_data = c.fetchall()
    conn.close()
    
    # Convert to JSON
    soil_list = []
    for data in soil_data:
        soil_list.append({
            'id': data[0],
            'farm_id': data[1],
            'date': data[2],
            'pH': data[3],
            'nitrogen': data[4],
            'phosphorus': data[5],
            'potassium': data[6],
            'organic_matter': data[7]
        })
    
    return jsonify(soil_list)

@app.route('/api/weather_data')
def api_weather_data():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT * FROM weather_data')
    weather_data = c.fetchall()
    conn.close()
    
    # Convert to JSON
    weather_list = []
    for data in weather_data:
        weather_list.append({
            'id': data[0],
            'farm_id': data[1],
            'date': data[2],
            'temperature': data[3],
            'humidity': data[4],
            'rainfall': data[5]
        })
    
    return jsonify(weather_list)

@app.route('/api/sustainability_data')
def api_sustainability_data():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sustainability_data')
    sustainability_data = c.fetchall()
    conn.close()
    
    # Convert to JSON
    sustainability_list = []
    for data in sustainability_data:
        sustainability_list.append({
            'id': data[0],
            'farm_id': data[1],
            'date': data[2],
            'carbon_footprint': data[3],
            'water_usage': data[4],
            'energy_usage': data[5]
        })
    
    return jsonify(sustainability_list)

@app.route('/api/environmental_impact')
def api_environmental_impact():
    conn = sqlite3.connect('agri_ai.db')
    c = conn.cursor()
    
    # Get total carbon footprint
    c.execute('SELECT SUM(carbon_footprint) FROM sustainability_data')
    total_carbon = c.fetchone()[0] or 0
    
    # Get total water usage
    c.execute('SELECT SUM(water_usage) FROM sustainability_data')
    total_water = c.fetchone()[0] or 0
    
    # Get total energy usage
    c.execute('SELECT SUM(energy_usage) FROM sustainability_data')
    total_energy = c.fetchone()[0] or 0
    
    # Get farm count
    c.execute('SELECT COUNT(*) FROM farms')
    farm_count = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_carbon_footprint': total_carbon,
        'total_water_usage': total_water,
        'total_energy_usage': total_energy,
        'farm_count': farm_count,
        'avg_carbon_per_farm': total_carbon / farm_count if farm_count > 0 else 0
    })

if __name__ == '__main__':
    app.run(debug=True)
