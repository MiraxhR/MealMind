import requests
import json
from typing import Dict, Optional, List
import time
import os

class OpenFoodFactsAPI:
    def __init__(self):
        self.base_url = "https://world.openfoodfacts.org"
        self.headers = {
            'User-Agent': 'WellnessTracker/1.0 (https://github.com/wellness-tracker)'
        }
        self.cache = {} 
        
    def search_food(self, query: str, limit: int = 5) -> Optional[Dict]:
        """Search for food items using OpenFoodFacts API"""
        if not query or len(query.strip()) < 2:
            return None
            
       
        cache_key = f"search_{query.lower().strip()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
           
            search_url = f"{self.base_url}/cgi/search.pl"
            params = {
                'search_terms': query,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': limit,
                'fields': 'product_name,brands,nutriscore_grade,energy_kcal_100g,proteins_100g,carbohydrates_100g,fat_100g,fiber_100g,sugars_100g,salt_100g,ingredients_text'
            }
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('products'):
                
                for product in data['products']:
                    if self._has_nutrition_data(product):
                        nutrition_data = self._extract_nutrition_data(product)
                       
                        self.cache[cache_key] = nutrition_data
                        return nutrition_data
            
            return None
            
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse API response: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in food search: {e}")
            return None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Get product information by barcode"""
        if not barcode or not barcode.isdigit():
            return None
            
        cache_key = f"barcode_{barcode}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            product_url = f"{self.base_url}/api/v0/product/{barcode}.json"
            response = requests.get(product_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 1 and data.get('product'):
                product = data['product']
                if self._has_nutrition_data(product):
                    nutrition_data = self._extract_nutrition_data(product)
                    self.cache[cache_key] = nutrition_data
                    return nutrition_data
            
            return None
            
        except requests.RequestException as e:
            print(f"Barcode API request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in barcode lookup: {e}")
            return None
    
    def _has_nutrition_data(self, product: Dict) -> bool:
        """Check if product has essential nutrition data"""
        required_fields = ['energy_kcal_100g']
        return any(product.get(field) is not None for field in required_fields)
    
    def _extract_nutrition_data(self, product: Dict) -> Dict:
        """Extract and normalize nutrition data from product"""
        try:
            nutrition_data = {
                'product_name': product.get('product_name', 'Unknown Product'),
                'brands': product.get('brands', ''),
                'nutriscore_grade': product.get('nutriscore_grade', '').upper(),
                'energy_kcal_100g': float(product.get('energy_kcal_100g', 0)),
                'proteins_100g': float(product.get('proteins_100g', 0)),
                'carbohydrates_100g': float(product.get('carbohydrates_100g', 0)),
                'fat_100g': float(product.get('fat_100g', 0)),
                'fiber_100g': float(product.get('fiber_100g', 0)),
                'sugars_100g': float(product.get('sugars_100g', 0)),
                'salt_100g': float(product.get('salt_100g', 0)),
                'ingredients_text': product.get('ingredients_text', '')
            }
            
            return nutrition_data
            
        except (ValueError, TypeError) as e:
            print(f"Error processing nutrition data: {e}")
            
            return {
                'product_name': product.get('product_name', 'Unknown Product'),
                'brands': product.get('brands', ''),
                'nutriscore_grade': '',
                'energy_kcal_100g': 0,
                'proteins_100g': 0,
                'carbohydrates_100g': 0,
                'fat_100g': 0,
                'fiber_100g': 0,
                'sugars_100g': 0,
                'salt_100g': 0,
                'ingredients_text': ''
            }
    
    def get_nutrition_suggestions(self, dietary_restrictions: List[str] = None) -> List[Dict]:
        """Get nutrition suggestions based on dietary restrictions"""
        suggestions = []
        
        
        healthy_foods = [
            'quinoa', 'salmon', 'avocado', 'spinach', 'blueberries',
            'sweet potato', 'almonds', 'greek yogurt', 'broccoli', 'chicken breast'
        ]
        
       
        if dietary_restrictions:
            restrictions_lower = [r.lower() for r in dietary_restrictions]
            
            if 'vegetarian' in restrictions_lower or 'vegan' in restrictions_lower:
                healthy_foods = [food for food in healthy_foods 
                               if food not in ['salmon', 'chicken breast', 'greek yogurt']]
            
            if 'vegan' in restrictions_lower:
                healthy_foods = [food for food in healthy_foods 
                               if food not in ['greek yogurt']]
        
       
        for food in healthy_foods[:5]:  
            nutrition_data = self.search_food(food)
            if nutrition_data:
                suggestions.append(nutrition_data)
            
            
            time.sleep(0.1)
        
        return suggestions
    
    def analyze_ingredient_quality(self, ingredients_text: str) -> Dict:
        """Analyze ingredient quality and provide insights"""
        if not ingredients_text:
            return {'quality_score': 0, 'insights': ['No ingredient information available']}
        
        ingredients = ingredients_text.lower()
        insights = []
        quality_score = 50  
        
        
        positive_keywords = [
            'organic', 'natural', 'whole grain', 'fresh', 'pure',
            'virgin', 'unrefined', 'raw', 'free-range'
        ]
        
        
        negative_keywords = [
            'artificial', 'preservatives', 'high fructose corn syrup',
            'trans fat', 'hydrogenated', 'monosodium glutamate',
            'artificial colors', 'artificial flavors'
        ]
        
        
        for keyword in positive_keywords:
            if keyword in ingredients:
                quality_score += 10
                insights.append(f"Contains {keyword} - good quality indicator")
        
        
        for keyword in negative_keywords:
            if keyword in ingredients:
                quality_score -= 15
                insights.append(f"Contains {keyword} - consider alternatives")
        
        
        ingredient_count = len(ingredients.split(','))
        if ingredient_count <= 5:
            quality_score += 5
            insights.append("Simple ingredient list - usually a good sign")
        elif ingredient_count > 15:
            quality_score -= 5
            insights.append("Long ingredient list - check for unnecessary additives")
        
        
        quality_score = max(0, min(100, quality_score))
        
        if not insights:
            insights.append("Standard ingredient profile - no specific concerns identified")
        
        return {
            'quality_score': quality_score,
            'insights': insights,
            'ingredient_count': ingredient_count
        }
    
    def clear_cache(self):
        """Clear the API cache"""
        self.cache.clear()
