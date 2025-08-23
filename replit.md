# AI-Powered Meal Planner & Wellness Tracker

## Overview

This is a comprehensive wellness tracking application built with Streamlit that provides AI-powered meal recommendations, nutrition tracking, and progress monitoring. The system combines user profile management, intelligent meal planning, food logging capabilities, and data visualization to help users achieve their health and fitness goals. The application integrates with external nutrition APIs and uses machine learning algorithms for personalized meal recommendations based on user preferences, dietary restrictions, and health objectives.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web-based user interface
- **Layout**: Multi-page application with sidebar navigation
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts and data visualization
- **State Management**: Streamlit session state for maintaining user data across page interactions

### Backend Architecture
- **Core Components**: Modular design with separate classes for database management, meal recommendations, and nutrition API integration
- **Data Processing**: Pandas for data manipulation and analysis
- **Machine Learning**: Scikit-learn with TF-IDF vectorization and cosine similarity for meal recommendation algorithms
- **Nutrition Calculations**: Custom utility functions for BMR (Basal Metabolic Rate) and daily calorie calculations using Mifflin-St Jeor equation

### Data Storage
- **Database**: SQLite for local data persistence
- **Schema Design**: 
  - User profiles with demographics, goals, and dietary restrictions
  - Meal logs with nutritional information and timestamps
- **Data Export**: CSV export functionality for progress tracking

### Meal Recommendation System
- **Algorithm**: Content-based filtering using TF-IDF and cosine similarity
- **Database**: Structured meal database with nutritional information, dietary tags, and health benefits
- **Personalization**: Recommendations based on user preferences, allergies, and fitness goals

### Authentication and User Management
- **Profile System**: Single-user profile management with persistent storage
- **Session Handling**: Streamlit session state for maintaining user context

## External Dependencies

### Third-Party APIs
- **OpenFoodFacts API**: External nutrition database for food item lookup and nutritional information retrieval
- **Rate Limiting**: Built-in caching mechanism to optimize API calls and improve performance

### Python Libraries
- **Core Framework**: Streamlit for web application development
- **Data Science**: Pandas, NumPy for data manipulation and numerical computations
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts
- **Machine Learning**: Scikit-learn for recommendation algorithms
- **Database**: SQLite3 for local database operations
- **HTTP Requests**: Requests library for external API communication

### External Services
- **Nutrition Data**: Integration with OpenFoodFacts for comprehensive food database access
- **Export Capabilities**: CSV file generation for data portability and external analysis

### Development Dependencies
- **Environment Management**: Local file system for database storage and configuration
- **Error Handling**: Comprehensive exception handling for API failures and data validation