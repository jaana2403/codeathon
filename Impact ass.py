import pandas as pd
import numpy as np
import random
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

# Generation of synthetic data of 500 rows
def generate_synthetic_data(num_employees=500):
    np.random.seed(42)
    random.seed(42)
    
    employee_ids = [f'EMP{str(i).zfill(4)}' for i in range(1, num_employees + 1)]
    working_hours = np.random.normal(40, 12, num_employees).clip(20, 80)
    overtime_hours = np.random.randint(0, 20, num_employees)
    sick_leaves = np.random.randint(0, 10, num_employees)
    projects_completed = np.random.randint(1, 10, num_employees)
    
    efficiency = 100 - (abs(working_hours - 40) / 40) * 50
    burnout_risk = np.where(working_hours > 55, 1, 0)
    engagement_score = np.clip(100 - sick_leaves * 5 - overtime_hours * 2, 0, 100)
    performance_score = efficiency - burnout_risk * 10 + projects_completed * 2 + np.random.normal(0, 5, num_employees)
    
    impact_scale = np.where(efficiency < 50, 'High', np.where(efficiency < 75, 'Moderate', 'Low'))
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

# Added categorize_employees function
def categorize_employees(data):
    """
    Categorize employees based on their working hours into different levels
    """
    conditions = [
        (data['Working_Hours'] < 30),
        (data['Working_Hours'] >= 30) & (data['Working_Hours'] < 38),
        (data['Working_Hours'] >= 38) & (data['Working_Hours'] <= 46),
        (data['Working_Hours'] > 46) & (data['Working_Hours'] <= 55),
        (data['Working_Hours'] > 55)
    ]
    categories = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    data['Category'] = np.select(conditions, categories, default='Unknown')
    return data

# Added train_predictive_model function
def train_predictive_model(data):
    """
    Train an XGBoost model to predict performance scores
    """
    features = ['Working_Hours', 'Overtime_Hours', 'Sick_Leaves', 'Projects_Completed']
    target = 'Performance_Score'
    
    X_train, X_test, y_train, y_test = train_test_split(
        data[features], data[target], test_size=0.2, random_state=42
    )
    
    model = xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f'Model MAE: {mae:.2f}')
    
    return model

# Generates detailed rto analysis based on the data
def generate_rto_analysis(data):
    """
    Generate detailed RTO analysis based on impact levels and various metrics
    """
    # Calculate additional RTO factors
    data['Workload_Intensity'] = (data['Working_Hours'] + data['Overtime_Hours']) / 40
    data['Risk_Factor'] = (data['Burnout_Risk'] * 2 + 
                          (data['Sick_Leaves'] / 10) + 
                          (data['Workload_Intensity'] - 1))
    
    # Generate detailed RTO recommendations
    def get_rto_recommendation(row):
        base_message = f"Employee {row['Employee_ID']} - "
        
        if row['Impact_Scale'] == 'High':
            if row['Burnout_Risk'] == 1:
                return (base_message + 
                       f"Critical attention required. Recommended RTO: {row['RTO_Days']} days. "
                       f"High workload intensity ({row['Workload_Intensity']:.1f}x) detected. "
                       "Immediate workload redistribution advised. Consider mandatory time off "
                       "and wellness program enrollment.")
            else:
                return (base_message +
                       f"Preventive measures needed. Recommended RTO: {row['RTO_Days']} days. "
                       "Review project allocation and implement regular check-ins.")
                
        elif row['Impact_Scale'] == 'Moderate':
            return (base_message +
                   f"Monitor closely. Suggested RTO: {row['RTO_Days']} days. "
                   f"Current efficiency at {row['Efficiency_Score']:.1f}%. "
                   "Consider flexible working arrangements.")
            
        else:  # Low Impact
            return (base_message +
                   f"Maintenance level. Standard RTO: {row['RTO_Days']} days. "
                   "Continue regular performance reviews.")

    # Generate RTO analysis for each employee
    data['RTO_Analysis'] = data.apply(get_rto_recommendation, axis=1)
    
    # Generate summary statistics
    rto_summary = {
        'impact_level': [],
        'avg_rto': [],
        'risk_profile': [],
        'recommendations': []
    }
    
    for impact in ['High', 'Moderate', 'Low']:
        impact_data = data[data['Impact_Scale'] == impact]
        avg_rto = impact_data['RTO_Days'].mean()
        avg_risk = impact_data['Risk_Factor'].mean()
        
        risk_profile = ("High risk" if avg_risk > 2 else 
                       "Medium risk" if avg_risk > 1 else 
                       "Low risk")
        
        recommendation = (
            "Immediate intervention required. Implement team rebalancing." if impact == 'High'
            else "Regular monitoring and preventive measures advised." if impact == 'Moderate'
            else "Maintain current workforce management practices."
        )
        
        rto_summary['impact_level'].append(impact)
        rto_summary['avg_rto'].append(avg_rto)
        rto_summary['risk_profile'].append(risk_profile)
        rto_summary['recommendations'].append(recommendation)
    
    return data, pd.DataFrame(rto_summary)

# Saved output in excel
def save_to_excel(data, rto_summary, filename='Employee_Impact_Assessment.xlsx'):
    # Create a copy of data without RTO analysis for the assessment sheet
    assessment_data = data.drop(['Workload_Intensity', 'Risk_Factor', 'RTO_Analysis'], axis=1, errors='ignore')
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Save basic assessment data without RTO analysis
        assessment_data.to_excel(writer, sheet_name='Assessment', index=False)
        
        # Basic summary statistics without RTO metrics
        summary = assessment_data.groupby('Category').agg({
            'Working_Hours': ['mean', 'std'],
            'Overtime_Hours': ['mean', 'std'],
            'Sick_Leaves': ['mean', 'std'],
            'Projects_Completed': ['mean', 'std'],
            'Efficiency_Score': ['mean', 'std'],
            'Engagement_Score': ['mean', 'std'],
            'Performance_Score': ['mean', 'std'],
            'Burnout_Risk': ['sum'],
            'Impact_Scale': lambda x: x.value_counts().index[0]
        })
        summary.to_excel(writer, sheet_name='Summary')
        
        # RTO Analysis sheet
        rto_summary.to_excel(writer, sheet_name='RTO_Analysis', index=False)
        
        # Detailed RTO recommendations with complete analysis
        rto_recommendations = pd.DataFrame({
            'Employee_ID': data['Employee_ID'],
            'Impact_Scale': data['Impact_Scale'],
            'Workload_Intensity': data['Workload_Intensity'],
            'Risk_Factor': data['Risk_Factor'],
            'RTO_Days': data['RTO_Days'],
            'RTO_Analysis': data['RTO_Analysis']
        })
        rto_recommendations.to_excel(writer, sheet_name='RTO_Recommendations', index=False)
        
    print(f'Data successfully saved to {filename}')

# Main execution
if __name__ == "__main__":
    data = generate_synthetic_data()
    data = categorize_employees(data)
    model = train_predictive_model(data)
    data, rto_summary = generate_rto_analysis(data)
    save_to_excel(data, rto_summary)

    # Visualization
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(data['Working_Hours'], 
                         data['Performance_Score'],
                         c=data['RTO_Days'],
                         cmap='YlOrRd',
                         s=100,
                         alpha=0.6)
    plt.colorbar(scatter, label='RTO Days')
    plt.title('Working Hours vs Performance Score (with RTO Days)')
    plt.xlabel('Working Hours')
    plt.ylabel('Performance Score')
    plt.show()
