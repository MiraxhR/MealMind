import random
from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MealRecommender:
    def __init__(self):
        # Sample meal database - in a real application, this would be more extensive
        self.meals_database = {
            'Breakfast': [
                {
                    'name': 'Greek Yogurt Parfait',
                    'description': 'Greek yogurt layered with berries and granola',
                    'ingredients': ['Greek yogurt', 'mixed berries', 'granola', 'honey'],
                    'calories': 280,
                    'protein': 18,
                    'carbs': 35,
                    'fat': 8,
                    'preparation_time': 5,
                    'dietary_tags': ['vegetarian', 'gluten-free'],
                    'health_benefits': ['probiotics', 'antioxidants', 'fiber']
                },
                {
                    'name': 'Avocado Toast',
                    'description': 'Whole grain toast topped with mashed avocado and seasonings',
                    'ingredients': ['whole grain bread', 'avocado', 'lime juice', 'salt', 'pepper'],
                    'calories': 320,
                    'protein': 8,
                    'carbs': 25,
                    'fat': 22,
                    'preparation_time': 8,
                    'dietary_tags': ['vegan', 'vegetarian'],
                    'health_benefits': ['healthy fats', 'fiber', 'potassium']
                },
                {
                    'name': 'Protein Smoothie',
                    'description': 'Blended smoothie with protein powder, fruits, and spinach',
                    'ingredients': ['protein powder', 'banana', 'spinach', 'almond milk', 'berries'],
                    'calories': 250,
                    'protein': 25,
                    'carbs': 20,
                    'fat': 5,
                    'preparation_time': 5,
                    'dietary_tags': ['dairy-free', 'vegetarian'],
                    'health_benefits': ['high protein', 'vitamins', 'antioxidants']
                },
                {
                    'name': 'Oatmeal Bowl',
                    'description': 'Steel-cut oats with fruits, nuts, and cinnamon',
                    'ingredients': ['steel-cut oats', 'banana', 'walnuts', 'cinnamon', 'maple syrup'],
                    'calories': 350,
                    'protein': 12,
                    'carbs': 45,
                    'fat': 14,
                    'preparation_time': 15,
                    'dietary_tags': ['vegan', 'vegetarian', 'gluten-free'],
                    'health_benefits': ['fiber', 'complex carbs', 'omega-3']
                }
            ],
            'Lunch': [
                {
                    'name': 'Quinoa Buddha Bowl',
                    'description': 'Colorful bowl with quinoa, roasted vegetables, and tahini dressing',
                    'ingredients': ['quinoa', 'sweet potato', 'chickpeas', 'kale', 'tahini', 'lemon'],
                    'calories': 420,
                    'protein': 16,
                    'carbs': 55,
                    'fat': 16,
                    'preparation_time': 25,
                    'dietary_tags': ['vegan', 'vegetarian', 'gluten-free'],
                    'health_benefits': ['complete protein', 'fiber', 'antioxidants']
                },
                {
                    'name': 'Grilled Chicken Salad',
                    'description': 'Mixed greens with grilled chicken, vegetables, and vinaigrette',
                    'ingredients': ['chicken breast', 'mixed greens', 'cherry tomatoes', 'cucumber', 'olive oil'],
                    'calories': 380,
                    'protein': 35,
                    'carbs': 12,
                    'fat': 22,
                    'preparation_time': 20,
                    'dietary_tags': ['gluten-free', 'dairy-free'],
                    'health_benefits': ['lean protein', 'vitamins', 'healthy fats']
                },
                {
                    'name': 'Vegetable Stir-fry',
                    'description': 'Mixed vegetables stir-fried with tofu and brown rice',
                    'ingredients': ['tofu', 'broccoli', 'bell peppers', 'brown rice', 'soy sauce', 'ginger'],
                    'calories': 340,
                    'protein': 18,
                    'carbs': 42,
                    'fat': 12,
                    'preparation_time': 18,
                    'dietary_tags': ['vegan', 'vegetarian'],
                    'health_benefits': ['plant protein', 'fiber', 'vitamins']
                },
                {
                    'name': 'Turkey Wrap',
                    'description': 'Whole wheat wrap with turkey, vegetables, and hummus',
                    'ingredients': ['turkey breast', 'whole wheat tortilla', 'hummus', 'lettuce', 'tomatoes'],
                    'calories': 390,
                    'protein': 28,
                    'carbs': 35,
                    'fat': 15,
                    'preparation_time': 10,
                    'dietary_tags': ['dairy-free'],
                    'health_benefits': ['lean protein', 'fiber', 'B vitamins']
                }
            ],
            'Dinner': [
                {
                    'name': 'Baked Salmon',
                    'description': 'Herb-crusted salmon with roasted vegetables and quinoa',
                    'ingredients': ['salmon fillet', 'asparagus', 'quinoa', 'herbs', 'lemon', 'olive oil'],
                    'calories': 450,
                    'protein': 35,
                    'carbs': 28,
                    'fat': 22,
                    'preparation_time': 30,
                    'dietary_tags': ['gluten-free', 'dairy-free'],
                    'health_benefits': ['omega-3', 'complete protein', 'vitamins']
                },
                {
                    'name': 'Vegetarian Chili',
                    'description': 'Hearty chili with beans, vegetables, and spices',
                    'ingredients': ['black beans', 'kidney beans', 'tomatoes', 'onions', 'bell peppers', 'spices'],
                    'calories': 320,
                    'protein': 18,
                    'carbs': 52,
                    'fat': 4,
                    'preparation_time': 35,
                    'dietary_tags': ['vegan', 'vegetarian', 'gluten-free'],
                    'health_benefits': ['fiber', 'plant protein', 'antioxidants']
                },
                {
                    'name': 'Lean Beef Stir-fry',
                    'description': 'Lean beef strips with vegetables over brown rice',
                    'ingredients': ['lean beef', 'broccoli', 'snap peas', 'brown rice', 'garlic', 'soy sauce'],
                    'calories': 410,
                    'protein': 30,
                    'carbs': 38,
                    'fat': 14,
                    'preparation_time': 22,
                    'dietary_tags': ['dairy-free'],
                    'health_benefits': ['iron', 'protein', 'B vitamins']
                },
                {
                    'name': 'Stuffed Bell Peppers',
                    'description': 'Bell peppers stuffed with turkey, rice, and vegetables',
                    'ingredients': ['ground turkey', 'bell peppers', 'brown rice', 'onions', 'tomatoes'],
                    'calories': 380,
                    'protein': 26,
                    'carbs': 32,
                    'fat': 16,
                    'preparation_time': 40,
                    'dietary_tags': ['gluten-free', 'dairy-free'],
                    'health_benefits': ['lean protein', 'vitamins', 'fiber']
                }
            ],
            'Snack': [
                {
                    'name': 'Apple with Almond Butter',
                    'description': 'Sliced apple with natural almond butter',
                    'ingredients': ['apple', 'almond butter'],
                    'calories': 190,
                    'protein': 6,
                    'carbs': 20,
                    'fat': 11,
                    'preparation_time': 2,
                    'dietary_tags': ['vegan', 'vegetarian', 'gluten-free'],
                    'health_benefits': ['fiber', 'healthy fats', 'vitamin C']
                },
                {
                    'name': 'Protein Energy Balls',
                    'description': 'No-bake energy balls with oats, dates, and protein powder',
                    'ingredients': ['rolled oats', 'dates', 'protein powder', 'chia seeds', 'coconut'],
                    'calories': 150,
                    'protein': 8,
                    'carbs': 18,
                    'fat': 5,
                    'preparation_time': 10,
                    'dietary_tags': ['vegetarian', 'gluten-free'],
                    'health_benefits': ['protein', 'fiber', 'natural sugars']
                },
                {
                    'name': 'Mixed Nuts',
                    'description': 'Portion-controlled mix of raw almonds, walnuts, and cashews',
                    'ingredients': ['almonds', 'walnuts', 'cashews'],
                    'calories': 160,
                    'protein': 6,
                    'carbs': 6,
                    'fat': 14,
                    'preparation_time': 1,
                    'dietary_tags': ['vegan', 'vegetarian', 'gluten-free', 'keto'],
                    'health_benefits': ['healthy fats', 'protein', 'vitamin E']
                },
                {
                    'name': 'Veggie Hummus Plate',
                    'description': 'Fresh vegetables with homemade hummus',
                    'ingredients': ['carrots', 'cucumbers', 'bell peppers', 'hummus'],
                    'calories': 140,
                    'protein': 6,
                    'carbs': 16,
                    'fat': 6,
                    'preparation_time': 5,
                    'dietary_tags': ['vegan', 'vegetarian', 'gluten-free'],
                    'health_benefits': ['fiber', 'vitamins', 'plant protein']
                }
            ]
        }
    
    def get_recommendations(self, user_profile: Dict, meal_type: str, num_recommendations: int = 3) -> List[Dict]:
        """Generate AI-powered meal recommendations based on user profile"""
        try:
            available_meals = self.meals_database.get(meal_type, [])
            
            if not available_meals:
                return []
            
            # Filter meals based on dietary restrictions
            filtered_meals = self._filter_by_dietary_restrictions(
                available_meals, 
                user_profile.get('dietary_restrictions', [])
            )
            
            if not filtered_meals:
                # If no meals match dietary restrictions, use all available meals
                filtered_meals = available_meals
            
            # Score meals based on user profile
            scored_meals = self._score_meals(filtered_meals, user_profile, meal_type)
            
            # Sort by score and return top recommendations
            scored_meals.sort(key=lambda x: x['ai_score'], reverse=True)
            
            return scored_meals[:num_recommendations]
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def _filter_by_dietary_restrictions(self, meals: List[Dict], restrictions: List[str]) -> List[Dict]:
        """Filter meals based on dietary restrictions"""
        if not restrictions:
            return meals
        
        filtered_meals = []
        
        for meal in meals:
            meal_tags = [tag.lower() for tag in meal.get('dietary_tags', [])]
            restriction_tags = [restriction.lower() for restriction in restrictions]
            
            # Check if meal satisfies all dietary restrictions
            satisfies_restrictions = True
            for restriction in restriction_tags:
                if restriction not in meal_tags:
                    satisfies_restrictions = False
                    break
            
            if satisfies_restrictions:
                filtered_meals.append(meal)
        
        return filtered_meals
    
    def _score_meals(self, meals: List[Dict], user_profile: Dict, meal_type: str) -> List[Dict]:
        """Score meals based on user profile and goals"""
        scored_meals = []
        
        # Calculate target calories per meal based on daily needs
        daily_calories = user_profile.get('daily_calories', 2000)
        meal_calorie_targets = {
            'Breakfast': daily_calories * 0.25,
            'Lunch': daily_calories * 0.35,
            'Dinner': daily_calories * 0.35,
            'Snack': daily_calories * 0.05
        }
        
        target_calories = meal_calorie_targets.get(meal_type, daily_calories * 0.25)
        
        for meal in meals:
            score = 0
            meal_copy = meal.copy()
            
            # Calorie alignment score (closer to target is better)
            calorie_diff = abs(meal['calories'] - target_calories)
            calorie_score = max(0, 100 - (calorie_diff / target_calories * 100))
            score += calorie_score * 0.3
            
            # Goal-based scoring
            goal = user_profile.get('goal', '').lower()
            if 'lose weight' in goal:
                # Prefer lower calorie, higher protein meals
                if meal['calories'] < target_calories:
                    score += 20
                if meal.get('protein', 0) > 15:
                    score += 15
            elif 'gain weight' in goal or 'build muscle' in goal:
                # Prefer higher calorie, higher protein meals
                if meal['calories'] > target_calories * 0.9:
                    score += 20
                if meal.get('protein', 0) > 20:
                    score += 20
            elif 'maintain' in goal:
                # Prefer balanced meals
                protein_ratio = meal.get('protein', 0) * 4 / meal['calories']
                if 0.15 <= protein_ratio <= 0.35:  # 15-35% protein
                    score += 15
            
            # Health benefits score
            health_benefits = meal.get('health_benefits', [])
            score += len(health_benefits) * 2
            
            # Preparation time score (shorter is generally better)
            prep_time = meal.get('preparation_time', 30)
            if prep_time <= 10:
                score += 10
            elif prep_time <= 20:
                score += 5
            
            # Variety score (randomness to avoid repetition)
            score += random.randint(0, 15)
            
            # Macro balance score
            total_macros = meal.get('protein', 0) + meal.get('carbs', 0) + meal.get('fat', 0)
            if total_macros > 0:
                protein_ratio = meal.get('protein', 0) / total_macros
                carb_ratio = meal.get('carbs', 0) / total_macros
                fat_ratio = meal.get('fat', 0) / total_macros
                
                # Prefer balanced macros
                if 0.15 <= protein_ratio <= 0.4 and 0.2 <= fat_ratio <= 0.4:
                    score += 10
            
            meal_copy['ai_score'] = score
            scored_meals.append(meal_copy)
        
        return scored_meals
    
    def get_quick_meal_ideas(self, dietary_restrictions: List[str] = None) -> List[Dict]:
        """Get quick meal ideas for last-minute decisions"""
        quick_meals = []
        
        for meal_type, meals in self.meals_database.items():
            for meal in meals:
                if meal.get('preparation_time', 30) <= 15:  # 15 minutes or less
                    quick_meal = meal.copy()
                    quick_meal['meal_type'] = meal_type
                    
                    # Filter by dietary restrictions if provided
                    if dietary_restrictions:
                        meal_tags = [tag.lower() for tag in meal.get('dietary_tags', [])]
                        restriction_tags = [r.lower() for r in dietary_restrictions]
                        
                        if not all(restriction in meal_tags for restriction in restriction_tags):
                            continue
                    
                    quick_meals.append(quick_meal)
        
        # Sort by preparation time
        quick_meals.sort(key=lambda x: x.get('preparation_time', 30))
        
        return quick_meals[:6]  # Return top 6 quick meals
    
    def analyze_nutrition_patterns(self, meal_logs: List[Dict]) -> Dict:
        """Analyze user's nutrition patterns and provide insights"""
        if not meal_logs:
            return {'error': 'No meal data available for analysis'}
        
        # Calculate averages
        total_meals = len(meal_logs)
        avg_calories = sum(meal.get('calories', 0) for meal in meal_logs) / total_meals
        avg_protein = sum(meal.get('protein', 0) for meal in meal_logs) / total_meals
        avg_carbs = sum(meal.get('carbs', 0) for meal in meal_logs) / total_meals
        avg_fat = sum(meal.get('fat', 0) for meal in meal_logs) / total_meals
        
        # Meal type distribution
        meal_types = {}
        for meal in meal_logs:
            meal_type = meal.get('meal_type', 'Unknown')
            meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
        
        # Generate insights
        insights = []
        
        if avg_protein < 15:
            insights.append("Consider increasing protein intake for better muscle maintenance and satiety.")
        
        if avg_calories < 1200:
            insights.append("Your average calorie intake seems low. Consider adding healthy snacks.")
        elif avg_calories > 2500:
            insights.append("Your calorie intake is quite high. Consider portion control if weight loss is your goal.")
        
        if meal_types.get('Breakfast', 0) < total_meals * 0.2:
            insights.append("Don't skip breakfast! It helps maintain steady energy levels throughout the day.")
        
        return {
            'avg_calories': round(avg_calories, 1),
            'avg_protein': round(avg_protein, 1),
            'avg_carbs': round(avg_carbs, 1),
            'avg_fat': round(avg_fat, 1),
            'meal_distribution': meal_types,
            'insights': insights,
            'total_meals_analyzed': total_meals
        }
