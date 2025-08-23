import pandas as pd
from datetime import datetime, timedelta
import io
from typing import Dict, List
import csv

def calculate_bmr(weight: float, height: int, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if gender.lower() == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    return bmr

def calculate_daily_calories(bmr: float, activity_level: str) -> float:
    """Calculate daily calorie needs based on BMR and activity level"""
    activity_multipliers = {
        "Sedentary (little/no exercise)": 1.2,
        "Lightly active (light exercise 1-3 days/week)": 1.375,
        "Moderately active (moderate exercise 3-5 days/week)": 1.55,
        "Very active (hard exercise 6-7 days/week)": 1.725,
        "Extremely active (very hard exercise, physical job)": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.2)
    return bmr * multiplier

def calculate_macro_percentages(protein: float, carbs: float, fat: float) -> Dict[str, float]:
    """Calculate macronutrient percentages by calories"""
    protein_calories = protein * 4
    carb_calories = carbs * 4
    fat_calories = fat * 9
    
    total_calories = protein_calories + carb_calories + fat_calories
    
    if total_calories == 0:
        return {'protein': 0, 'carbs': 0, 'fat': 0}
    
    return {
        'protein': round((protein_calories / total_calories) * 100, 1),
        'carbs': round((carb_calories / total_calories) * 100, 1),
        'fat': round((fat_calories / total_calories) * 100, 1)
    }

def get_nutrition_insights(daily_totals: Dict, target_calories: float = None) -> List[str]:
    """Generate nutrition insights based on daily totals"""
    insights = []
    
    if not daily_totals:
        return ["No nutrition data available for analysis."]
    
    calories = daily_totals.get('total_calories', 0)
    protein = daily_totals.get('total_protein', 0)
    carbs = daily_totals.get('total_carbs', 0)
    fat = daily_totals.get('total_fat', 0)
    
    # Calorie insights
    if target_calories:
        calorie_diff = calories - target_calories
        if calorie_diff > 200:
            insights.append(f"You're {calorie_diff:.0f} calories over your target. Consider reducing portion sizes.")
        elif calorie_diff < -200:
            insights.append(f"You're {abs(calorie_diff):.0f} calories under your target. Consider adding a healthy snack.")
        else:
            insights.append("Your calorie intake is well-aligned with your target!")
    
    # Protein insights
    if calories > 0:
        protein_percentage = (protein * 4 / calories) * 100
        if protein_percentage < 10:
            insights.append("Consider increasing protein intake for better muscle maintenance and satiety.")
        elif protein_percentage > 35:
            insights.append("Your protein intake is quite high. Make sure to balance with carbs and fats.")
        else:
            insights.append(f"Good protein intake! ({protein_percentage:.1f}% of calories)")
    
    # Hydration reminder (if applicable)
    if len(insights) < 3:
        insights.append("Don't forget to stay hydrated throughout the day!")
    
    return insights

def format_nutrition_summary(meal_logs: List[Dict], days: int = 7) -> Dict:
    """Create a comprehensive nutrition summary"""
    if not meal_logs:
        return {'error': 'No meal data available'}
    
    # Calculate totals
    total_meals = len(meal_logs)
    total_calories = sum(meal.get('calories', 0) for meal in meal_logs)
    total_protein = sum(meal.get('protein', 0) for meal in meal_logs)
    total_carbs = sum(meal.get('carbs', 0) for meal in meal_logs)
    total_fat = sum(meal.get('fat', 0) for meal in meal_logs)
    
    # Calculate averages
    avg_calories = total_calories / days if days > 0 else 0
    avg_protein = total_protein / days if days > 0 else 0
    avg_carbs = total_carbs / days if days > 0 else 0
    avg_fat = total_fat / days if days > 0 else 0
    
    # Meal type breakdown
    meal_types = {}
    for meal in meal_logs:
        meal_type = meal.get('meal_type', 'Unknown')
        meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
    
    # Calculate macro percentages
    macro_percentages = calculate_macro_percentages(total_protein, total_carbs, total_fat)
    
    return {
        'period_days': days,
        'total_meals': total_meals,
        'totals': {
            'calories': round(total_calories, 1),
            'protein': round(total_protein, 1),
            'carbs': round(total_carbs, 1),
            'fat': round(total_fat, 1)
        },
        'daily_averages': {
            'calories': round(avg_calories, 1),
            'protein': round(avg_protein, 1),
            'carbs': round(avg_carbs, 1),
            'fat': round(avg_fat, 1)
        },
        'meal_distribution': meal_types,
        'macro_percentages': macro_percentages
    }

def export_progress_to_csv(db_manager, start_date: str, end_date: str, export_type: str = "All Data") -> str:
    """Export user progress data to CSV format"""
    try:
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        if export_type == "All Data":
            # Export comprehensive data
            writer.writerow(['Export Date', datetime.now().strftime("%Y-%m-%d %H:%M")])
            writer.writerow(['Data Period', f"{start_date} to {end_date}"])
            writer.writerow([])  # Empty row
            
            # Meal logs
            meal_data = db_manager.get_progress_data(start_date, end_date)
            if meal_data:
                writer.writerow(['=== MEAL LOGS ==='])
                writer.writerow(['Date', 'Time', 'Meal Name', 'Meal Type', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)'])
                for meal in meal_data:
                    writer.writerow([
                        meal['date'], meal['time'], meal['meal_name'], meal['meal_type'],
                        meal['calories'], meal['protein'], meal['carbs'], meal['fat']
                    ])
                writer.writerow([])  # Empty row
            
            # Water logs
            water_data = db_manager.get_water_logs(start_date, end_date)
            if water_data:
                writer.writerow(['=== WATER INTAKE LOGS ==='])
                writer.writerow(['Date/Time', 'Amount (ml)'])
                for water in water_data:
                    writer.writerow([water['date'], water['amount']])
                writer.writerow([])  # Empty row
            
            # Mood logs
            mood_data = db_manager.get_mood_logs(start_date, end_date)
            if mood_data:
                writer.writerow(['=== MOOD LOGS ==='])
                writer.writerow(['Date/Time', 'Rating (1-10)', 'Notes'])
                for mood in mood_data:
                    writer.writerow([mood['date'], mood['rating'], mood['notes']])
        
        elif export_type == "Meal Logs Only":
            meal_data = db_manager.get_progress_data(start_date, end_date)
            writer.writerow(['Date', 'Time', 'Meal Name', 'Meal Type', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)'])
            for meal in meal_data:
                writer.writerow([
                    meal['date'], meal['time'], meal['meal_name'], meal['meal_type'],
                    meal['calories'], meal['protein'], meal['carbs'], meal['fat']
                ])
        
        elif export_type == "Water Intake Only":
            water_data = db_manager.get_water_logs(start_date, end_date)
            writer.writerow(['Date/Time', 'Amount (ml)'])
            for water in water_data:
                writer.writerow([water['date'], water['amount']])
        
        elif export_type == "Mood Logs Only":
            mood_data = db_manager.get_mood_logs(start_date, end_date)
            writer.writerow(['Date/Time', 'Rating (1-10)', 'Notes'])
            for mood in mood_data:
                writer.writerow([mood['date'], mood['rating'], mood['notes']])
        
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        return csv_content if csv_content.strip() else None
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

def validate_nutrition_data(calories: float, protein: float, carbs: float, fat: float) -> Dict[str, str]:
    """Validate nutrition data and return any errors"""
    errors = {}
    
    if calories < 0 or calories > 10000:
        errors['calories'] = "Calories must be between 0 and 10,000"
    
    if protein < 0 or protein > 500:
        errors['protein'] = "Protein must be between 0 and 500g"
    
    if carbs < 0 or carbs > 1000:
        errors['carbs'] = "Carbohydrates must be between 0 and 1,000g"
    
    if fat < 0 or fat > 500:
        errors['fat'] = "Fat must be between 0 and 500g"
    
    # Check if macros roughly match calories (allowing for some variance)
    calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
    if calories > 0 and calculated_calories > 0:
        variance = abs(calories - calculated_calories) / calories
        if variance > 0.5:  # 50% variance threshold
            errors['macros'] = "Macro breakdown doesn't align well with total calories"
    
    return errors

def get_meal_timing_insights(meal_logs: List[Dict]) -> List[str]:
    """Analyze meal timing patterns and provide insights"""
    insights = []
    
    if not meal_logs:
        return ["No meal timing data available for analysis."]
    
    # Group meals by time of day
    morning_meals = []
    afternoon_meals = []
    evening_meals = []
    
    for meal in meal_logs:
        try:
            time_str = meal.get('time', '12:00')
            hour = int(time_str.split(':')[0])
            
            if 5 <= hour < 12:
                morning_meals.append(meal)
            elif 12 <= hour < 17:
                afternoon_meals.append(meal)
            else:
                evening_meals.append(meal)
        except (ValueError, IndexError):
            continue
    
    # Generate insights based on timing patterns
    total_meals = len(meal_logs)
    
    if len(morning_meals) / total_meals < 0.2:
        insights.append("You tend to skip morning meals. Consider having a healthy breakfast to boost energy.")
    
    if len(evening_meals) / total_meals > 0.5:
        insights.append("Most of your meals are in the evening. Try distributing meals more evenly throughout the day.")
    
    if len(afternoon_meals) / total_meals > 0.6:
        insights.append("Great job having substantial midday nutrition!")
    
    # Check for very late meals
    late_meals = sum(1 for meal in meal_logs 
                    if meal.get('time', '').startswith(('21:', '22:', '23:')))
    
    if late_meals > total_meals * 0.3:
        insights.append("You eat late quite often. Try to have your last meal 2-3 hours before bedtime.")
    
    if not insights:
        insights.append("Your meal timing patterns look balanced!")
    
    return insights

def calculate_weekly_trends(meal_logs: List[Dict]) -> Dict:
    """Calculate weekly nutrition trends"""
    if not meal_logs:
        return {}
    
    # Convert meal logs to DataFrame for easier analysis
    df = pd.DataFrame(meal_logs)
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.isocalendar().week
    
    # Calculate weekly averages
    weekly_stats = df.groupby('week').agg({
        'calories': ['sum', 'mean', 'count'],
        'protein': ['sum', 'mean'],
        'carbs': ['sum', 'mean'],
        'fat': ['sum', 'mean']
    }).round(2)
    
    return weekly_stats.to_dict() if not weekly_stats.empty else {}
