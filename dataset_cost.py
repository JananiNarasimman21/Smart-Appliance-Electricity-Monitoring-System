import pandas as pd
import os
from tariff import slab_tariff  # your slab function

# Load dataset
dataset_path = "dataset/refit_data.csv"
df = pd.read_csv(dataset_path)

# Convert 'Time' column to datetime
df['Time'] = pd.to_datetime(df['Time'])
df['date'] = df['Time'].dt.date
df['month'] = df['Time'].dt.month
df['year'] = df['Time'].dt.year

appliance_columns = [
'Appliance1','Appliance2','Appliance3','Appliance4','Appliance5',
'Appliance6','Appliance7','Appliance8','Appliance9'
]

appliance_names = [
'Geyser','Fridge','Microwave','AirConditioner','WashingMachine',
'Television','WaterPurifier','ElectricKettle','LaptopCharger'
]
# Output folder
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# Process each appliance
for col, name in zip(appliance_columns, appliance_names):
    # Convert energy from Wh to kWh
    df[col + '_kWh'] = df[col] / 1000.0
    
    # Daily energy & cost
    daily = df.groupby('date')[col + '_kWh'].sum().reset_index()
    daily['cost'] = daily[col + '_kWh'].apply(slab_tariff)
    
    # Monthly energy & cost
    monthly = df.groupby(['year','month'])[col + '_kWh'].sum().reset_index()
    monthly['cost'] = monthly[col + '_kWh'].apply(slab_tariff)
    
    # Save CSVs
    daily_file = os.path.join(output_folder, f"{name}_daily.csv")
    monthly_file = os.path.join(output_folder, f"{name}_monthly.csv")
    daily.to_csv(daily_file, index=False)
    monthly.to_csv(monthly_file, index=False)
    
    print(f"Saved {name} daily & monthly CSV in {output_folder}/")

# Optional: print sample for first appliance
print("\nSample daily energy & cost for Geyser:")
print(daily.head(10))
print("\nSample monthly energy & cost for Geyser:")
print(monthly.head(12))