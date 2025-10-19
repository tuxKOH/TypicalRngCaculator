"""
Typical RNG Calculator
Copyright (C) 2025 tux_koh

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from flask import Flask, render_template, request, jsonify
import math
import json
import re
from typing import Dict, List, Tuple

app = Flask(__name__)

# Default sans data with fixed name consistency
DEFAULT_SANS_DATA = {
    "Little": 2, "classic": 3, "Fell": 5, "outer": 8, "horror": 25,
    "Fresh": 32, "After": 44, "Killer": 66, "Dream": 77, "RuinsDust": 12,
    "SnowdinDust": 20, "Photo Negative": 200, "Assured Prey": 500, "gencide": 900,
    "C!insanity": 3666, "Avenge": 3449, "Ink": 5000, "Error": 5000, "Fatal error": 55555,
    "Reaper": 99999, "Pesti": 3500, "DD (dustdust)": 16666, "Lethal Deal": 50000, "Hyper-dust": 99999,
    "clown": 69420, "undersanity": 500000, "Corrupted insanity": 162162, "Final insanity": 241956,
    "Superfell": 250000, "Cone": 100000, "Weakened alpha": 250000, "king mutiverse": 333333,
    "zalgo": 366666, "error404": 404040, "omnipotent": 555555, "infected": 666666,
    "fatal corruption": 666666, "virus404": 999999, "HIM (true insanity)": 1666666,
    "alpha judge": 399999, "errordust": 444444, "true dust": 500000, "Shanghaivania": 1500000,
    "lulzsec": 777777, "containment": 800000, "negative error404": 1404040, "omnithorn": 2222220,
    "DDD (dustdustdust)": 2666666, "final dust": 2999999, "butterfly404": 4040404, "error666": 6666666,
    "overkill": 16000000, "loading": 2222222, "code rainbow": 2222222, "distortion": 3666666,
    "entity0": 11111111, "anti god": 6000000, "CTI (corrupted true insanity)": 15000000,
    "roland": 15000000
}

# Default configuration lists
DEFAULT_UNOBTAINABLE_SANS = ["CTI (corrupted true insanity)", "clown", "undersanity", "roland", "anti god"]
DEFAULT_RAW_SANS = ["CTI (corrupted true insanity)", "negative error404", "anti god"]
DEFAULT_BLACKLISTED_SANS = []  # New blacklist, only hides display

def search_sans(query: str, sans_list: List[str]) -> List[Tuple[str, float]]:
    """Search sans function with fuzzy matching"""
    if not query:
        return [(sans, 0) for sans in sans_list[:10]]
    
    query = query.lower()
    results = []
    
    for sans in sans_list:
        sans_lower = sans.lower()
        
        # Calculate match score based on different criteria
        if sans_lower == query:
            score = 1.0  # Exact match
        elif sans_lower.startswith(query):
            score = 0.8  # Starts with query
        elif re.search(r'\b' + re.escape(query) + r'\b', sans_lower):
            score = 0.6  # Word boundary match
        elif query in sans_lower:
            score = 0.4  # Contains query
        else:
            # Fuzzy match with character sequence
            pattern = '.*'.join(query)
            if re.search(pattern, sans_lower):
                score = 0.2  # Fuzzy match
            else:
                score = 0.0  # No match
        
        if score > 0:
            results.append((sans, score))
    
    # Sort by score (descending) and then by name
    results.sort(key=lambda x: (-x[1], x[0]))
    return results[:15]  # Return top 15 results

class SansCalculator:
    """Main calculator class for probability calculations"""
    
    def __init__(self):
        self.sans_list = []
        self.server_luck = 1
    
    def setup(self, sans_data: Dict, raw_sans: List[str], unobtainable_sans: List[str], server_luck: int):
        """Setup calculator with sans data and configuration"""
        self.sans_list = []
        self.server_luck = server_luck
        raw_set = set(raw_sans)
        unobtainable_set = set(unobtainable_sans)
        
        # Filter out unobtainable sans and prepare sans list
        for name, chance in sans_data.items():
            if name in unobtainable_set:
                continue  # Skip unobtainable sans
                
            is_raw = name in raw_set
            self.sans_list.append({
                "name": name,
                "chance": chance,
                "is_raw": is_raw
            })
    
    def calculate_probabilities(self):
        """Calculate normalized probabilities for all sans"""
        if not self.sans_list:
            return {}, 0.0
        
        final_probs = {}
        
        # Calculate individual success probabilities
        for sans in self.sans_list:
            chance = sans["chance"]
            
            # Apply server luck to non-RAW sans
            if not sans["is_raw"]:
                chance = chance / self.server_luck
            
            # Ensure chance is at least 1
            chance = max(1, chance)
            success_prob = 1.0 / chance
            final_probs[sans["name"]] = success_prob
        
        # Normalize probabilities so they sum to 1
        total = sum(final_probs.values())
        if total > 0:
            for name in final_probs:
                final_probs[name] /= total
        
        # Calculate total weight for expected value calculations
        total_weight = sum(1.0 / sans["chance"] if sans["is_raw"] else self.server_luck / sans["chance"] for sans in self.sans_list)
        
        # Build detailed probability information
        probabilities = {}
        for sans in self.sans_list:
            final_prob = final_probs[sans["name"]]
            individual_prob = 1.0 / sans["chance"] if sans["is_raw"] else self.server_luck / sans["chance"]
            probabilities[sans["name"]] = {
                "probability": final_prob,
                "percentage": final_prob * 100,
                "individual_probability": individual_prob,
                "individual_percentage": individual_prob * 100,
                "is_raw": sans["is_raw"],
                "chance": sans["chance"]
            }
        
        return probabilities, total_weight
    
    def expected_per_event(self, target_sans=None):
        """Calculate expected number of sans per summon event"""
        probs, _ = self.calculate_probabilities()
        avg_sans_per_event = 16  # Average sans spawned per summon
        
        if target_sans:
            return avg_sans_per_event * probs[target_sans]["probability"]
        else:
            return {name: avg_sans_per_event * data["probability"] for name, data in probs.items()}
    
    def probability_in_time(self, target_sans: str, time_seconds: float):
        """Calculate probability of getting at least one target sans in specified time"""
        probs, _ = self.calculate_probabilities()
        if target_sans not in probs:
            return 0.0, 0.0
            
        # Fixed summon time: 2s + 0.04 * 16 = 2.64s
        time_per_roll = 2.64
        events_per_second = 1.0 / time_per_roll
        total_events = events_per_second * time_seconds
        expected_per_event = self.expected_per_event(target_sans)
        lambda_total = expected_per_event * total_events
        
        # Poisson distribution for probability of at least one success
        prob_at_least_one = 1 - math.exp(-lambda_total)
        
        return prob_at_least_one, lambda_total
    
    def time_for_expected_first(self, target_sans: str):
        """Calculate expected time to get first target sans"""
        expected_per_event = self.expected_per_event(target_sans)
        time_per_roll = 2.64
        events_per_second = 1.0 / time_per_roll
        
        if expected_per_event <= 0:
            return float('inf')
        
        return 1 / (expected_per_event * events_per_second)
    
    def time_for_certainty(self, target_sans: str, certainty: float = 0.99):
        """Calculate time required to reach specified certainty level"""
        expected_per_event = self.expected_per_event(target_sans)
        time_per_roll = 2.64
        events_per_second = 1.0 / time_per_roll
        
        if expected_per_event <= 0:
            return float('inf')
        
        lambda_rate = expected_per_event * events_per_second
        return -math.log(1 - certainty) / lambda_rate
    
    def probability_all_in_time(self, time_seconds: float):
        """Calculate probabilities for all sans in specified time period"""
        probs, _ = self.calculate_probabilities()
        result = {}
        
        for name in probs.keys():
            prob, expected = self.probability_in_time(name, time_seconds)
            time_first = self.time_for_expected_first(name)
            time_99 = self.time_for_certainty(name)
            result[name] = {
                "probability_percent": prob * 100,
                "expected_count": expected,
                "time_first_seconds": time_first,
                "time_99_percent_seconds": time_99,
                "base_probability": probs[name]["percentage"],
                "individual_probability": probs[name]["individual_percentage"],
                "is_raw": probs[name]["is_raw"]
            }
        
        return result

@app.route('/')
def index():
    """Home page route - serves the main calculator interface"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint for finding sans by name"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'})
            
        query = data.get('query', '')
        
        all_sans = list(DEFAULT_SANS_DATA.keys())
        results = search_sans(query, all_sans)
        
        return jsonify({
            'success': True, 
            'results': [{'name': name, 'score': score} for name, score in results]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/calculate', methods=['POST'])
def calculate():
    """Main calculation endpoint - processes calculator requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'})
        
        # Extract and validate input parameters
        server_luck = int(data.get('server_luck', 8))
        time_seconds = float(data.get('time_seconds', 3600))
        custom_sans = data.get('custom_sans', {})
        selected_sans = data.get('selected_sans', [])
        custom_raw = data.get('custom_raw', [])
        custom_unobtainable = data.get('custom_unobtainable', [])
        custom_blacklisted = data.get('custom_blacklisted', [])
        
        # Combine default sans data with custom sans
        sans_data = DEFAULT_SANS_DATA.copy()
        if isinstance(custom_sans, dict):
            sans_data.update(custom_sans)
        
        # Ensure all list inputs are properly formatted
        if not isinstance(custom_raw, list):
            custom_raw = []
        if not isinstance(custom_unobtainable, list):
            custom_unobtainable = []
        if not isinstance(custom_blacklisted, list):
            custom_blacklisted = []
        if not isinstance(selected_sans, list):
            selected_sans = []
        
        # Combine default and custom configurations
        raw_sans = DEFAULT_RAW_SANS + custom_raw
        unobtainable_sans = DEFAULT_UNOBTAINABLE_SANS + custom_unobtainable
        blacklisted_sans = DEFAULT_BLACKLISTED_SANS + custom_blacklisted
        
        # Initialize calculator and perform calculations
        calculator = SansCalculator()
        calculator.setup(sans_data, raw_sans, unobtainable_sans, server_luck)
        
        probs, total_weight = calculator.calculate_probabilities()
        all_probabilities = calculator.probability_all_in_time(time_seconds)
        
        # Calculate statistics
        time_per_roll = 2.64  # 2s + 0.04 * 16
        events_per_second = 1.0 / time_per_roll
        total_rolls = events_per_second * time_seconds
        total_sans_spawned = total_rolls * 16  # 16 sans per summon
        
        # Filter out blacklisted sans from rankings
        filtered_by_prob = [(name, data) for name, data in all_probabilities.items() if name not in blacklisted_sans]
        filtered_by_rarity = [(name, data) for name, data in all_probabilities.items() if name not in blacklisted_sans]
        
        # Sort rankings
        sorted_by_prob = sorted(filtered_by_prob, key=lambda x: x[1]['probability_percent'], reverse=True)[:20]
        sorted_by_rarity = sorted(filtered_by_rarity, key=lambda x: x[1]['base_probability'])[:20]
        
        # Prepare detailed results for selected sans
        selected_results = {}
        for sans_name in selected_sans:
            if sans_name in probs:
                prob, expected = calculator.probability_in_time(sans_name, time_seconds)
                time_first = calculator.time_for_expected_first(sans_name)
                time_99 = calculator.time_for_certainty(sans_name)
                selected_results[sans_name] = {
                    'probability_percent': prob * 100,
                    'expected_count': expected,
                    'time_first': time_first,
                    'time_99_percent': time_99,
                    'base_probability': probs[sans_name]["percentage"],
                    'individual_probability': probs[sans_name]["individual_percentage"],
                    'is_raw': probs[sans_name]['is_raw']
                }
        
        # Compile final results
        results = {
            'total_sans': len(probs),
            'total_weight': total_weight,
            'server_luck': server_luck,
            'time_seconds': time_seconds,
            'time_per_roll': time_per_roll,
            'total_rolls': total_rolls,
            'total_sans_spawned': total_sans_spawned,
            'all_probabilities': all_probabilities,
            'sorted_by_prob': sorted_by_prob,
            'sorted_by_rarity': sorted_by_rarity,
            'selected_results': selected_results,
            'blacklisted_sans': blacklisted_sans
        }
        
        return jsonify({'success': True, 'results': results})
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Calculation error: {error_details}")  # Log error for debugging
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(404)
def not_found(error):
    """404 error handler - returns JSON response"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler - returns JSON response"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
