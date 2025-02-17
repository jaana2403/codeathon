import pandas as pd
import numpy as np
import random
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

# Generate sophisticated synthetic dataset
def generate_synthetic_data(num_employees=500):
    np.random.seed(42)
    random.seed(42)
    
    employee_ids = [f'EMP{str(i).zfill(4)}' for i in range(1, num_employees + 1)]
    working_hours = np.random.normal(40, 12, num_employees).clip(20, 80)
    overtime_hours = np.random.randint(0, 20, num_employees)
    sick_leaves = np.random.randint(0, 10, num_employees)
    projects_completed = np.random.randint(1, 10, num_employees)
    
    efficiency = 100 - (abs(working_hours - 40) / 40) * 50  # Efficiency drops for too high/low hours
    burnout_risk = np.where(working_hours > 55, 1, 0)
    engagement_score = np.clip(100 - sick_leaves * 5 - overtime_hours * 2, 0, 100)
    performance_score = efficiency - burnout_risk * 10 + projects_completed * 2 + np.random.normal(0, 5, num_employees)
    
    # Impact Scale based on efficiency and burnout risk
    impact_scale = np.where(efficiency < 50, 'High', np.where(efficiency < 75, 'Moderate', 'Low'))
    
    # Recovery Time Objective (RTO) estimation (in days)
    rto = np.where(burnout_risk == 1, np.random.randint(10, 30, num_employees), np.random.randint(1, 10, num_employees))
    
    data = pd.DataFrame({
        'Employee_ID': employee_ids,
        'Working_Hours': working_hours,
        'Overtime_Hours': overtime_hours,
        'Sick_Leaves': sick_leaves,
        'Projects_Completed': projects_completed,
        'Efficiency_Score': efficiency,
        'Burnout_Risk': burnout_risk,
        'Engagement_Score': engagement_score,
        'Performance_Score': performance_score,
        'Impact_Scale': impact_scale,
        'RTO_Days': rto
    })
    
    return data

data = generate_synthetic_data()

# Categorize Employees into more levels
def categorize_employees(data):
    conditions = [
        (data['Working_Hours'] < 30),
        (data['Working_Hours'] >= 30) & (data['Working_Hours'] < 38),
        (data['Working_Hours'] >= 38) & (data['Working_Hours'] <= 46),
        (data['Working_Hours'] > 46) & (data['Working_Hours'] <= 55),
        (data['Working_Hours'] > 55)
    ]
    categories = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    data['Category'] = np.select(conditions, categories, default='Unknown')  # Fix: Added default string value
    return data

data = categorize_employees(data)

# Train a more advanced predictive model
def train_predictive_model(data):
    features = ['Working_Hours', 'Overtime_Hours', 'Sick_Leaves', 'Projects_Completed']
    target = 'Performance_Score'
    
    X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2, random_state=42)
    
    model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f'Model MAE: {mae:.2f}')
    
    return model

model = train_predictive_model(data)

# Save input and output data to Excel
def save_to_excel(data, filename='Employee_Impact_Assessment.xlsx'):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Assessment', index=False)
        summary = data.groupby('Category').agg({
            'Working_Hours': ['mean', 'std'],
            'Overtime_Hours': ['mean', 'std'],
            'Sick_Leaves': ['mean', 'std'],
            'Projects_Completed': ['mean', 'std'],
            'Efficiency_Score': ['mean', 'std'],
            'Engagement_Score': ['mean', 'std'],
            'Performance_Score': ['mean', 'std'],
            'Burnout_Risk': ['sum'],
            'RTO_Days': ['mean', 'std'],
            'Impact_Scale': lambda x: x.value_counts().index[0]
        })
        summary.to_excel(writer, sheet_name='Summary')
    print(f'Data successfully saved to {filename}')

save_to_excel(data)

# Visualization of working hours vs performance
plt.figure(figsize=(10, 6))
sns.scatterplot(x=data['Working_Hours'], y=data['Performance_Score'], hue=data['Impact_Scale'], palette='coolwarm')
plt.title('Working Hours vs Performance Score')
plt.xlabel('Working Hours')
plt.ylabel('Performance Score')
plt.legend(title='Impact Scale')
plt.show()
