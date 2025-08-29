import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('agri_ai.db')
c = conn.cursor()

# Clear existing data
tables = ['sustainability_data', 'market_data', 'pest_disease_data', 'irrigation_data', 'crop_data', 'weather_data', 'soil_data', 'farms', 'farmers']
for table in tables:
    c.execute(f'DELETE FROM {table}')

# Add sample farmers
farmers = [
    ('John Smith', 'john@example.com', '123-456-7890', 'California'),
    ('Jane Doe', 'jane@example.com', '098-765-4321', 'Iowa'),
    ('Bob Johnson', 'bob@example.com', '555-123-4567', 'Texas'),
    ('Alice Brown', 'alice@example.com', '555-987-6543', 'Florida')
]

c.executemany('INSERT INTO farmers (name, email, phone, location) VALUES (?, ?, ?, ?)', farmers)

# Add sample farms
farms = [
    (1, 'Smith Family Farm', 150.5, 'California'),
    (2, 'Doe Agricultural Co.', 200.0, 'Iowa'),
    (3, 'Johnson Farmstead', 175.2, 'Texas'),
    (4, 'Brown Acres', 120.8, 'Florida')
]

c.executemany('INSERT INTO farms (farmer_id, name, size, location) VALUES (?, ?, ?, ?)', farms)

# Add sample soil data
soil_data = []
for i in range(20):
    farm_id = random.randint(1, 4)
    date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
    pH = round(random.uniform(5.5, 7.5), 1)
    nitrogen = round(random.uniform(10, 50), 1)
    phosphorus = round(random.uniform(5, 30), 1)
    potassium = round(random.uniform(50, 300), 1)
    organic_matter = round(random.uniform(1, 10), 1)
    soil_data.append((farm_id, date, pH, nitrogen, phosphorus, potassium, organic_matter))

c.executemany('''INSERT INTO soil_data 
                 (farm_id, date, pH, nitrogen, phosphorus, potassium, organic_matter) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', soil_data)

# Add sample weather data
weather_data = []
for i in range(50):
    farm_id = random.randint(1, 4)
    date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
    temperature = round(random.uniform(10, 35), 1)
    humidity = random.randint(30, 90)
    rainfall = round(random.uniform(0, 50), 1)
    weather_data.append((farm_id, date, temperature, humidity, rainfall))

c.executemany('''INSERT INTO weather_data 
                 (farm_id, date, temperature, humidity, rainfall) 
                 VALUES (?, ?, ?, ?, ?)''', weather_data)

# Add sample crop data
crop_types = ['wheat', 'rice', 'corn', 'soybean', 'cotton', 'potato', 'tomato']
crop_data = []
for i in range(15):
    farm_id = random.randint(1, 4)
    crop_type = random.choice(crop_types)
    planting_date = (datetime.now() - timedelta(days=random.randint(30, 150))).strftime('%Y-%m-%d')
    expected_harvest_date = (datetime.now() + timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d')
    actual_harvest_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d') if random.random() > 0.5 else None
    expected_yield = round(random.uniform(1, 5), 2)
    actual_yield = round(expected_yield * random.uniform(0.8, 1.2), 2) if actual_harvest_date else None
    crop_data.append((farm_id, crop_type, planting_date, expected_harvest_date, actual_harvest_date, expected_yield, actual_yield))

c.executemany('''INSERT INTO crop_data 
                 (farm_id, crop_type, planting_date, expected_harvest_date, actual_harvest_date, expected_yield, actual_yield) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', crop_data)

# Add sample market data
market_data = []
for i in range(30):
    crop_type = random.choice(crop_types)
    date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
    price = round(random.uniform(100, 500), 2)
    location = random.choice(['California', 'Iowa', 'Texas', 'Florida'])
    market_data.append((crop_type, date, price, location))

c.executemany('INSERT INTO market_data (crop_type, date, price, location) VALUES (?, ?, ?, ?)', market_data)

# Add sample sustainability data
sustainability_data = []
for i in range(25):
    farm_id = random.randint(1, 4)
    date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
    carbon_footprint = round(random.uniform(1, 10), 2)
    water_usage = round(random.uniform(1000, 10000), 2)
    energy_usage = round(random.uniform(500, 5000), 2)
    sustainability_data.append((farm_id, date, carbon_footprint, water_usage, energy_usage))

c.executemany('''INSERT INTO sustainability_data 
                 (farm_id, date, carbon_footprint, water_usage, energy_usage) 
                 VALUES (?, ?, ?, ?, ?)''', sustainability_data)

# Commit changes and close connection
conn.commit()
conn.close()

print("Sample data populated successfully!")