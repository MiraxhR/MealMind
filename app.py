import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from database import DatabaseManager
from meal_recommender import MealRecommender
from nutrition_api import OpenFoodFactsAPI
from utils import calculate_bmr, calculate_daily_calories, export_progress_to_csv, format_nutrition_summary
import os
import random

def get_ai_coach_message(user_profile):
    """AI Wellness Coach - Provides personalized coaching messages"""
    messages = []
    
    # Get current time for time-based messages
    current_hour = datetime.now().hour
    goal = user_profile.get('goal', '').lower()
    
    # Time-based coaching
    if 6 <= current_hour < 10:
        messages.append("🌅 Good morning! Start your day with a nutritious breakfast.")
    elif 11 <= current_hour < 14:
        messages.append("🌞 Lunch time! Keep your energy up with a balanced meal.")
    elif 17 <= current_hour < 20:
        messages.append("🌆 Dinner time! Consider lighter options for the evening.")
    elif 20 <= current_hour < 23:
        messages.append("🌙 Evening wind-down. Stay hydrated and avoid late snacking.")
    
    # Goal-specific coaching
    if 'lose weight' in goal:
        coach_tips = [
            "Focus on protein and fiber to stay fuller longer",
            "Try drinking water before meals to help with portion control",
            "Small, consistent changes lead to lasting results"
        ]
        messages.append(random.choice(coach_tips))
    elif 'gain weight' in goal or 'build muscle' in goal:
        coach_tips = [
            "Include protein in every meal to support muscle growth",
            "Don't forget healthy fats - nuts, avocado, olive oil",
            "Consistency is key for building muscle mass"
        ]
        messages.append(random.choice(coach_tips))
    else:
        general_tips = [
            "Balance is key - aim for variety in your meals",
            "Listen to your body's hunger and fullness cues",
            "Small steps lead to big changes over time"
        ]
        messages.append(random.choice(general_tips))
    
    # Motivational messages
    motivation = [
        "You're doing great! Every healthy choice counts.",
        "Progress, not perfection. Keep going!",
        "Your future self will thank you for these healthy habits.",
        "One meal at a time, one day at a time. You've got this!"
    ]
    
    if len(messages) < 2:
        messages.append(random.choice(motivation))
    
    return messages[:2]  # Return max 2 messages to avoid clutter

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
    
    # AI Wellness Coach sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🤖 AI Wellness Coach")
        
        if st.session_state.user_profile:
            coach_messages = get_ai_coach_message(st.session_state.user_profile)
            for message in coach_messages:
                st.info(f"💡 {message}")
        else:
            st.info("👋 Set up your profile to get personalized AI coaching!")
        
        # Quick stats if user has data
        recent_meals = st.session_state.db_manager.get_recent_meals(1)
        if recent_meals:
            st.metric("Today's Meals", len(recent_meals))
        
        st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "User Profile", 
        "AI Meal Recommendations", 
        "Last-Minute Meal Ideas",
        "Food Logging", 
        "Progress Dashboard",
        "AI Insights & Predictions",
        "Export & Share Data"
    ])
    
    # Initialize database
    st.session_state.db_manager.init_database()
    
    if page == "User Profile":
        show_user_profile()
    elif page == "AI Meal Recommendations":
        show_meal_recommendations()
    elif page == "Last-Minute Meal Ideas":
        show_quick_meals()
    elif page == "Food Logging":
        show_food_logging()
    elif page == "Progress Dashboard":
        show_progress_dashboard()
    elif page == "AI Insights & Predictions":
        show_ai_insights()
    elif page == "Export & Share Data":
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

def show_quick_meals():
    st.header("⚡ Last-Minute Meal Ideas")
    st.subheader("Quick & Easy Meals Ready in 15 Minutes or Less!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        dietary_filter = st.multiselect("Filter by Dietary Preferences", [
            "Vegetarian", "Vegan", "Gluten-free", "Dairy-free", "Keto"
        ])
    
    with col2:
        if st.button("Get Quick Ideas", type="primary"):
            with st.spinner("Finding quick meal ideas..."):
                quick_meals = st.session_state.meal_recommender.get_quick_meal_ideas(dietary_filter)
                st.session_state.quick_meals = quick_meals
    
    # Show quick meal suggestions
    if hasattr(st.session_state, 'quick_meals') and st.session_state.quick_meals:
        st.subheader("🍽️ Quick Meal Solutions")
        
        for i, meal in enumerate(st.session_state.quick_meals):
            with st.expander(f"⚡ {meal['name']} - {meal.get('preparation_time', 15)} min", expanded=i == 0):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Type:** {meal.get('meal_type', 'Any time')}")
                    st.write(f"**Description:** {meal['description']}")
                    st.write(f"**Ingredients:** {', '.join(meal['ingredients'][:5])}...")
                    
                    if meal.get('dietary_tags'):
                        tags_str = " ".join([f"`{tag}`" for tag in meal['dietary_tags']])
                        st.write(f"**Tags:** {tags_str}")
                
                with col2:
                    st.metric("⏱️ Prep Time", f"{meal.get('preparation_time', 15)} min")
                    st.metric("🔥 Calories", f"{meal['calories']}")
                    
                    if st.button(f"Log This Meal", key=f"quick_log_{i}"):
                        log_data = {
                            'meal_name': meal['name'],
                            'meal_type': meal.get('meal_type', 'Snack'),
                            'calories': meal['calories'],
                            'protein': meal.get('protein', 0),
                            'carbs': meal.get('carbs', 0),
                            'fat': meal.get('fat', 0),
                            'date': datetime.now().strftime("%Y-%m-%d"),
                            'time': datetime.now().strftime("%H:%M")
                        }
                        st.session_state.db_manager.log_meal(log_data)
                        st.success(f"✅ Added {meal['name']} to your log!")
                        st.rerun()
    
    # Emergency meal tips
    st.subheader("🚨 Emergency Meal Tips")
    st.info("""
    **Super Quick Options (under 5 minutes):**
    • Greek yogurt + berries + granola
    • Peanut butter banana wrap
    • Hard-boiled egg + avocado toast
    • Protein smoothie with frozen fruits
    • Nuts + cheese + apple slices
    """)

def show_ai_insights():
    st.header("🤖 AI Insights & Predictions")
    
    if not st.session_state.user_profile:
        st.warning("⚠️ Please set up your user profile first to get personalized AI insights.")
        return
    
    # Get recent meal data for analysis
    recent_meals = st.session_state.db_manager.get_recent_meals(14)  # Last 2 weeks
    
    if not recent_meals:
        st.info("📊 No meal data available yet. Start logging meals to get AI insights!")
        return
    
    # Analyze nutrition patterns
    analysis = st.session_state.meal_recommender.analyze_nutrition_patterns(recent_meals)
    
    if 'error' not in analysis:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Your Nutrition Patterns")
            st.metric("Average Daily Calories", f"{analysis['avg_calories']}")
            st.metric("Average Protein", f"{analysis['avg_protein']}g")
            st.metric("Meals Analyzed", analysis['total_meals_analyzed'])
            
        with col2:
            st.subheader("🍽️ Meal Distribution")
            if analysis['meal_distribution']:
                meal_dist_df = pd.DataFrame(list(analysis['meal_distribution'].items()), 
                                          columns=['Meal Type', 'Count'])
                fig = px.pie(meal_dist_df, values='Count', names='Meal Type', 
                           title="Your Meal Type Distribution")
                st.plotly_chart(fig, use_container_width=True)
    
    # AI Predictions & Insights
    st.subheader("🔮 AI Predictions & Recommendations")
    
    target_calories = st.session_state.user_profile.get('daily_calories', 2000)
    goal = st.session_state.user_profile.get('goal', '').lower()
    
    # Generate predictions
    predictions = []
    
    if 'error' not in analysis:
        avg_calories = analysis['avg_calories']
        
        if 'lose weight' in goal:
            daily_deficit = target_calories - avg_calories
            if daily_deficit > 0:
                weeks_to_goal = 4  # Rough estimate
                predictions.append(f"🎯 At your current pace, you could reach your weight loss goal in approximately {weeks_to_goal} weeks!")
            else:
                predictions.append("⚖️ Consider reducing portions slightly to create a calorie deficit for weight loss.")
        
        elif 'gain weight' in goal or 'build muscle' in goal:
            if avg_calories < target_calories:
                predictions.append("📈 Consider adding healthy, high-calorie snacks to meet your muscle-building goals.")
            else:
                predictions.append("💪 Your calorie intake looks good for muscle building! Keep up the protein intake.")
        
        # Macro balance prediction
        protein_ratio = (analysis['avg_protein'] * 4) / avg_calories if avg_calories > 0 else 0
        if protein_ratio < 0.15:
            predictions.append("🥩 Increase protein intake - aim for 15-30% of your daily calories from protein.")
        elif protein_ratio > 0.35:
            predictions.append("🥗 Consider balancing your protein with more carbs and healthy fats.")
        else:
            predictions.append("✅ Your protein intake is well-balanced!")
    
    # Display predictions
    for i, prediction in enumerate(predictions, 1):
        st.success(f"{i}. {prediction}")
    
    # Personalized insights
    if 'insights' in analysis:
        st.subheader("💡 Personalized Insights")
        for insight in analysis['insights']:
            st.info(f"💡 {insight}")
    
    # Goal progress tracking
    st.subheader("🏆 Goal Progress Tracking")
    
    progress_data = st.session_state.db_manager.get_progress_data(
        (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d")
    )
    
    if progress_data:
        df = pd.DataFrame(progress_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate weekly averages for trend
        df['week'] = df['date'].dt.isocalendar().week
        weekly_avg = df.groupby('week')['calories'].mean().reset_index()
        
        if len(weekly_avg) >= 2:
            trend = weekly_avg['calories'].iloc[-1] - weekly_avg['calories'].iloc[-2]
            if abs(trend) > 50:
                direction = "increasing" if trend > 0 else "decreasing"
                st.metric("📊 Weekly Calorie Trend", f"{direction.title()}", f"{trend:+.0f} cal/week")

def show_export_data():
    st.header("📤 Export & Share Your Data")
    
    tab1, tab2 = st.tabs(["📊 Export Data", "🌟 Share Progress"])
    
    with tab1:
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
    
    with tab2:
        st.subheader("🌟 Share Your Progress")
        
        # Generate shareable summary
        recent_meals = st.session_state.db_manager.get_recent_meals(7)
        if recent_meals and st.session_state.user_profile:
            summary = format_nutrition_summary(recent_meals, 7)
            
            if 'error' not in summary:
                st.write("**Your 7-Day Wellness Summary:**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Avg Daily Calories", f"{summary['daily_averages']['calories']}")
                with col2:
                    st.metric("Meals Logged", summary['total_meals'])
                with col3:
                    st.metric("Avg Protein", f"{summary['daily_averages']['protein']}g")
                
                # Generate shareable text
                share_text = f"""🍎 My 7-Day Wellness Summary:
📊 Average Daily Calories: {summary['daily_averages']['calories']}
🥩 Average Protein: {summary['daily_averages']['protein']}g
🍽️ Meals Logged: {summary['total_meals']}
💪 Keep up the healthy habits!"""
                
                st.text_area("📱 Share this summary:", share_text, height=120)
                st.info("💡 Copy the text above to share your progress on social media!")
        else:
            st.info("Start logging meals to generate a shareable summary!")
    
    # Show data summary
    st.subheader("📈 Data Overview")
    
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
