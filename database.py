import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "wellness_tracker.db"):
        self.db_path = db_path
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                weight REAL NOT NULL,
                height INTEGER NOT NULL,
                gender TEXT NOT NULL,
                activity_level TEXT NOT NULL,
                goal TEXT NOT NULL,
                dietary_restrictions TEXT,
                allergies TEXT,
                daily_calories REAL,
                bmr REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_name TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                logged_at TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 10),
                notes TEXT,
                logged_at TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user_profile(self, profile_data: Dict) -> bool:
        """Save or update user profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            
            cursor.execute("SELECT id FROM user_profile LIMIT 1")
            existing = cursor.fetchone()
            
            dietary_restrictions_json = json.dumps(profile_data.get('dietary_restrictions', []))
            
            if existing:
                
                cursor.execute('''
                    UPDATE user_profile SET
                    name = ?, age = ?, weight = ?, height = ?, gender = ?,
                    activity_level = ?, goal = ?, dietary_restrictions = ?,
                    allergies = ?, daily_calories = ?, bmr = ?,
                    updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    profile_data['name'], profile_data['age'], profile_data['weight'],
                    profile_data['height'], profile_data['gender'], profile_data['activity_level'],
                    profile_data['goal'], dietary_restrictions_json, profile_data['allergies'],
                    profile_data['daily_calories'], profile_data['bmr'], existing[0]
                ))
            else:
               
                cursor.execute('''
                    INSERT INTO user_profile 
                    (name, age, weight, height, gender, activity_level, goal, 
                     dietary_restrictions, allergies, daily_calories, bmr)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    profile_data['name'], profile_data['age'], profile_data['weight'],
                    profile_data['height'], profile_data['gender'], profile_data['activity_level'],
                    profile_data['goal'], dietary_restrictions_json, profile_data['allergies'],
                    profile_data['daily_calories'], profile_data['bmr']
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get user profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, age, weight, height, gender, activity_level, goal,
                       dietary_restrictions, allergies, daily_calories, bmr
                FROM user_profile ORDER BY updated_at DESC LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'name': row[0],
                    'age': row[1],
                    'weight': row[2],
                    'height': row[3],
                    'gender': row[4],
                    'activity_level': row[5],
                    'goal': row[6],
                    'dietary_restrictions': json.loads(row[7]) if row[7] else [],
                    'allergies': row[8],
                    'daily_calories': row[9],
                    'bmr': row[10]
                }
            return None
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def log_meal(self, meal_data: Dict) -> bool:
        """Log a meal entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO meal_logs (meal_name, meal_type, calories, protein, carbs, fat, date, time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meal_data['meal_name'], meal_data['meal_type'], meal_data['calories'],
                meal_data['protein'], meal_data['carbs'], meal_data['fat'],
                meal_data['date'], meal_data['time']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging meal: {e}")
            return False
    
    def log_water(self, amount: float, logged_at: str) -> bool:
        """Log water intake"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO water_logs (amount, logged_at)
                VALUES (?, ?)
            ''', (amount, logged_at))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging water: {e}")
            return False
    
    def log_mood(self, rating: int, notes: str, logged_at: str) -> bool:
        """Log mood entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO mood_logs (rating, notes, logged_at)
                VALUES (?, ?, ?)
            ''', (rating, notes, logged_at))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging mood: {e}")
            return False
    
    def get_recent_meals(self, days: int = 7) -> List[Dict]:
        """Get recent meal logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT meal_name, meal_type, calories, protein, carbs, fat, date, time
                FROM meal_logs 
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC, time DESC
            '''.format(days))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'meal_name': row[0],
                    'meal_type': row[1],
                    'calories': row[2],
                    'protein': row[3],
                    'carbs': row[4],
                    'fat': row[5],
                    'date': row[6],
                    'time': row[7]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting recent meals: {e}")
            return []
    
    def get_daily_nutrition_totals(self, date: str) -> Optional[Dict]:
        """Get nutrition totals for a specific date"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT SUM(calories) as total_calories, 
                       SUM(protein) as total_protein,
                       SUM(carbs) as total_carbs, 
                       SUM(fat) as total_fat
                FROM meal_logs 
                WHERE date = ?
            ''', (date,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] is not None:
                return {
                    'total_calories': row[0] or 0,
                    'total_protein': row[1] or 0,
                    'total_carbs': row[2] or 0,
                    'total_fat': row[3] or 0
                }
            return None
            
        except Exception as e:
            print(f"Error getting daily nutrition totals: {e}")
            return None
    
    def get_progress_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Get progress data for date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT meal_name, meal_type, calories, protein, carbs, fat, date, time
                FROM meal_logs 
                WHERE date BETWEEN ? AND ?
                ORDER BY date, time
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'meal_name': row[0],
                    'meal_type': row[1],
                    'calories': row[2],
                    'protein': row[3],
                    'carbs': row[4],
                    'fat': row[5],
                    'date': row[6],
                    'time': row[7]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting progress data: {e}")
            return []
    
    def get_water_logs(self, start_date: str, end_date: str) -> List[Dict]:
        """Get water intake logs for date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT amount, logged_at
                FROM water_logs 
                WHERE date(logged_at) BETWEEN ? AND ?
                ORDER BY logged_at
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'amount': row[0],
                    'date': row[1]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting water logs: {e}")
            return []
    
    def get_mood_logs(self, start_date: str, end_date: str) -> List[Dict]:
        """Get mood logs for date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT rating, notes, logged_at
                FROM mood_logs 
                WHERE date(logged_at) BETWEEN ? AND ?
                ORDER BY logged_at
            ''', (start_date, end_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'rating': row[0],
                    'notes': row[1],
                    'date': row[2]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting mood logs: {e}")
            return []
