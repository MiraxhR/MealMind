import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from database import DatabaseManager
from meal_recommender import MealRecommender
from nutrition_api import OpenFoodFactsAPI
from utils import calculate_bmr, calculate_daily_calories, export_progress_to_csv
import os

# Initialize session state
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'meal_recommender' not in st.session_state:
    st.session_state.meal_recommender = MealRecommender()
if 'nutrition_api' not in st.session_state:
    st.session_state.nutrition_api = OpenFoodFactsAPI()

def main():
    st.set_page_config(
        page_title="AI Meal Planner & Wellness Tracker",
        page_icon="🍎",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🍎 AI-Powered Meal Planner & Wellness Tracker")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "User Profile", 
        "Meal Recommendations", 
        "Food Logging", 
        "Progress Dashboard",
        "Export Data"
    ])
    
    # Initialize database
    st.session_state.db_manager.init_database()
    
    if page == "User Profile":
        show_user_profile()
    elif page == "Meal Recommendations":
        show_meal_recommendations()
    elif page == "Food Logging":
        show_food_logging()
    elif page == "Progress Dashboard":
        show_progress_dashboard()
    elif page == "Export Data":
        show_export_data()

def show_user_profile():
    st.header("👤 User Profile & Preferences")
    
    with st.form("user_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", value=st.session_state.user_profile.get('name', '') if st.session_state.user_profile else '')
            age = st.number_input("Age", min_value=18, max_value=120, value=st.session_state.user_profile.get('age', 25) if st.session_state.user_profile else 25)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=st.session_state.user_profile.get('weight', 70.0) if st.session_state.user_profile else 70.0)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=st.session_state.user_profile.get('height', 170) if st.session_state.user_profile else 170)
            gender = st.selectbox("Gender", ["Male", "Female"], index=0 if not st.session_state.user_profile else (0 if st.session_state.user_profile.get('gender') == 'Male' else 1))
        
        with col2:
            activity_level = st.selectbox("Activity Level", [
                "Sedentary (little/no exercise)",
                "Lightly active (light exercise 1-3 days/week)",
                "Moderately active (moderate exercise 3-5 days/week)",
                "Very active (hard exercise 6-7 days/week)",
                "Extremely active (very hard exercise, physical job)"
            ], index=st.session_state.user_profile.get('activity_level', 1) if st.session_state.user_profile else 1)
            
            goal = st.selectbox("Health Goal", [
                "Maintain weight",
                "Lose weight",
                "Gain weight",
                "Build muscle",
                "Improve overall health"
            ], index=st.session_state.user_profile.get('goal', 0) if st.session_state.user_profile else 0)
            
            dietary_restrictions = st.multiselect("Dietary Restrictions", [
                "Vegetarian", "Vegan", "Gluten-free", "Dairy-free", 
                "Nut-free", "Keto", "Paleo", "Low-sodium", "Diabetic-friendly"
            ], default=st.session_state.user_profile.get('dietary_restrictions', []) if st.session_state.user_profile else [])
            
            allergies = st.text_area("Allergies (separate with commas)", 
                                   value=st.session_state.user_profile.get('allergies', '') if st.session_state.user_profile else '')
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            # Calculate daily calorie needs
            bmr = calculate_bmr(weight, height, age, gender)
            daily_calories = calculate_daily_calories(bmr, activity_level)
            
            profile_data = {
                'name': name,
                'age': age,
                'weight': weight,
                'height': height,
                'gender': gender,
                'activity_level': activity_level,
                'goal': goal,
                'dietary_restrictions': dietary_restrictions,
                'allergies': allergies,
                'daily_calories': daily_calories,
                'bmr': bmr
            }
            
            # Save to database
            st.session_state.db_manager.save_user_profile(profile_data)
            st.session_state.user_profile = profile_data
            
            st.success("Profile saved successfully!")
            st.info(f"Your estimated daily calorie needs: {daily_calories:.0f} calories")
            st.rerun()
    
    # Display current profile if exists
    if st.session_state.user_profile:
        st.subheader("Current Profile")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Daily Calories", f"{st.session_state.user_profile['daily_calories']:.0f}")
            st.metric("BMR", f"{st.session_state.user_profile['bmr']:.0f}")
        
        with col2:
            st.write(f"**Goal:** {st.session_state.user_profile['goal']}")
            if st.session_state.user_profile['dietary_restrictions']:
                st.write(f"**Dietary Restrictions:** {', '.join(st.session_state.user_profile['dietary_restrictions'])}")

def show_meal_recommendations():
    st.header("🤖 AI Meal Recommendations")
    
    if not st.session_state.user_profile:
        st.warning("Please set up your user profile first to get personalized recommendations.")
        return
    
    meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
    
    if st.button("Get AI Recommendations"):
        with st.spinner("Generating personalized meal recommendations..."):
            try:
                recommendations = st.session_state.meal_recommender.get_recommendations(
                    st.session_state.user_profile, meal_type
                )
                
                if recommendations:
                    st.subheader(f"Recommended {meal_type} Options")
                    
                    for i, meal in enumerate(recommendations):
                        with st.expander(f"🍽️ {meal['name']}", expanded=i == 0):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Description:** {meal['description']}")
                                st.write(f"**Ingredients:** {', '.join(meal['ingredients'])}")
                                
                                if meal.get('preparation_time'):
                                    st.write(f"**Prep Time:** {meal['preparation_time']} minutes")
                                
                                if st.button(f"Log this meal", key=f"log_{i}"):
                                    # Add to food log
                                    log_data = {
                                        'meal_name': meal['name'],
                                        'meal_type': meal_type,
                                        'calories': meal['calories'],
                                        'protein': meal.get('protein', 0),
                                        'carbs': meal.get('carbs', 0),
                                        'fat': meal.get('fat', 0),
                                        'date': datetime.now().strftime("%Y-%m-%d"),
                                        'time': datetime.now().strftime("%H:%M")
                                    }
                                    
                                    st.session_state.db_manager.log_meal(log_data)
                                    st.success(f"Added {meal['name']} to your food log!")
                                    st.rerun()
                            
                            with col2:
                                # Nutrition info
                                st.metric("Calories", f"{meal['calories']}")
                                if meal.get('protein'):
                                    st.metric("Protein", f"{meal['protein']}g")
                                if meal.get('carbs'):
                                    st.metric("Carbs", f"{meal['carbs']}g")
                                if meal.get('fat'):
                                    st.metric("Fat", f"{meal['fat']}g")
                
                else:
                    st.error("Failed to generate recommendations. Please try again.")
                    
            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")

def show_food_logging():
    st.header("📝 Food & Wellness Logging")
    
    tab1, tab2, tab3 = st.tabs(["Log Meal", "Log Water & Mood", "Recent Logs"])
    
    with tab1:
        st.subheader("Log a Meal")
        
        with st.form("meal_log_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                meal_name = st.text_input("Meal Name")
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
                food_search = st.text_input("Search Food Item (OpenFoodFacts)")
                
                if food_search and st.form_submit_button("Search Nutrition Data"):
                    with st.spinner("Searching nutrition data..."):
                        nutrition_data = st.session_state.nutrition_api.search_food(food_search)
                        if nutrition_data:
                            st.session_state.nutrition_search_result = nutrition_data
                        else:
                            st.error("No nutrition data found for this item.")
            
            with col2:
                # Manual nutrition input
                calories = st.number_input("Calories", min_value=0, value=0)
                protein = st.number_input("Protein (g)", min_value=0.0, value=0.0)
                carbs = st.number_input("Carbs (g)", min_value=0.0, value=0.0)
                fat = st.number_input("Fat (g)", min_value=0.0, value=0.0)
            
            # Show nutrition data if found
            if hasattr(st.session_state, 'nutrition_search_result'):
                st.subheader("Found Nutrition Data")
                data = st.session_state.nutrition_search_result
                st.write(f"**Product:** {data.get('product_name', 'Unknown')}")
                
                # Auto-populate form fields
                calories = data.get('energy_kcal_100g', 0)
                protein = data.get('proteins_100g', 0)
                carbs = data.get('carbohydrates_100g', 0)
                fat = data.get('fat_100g', 0)
            
            submitted = st.form_submit_button("Log Meal")
            
            if submitted and meal_name:
                log_data = {
                    'meal_name': meal_name,
                    'meal_type': meal_type,
                    'calories': calories,
                    'protein': protein,
                    'carbs': carbs,
                    'fat': fat,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'time': datetime.now().strftime("%H:%M")
                }
                
                st.session_state.db_manager.log_meal(log_data)
                st.success(f"Logged {meal_name} successfully!")
                
                # Clear search result
                if hasattr(st.session_state, 'nutrition_search_result'):
                    del st.session_state.nutrition_search_result
                
                st.rerun()
    
    with tab2:
        st.subheader("Log Water Intake & Mood")
        
        col1, col2 = st.columns(2)
        
        with col1:
            water_intake = st.number_input("Water Intake (ml)", min_value=0, max_value=5000, value=250)
            if st.button("Log Water"):
                st.session_state.db_manager.log_water(water_intake, datetime.now().strftime("%Y-%m-%d %H:%M"))
                st.success(f"Logged {water_intake}ml of water!")
                st.rerun()
        
        with col2:
            mood_rating = st.slider("Mood Rating (1-10)", min_value=1, max_value=10, value=5)
            mood_notes = st.text_area("Mood Notes (optional)", max_chars=200)
            
            if st.button("Log Mood"):
                st.session_state.db_manager.log_mood(mood_rating, mood_notes, datetime.now().strftime("%Y-%m-%d %H:%M"))
                st.success("Mood logged successfully!")
                st.rerun()
    
    with tab3:
        st.subheader("Recent Logs")
        
        # Show recent meals
        recent_meals = st.session_state.db_manager.get_recent_meals(7)
        if recent_meals:
            st.write("**Recent Meals (Last 7 days):**")
            df_meals = pd.DataFrame(recent_meals)
            st.dataframe(df_meals, use_container_width=True)
        else:
            st.info("No meal logs found.")
        
        # Show today's totals
        today = datetime.now().strftime("%Y-%m-%d")
        daily_totals = st.session_state.db_manager.get_daily_nutrition_totals(today)
        
        if daily_totals:
            st.subheader("Today's Nutrition Totals")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Calories", f"{daily_totals['total_calories']:.0f}")
            with col2:
                st.metric("Protein", f"{daily_totals['total_protein']:.1f}g")
            with col3:
                st.metric("Carbs", f"{daily_totals['total_carbs']:.1f}g")
            with col4:
                st.metric("Fat", f"{daily_totals['total_fat']:.1f}g")

def show_progress_dashboard():
    st.header("📊 Progress Dashboard")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Get progress data
    progress_data = st.session_state.db_manager.get_progress_data(
        start_date.strftime("%Y-%m-%d"), 
        end_date.strftime("%Y-%m-%d")
    )
    
    if not progress_data:
        st.info("No data available for the selected date range.")
        return
    
    df = pd.DataFrame(progress_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Daily calorie tracking
    st.subheader("📈 Daily Calorie Intake")
    
    daily_calories = df.groupby('date')['calories'].sum().reset_index()
    
    fig_calories = px.line(daily_calories, x='date', y='calories', 
                          title='Daily Calorie Intake Over Time',
                          markers=True)
    
    # Add target calorie line if user profile exists
    if st.session_state.user_profile:
        target_calories = st.session_state.user_profile['daily_calories']
        fig_calories.add_hline(y=target_calories, line_dash="dash", 
                              annotation_text=f"Target: {target_calories:.0f} cal")
    
    st.plotly_chart(fig_calories, use_container_width=True)
    
    # Macro breakdown
    st.subheader("🥗 Macronutrient Breakdown")
    
    macro_totals = df[['protein', 'carbs', 'fat']].sum()
    
    fig_macros = go.Figure(data=[go.Pie(
        labels=['Protein', 'Carbohydrates', 'Fat'],
        values=[macro_totals['protein'] * 4, macro_totals['carbs'] * 4, macro_totals['fat'] * 9],
        hole=0.3
    )])
    fig_macros.update_layout(title="Macronutrient Distribution (Calories)")
    
    st.plotly_chart(fig_macros, use_container_width=True)
    
    # Weekly averages
    st.subheader("📅 Weekly Averages")
    
    df['week'] = df['date'].dt.isocalendar().week
    weekly_avg = df.groupby('week').agg({
        'calories': 'mean',
        'protein': 'mean',
        'carbs': 'mean',
        'fat': 'mean'
    }).round(1)
    
    if not weekly_avg.empty:
        st.dataframe(weekly_avg, use_container_width=True)
    
    # Meal type distribution
    st.subheader("🍽️ Meal Type Distribution")
    
    meal_type_counts = df['meal_type'].value_counts()
    fig_meals = px.bar(x=meal_type_counts.index, y=meal_type_counts.values,
                       title="Number of Logged Meals by Type")
    st.plotly_chart(fig_meals, use_container_width=True)
    
    # Water and mood tracking if available
    water_data = st.session_state.db_manager.get_water_logs(
        start_date.strftime("%Y-%m-%d"), 
        end_date.strftime("%Y-%m-%d")
    )
    
    if water_data:
        st.subheader("💧 Water Intake")
        df_water = pd.DataFrame(water_data)
        df_water['date'] = pd.to_datetime(df_water['date']).dt.date
        daily_water = df_water.groupby('date')['amount'].sum().reset_index()
        
        fig_water = px.bar(daily_water, x='date', y='amount',
                          title='Daily Water Intake (ml)')
        st.plotly_chart(fig_water, use_container_width=True)
    
    mood_data = st.session_state.db_manager.get_mood_logs(
        start_date.strftime("%Y-%m-%d"), 
        end_date.strftime("%Y-%m-%d")
    )
    
    if mood_data:
        st.subheader("😊 Mood Tracking")
        df_mood = pd.DataFrame(mood_data)
        df_mood['date'] = pd.to_datetime(df_mood['date']).dt.date
        avg_mood = df_mood.groupby('date')['rating'].mean().reset_index()
        
        fig_mood = px.line(avg_mood, x='date', y='rating',
                          title='Average Daily Mood Rating',
                          markers=True, range_y=[1, 10])
        st.plotly_chart(fig_mood, use_container_width=True)

def show_export_data():
    st.header("📤 Export Your Data")
    
    st.info("Export your progress data to CSV format for external analysis or backup.")
    
    # Date range for export
    col1, col2 = st.columns(2)
    with col1:
        export_start = st.date_input("Export Start Date", value=datetime.now() - timedelta(days=30))
    with col2:
        export_end = st.date_input("Export End Date", value=datetime.now())
    
    export_type = st.selectbox("Select Data Type", [
        "All Data",
        "Meal Logs Only", 
        "Water Intake Only",
        "Mood Logs Only"
    ])
    
    if st.button("Generate Export"):
        try:
            csv_data = export_progress_to_csv(
                st.session_state.db_manager,
                export_start.strftime("%Y-%m-%d"),
                export_end.strftime("%Y-%m-%d"),
                export_type
            )
            
            if csv_data:
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"wellness_data_{export_start}_{export_end}.csv",
                    mime="text/csv"
                )
                st.success("Export generated successfully!")
            else:
                st.warning("No data available for the selected criteria.")
                
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
    
    # Show data summary
    st.subheader("Data Summary")
    
    total_meals = len(st.session_state.db_manager.get_recent_meals(365))  # Last year
    total_water_logs = len(st.session_state.db_manager.get_water_logs(
        (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    ))
    total_mood_logs = len(st.session_state.db_manager.get_mood_logs(
        (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    ))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Meals Logged", total_meals)
    with col2:
        st.metric("Water Logs", total_water_logs)
    with col3:
        st.metric("Mood Logs", total_mood_logs)

if __name__ == "__main__":
    main()
