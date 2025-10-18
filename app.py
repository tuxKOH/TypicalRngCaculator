from flask import Flask, render_template, request, jsonify
import math
import json
import re
from typing import Dict, List, Tuple

app = Flask(__name__)

# Default sans data
DEFAULT_SANS_DATA = {
    "Little": 2, "classic": 3, "Fell": 5, "outer": 8, "horror": 25,
    "Fresh": 32, "After": 44, "Killer": 66, "Dream": 77, "RuinsDust": 12,
    "SnowdinDust": 20, "Photo Negative": 200, "Assured Prey": 500, "gencide": 900,
    "C!insanity": 3666, "Avenge": 3449, "Ink": 5000, "Error": 5000, "Fatal error": 55555,
    "Reaper": 99999, "Pesti": 3500, "DD": 16666, "Lethal Deal": 50000, "Hyper-dust": 99999,
    "clown": 69420, "undersanity": 500000, "Corrupted insanity": 162162, "Final insanity": 241956,
    "Superfell": 250000, "Cone": 100000, "Weakened alpha": 250000, "king mutiverse": 333333,
    "zalgo": 366666, "error404": 404040, "omnipotent": 555555, "infected": 666666,
    "fatal corruption": 666666, "virus404": 999999, "HIM (true insanity)": 1666666,
    "alpha judge": 399999, "errordust": 444444, "true dust": 500000, "Shanghaivania": 1500000,
    "lulzsec": 777777, "containment": 800000, "negative error404": 1404040, "omnithorn": 2222220,
    "dustdustdust": 2666666, "final dust": 2999999, "butterfly404": 4040404, "error666": 6666666,
    "overkill": 16000000, "loading": 2222222, "code rainbow": 2222222, "distortion": 3666666,
    "entity0": 11111111, "anti god": 6000000, "CTI (corrupted true insanity)": 66666666,
    "roland": 15000000
}

DEFAULT_RAW_SANS = ["CTI (corrupted true insanity)", "error666", "negative error404", "anti god"]
DEFAULT_LIMITED_SANS = ["CTI (corrupted true insanity)", "antigod", "clown", "undersanity", "roland"]

def search_sans(query: str, sans_list: List[str]) -> List[Tuple[str, float]]:
    """Search sans with matching score"""
    if not query:
        return [(sans, 0) for sans in sans_list[:10]]
    
    query = query.lower()
    results = []
    
    for sans in sans_list:
        sans_lower = sans.lower()
        
        # Exact match
        if sans_lower == query:
            score = 1.0
        # Starts with query
        elif sans_lower.startswith(query):
            score = 0.8
        # Contains query as whole word
        elif re.search(r'\b' + re.escape(query) + r'\b', sans_lower):
            score = 0.6
        # Contains query as substring
        elif query in sans_lower:
            score = 0.4
        # Fuzzy match (all characters in order)
        else:
            pattern = '.*'.join(query)
            if re.search(pattern, sans_lower):
                score = 0.2
            else:
                score = 0.0
        
        if score > 0:
            results.append((sans, score))
    
    # Sort by score (descending), then by name
    results.sort(key=lambda x: (-x[1], x[0]))
    return results[:15]

class SansCalculator:
    def __init__(self):
        self.sans_list = []
    
    def setup(self, sans_data: Dict, raw_sans: List[str], limited_sans: List[str], 
              include_limited: List[str], server_luck: int):
        """Setup calculator parameters"""
        self.sans_list = []
        self.server_luck = server_luck
        raw_set = set(raw_sans)
        limited_set = set(limited_sans)
        
        print(f"=== DEBUG SETUP START ===")
        print(f"Raw sans received: {raw_sans}")
        print(f"Raw set: {raw_set}")
        print(f"Limited sans to include: {include_limited}")
        print(f"Server luck: {server_luck}")
        
        for name, chance in sans_data.items():
            # Check if this sans should be included based on limited settings
            if name in limited_set and name not in include_limited:
                print(f"Excluding limited sans: {name}")
                continue
                
            is_raw = name in raw_set
            if is_raw:
                print(f"✓ {name} is RAW (chance: {chance}, effective chance: {chance})")
            else:
                print(f"  {name} is NORMAL (chance: {chance}, effective chance: {chance/server_luck})")
                
            self.sans_list.append({
                "name": name,
                "chance": chance,
                "is_raw": is_raw
            })
        
        print(f"Total sans in calculation: {len(self.sans_list)}")
        raw_count = sum(1 for sans in self.sans_list if sans["is_raw"])
        print(f"Raw sans count: {raw_count}")
        print(f"=== DEBUG SETUP END ====")
    
    def calculate_probabilities(self) -> Tuple[Dict, float]:
        """Calculate probabilities using the correct RNG logic"""
        if not self.sans_list:
            return {}, 0.0
        
        N = len(self.sans_list)  # Number of sans types
        
        # Calculate individual success probabilities for each sans
        individual_success_probs = {}
        for sans in self.sans_list:
            if sans["is_raw"]:
                # Raw sans: probability = 1 / chance
                individual_success_probs[sans["name"]] = 1.0 / sans["chance"]
            else:
                # Normal sans: probability = server_luck / chance
                individual_success_probs[sans["name"]] = self.server_luck / sans["chance"]
        
        print(f"=== DEBUG PROBABILITIES START ===")
        print(f"Individual success probabilities: {individual_success_probs}")
        
        # Calculate the probability that a particular sans is selected AND succeeds
        select_and_succeed_probs = {}
        for sans_name, success_prob in individual_success_probs.items():
            # Probability of selecting this sans AND it succeeding
            select_and_succeed_probs[sans_name] = (1.0 / N) * success_prob
        
        # Total probability of any sans succeeding in one iteration
        total_success_prob = sum(select_and_succeed_probs.values())
        
        print(f"Total success probability: {total_success_prob}")
        
        # If total success probability is 0, all probabilities are 0
        if total_success_prob == 0:
            final_probs = {name: 0.0 for name in individual_success_probs.keys()}
        else:
            # The final probability for each sans is proportional to its select_and_succeed probability
            final_probs = {}
            for sans_name, prob in select_and_succeed_probs.items():
                final_probs[sans_name] = prob / total_success_prob
        
        # Calculate total weight for display purposes
        total_weight = sum(individual_success_probs.values())
        
        # Format the results
        probabilities = {}
        for sans in self.sans_list:
            final_prob = final_probs[sans["name"]]
            individual_prob = individual_success_probs[sans["name"]]
            probabilities[sans["name"]] = {
                "probability": final_prob,
                "percentage": final_prob * 100,
                "individual_probability": individual_prob,
                "individual_percentage": individual_prob * 100,
                "is_raw": sans["is_raw"],
                "chance": sans["chance"]
            }
        
        print(f"Final probabilities: {final_probs}")
        print(f"=== DEBUG PROBABILITIES END ====")
        return probabilities, total_weight
    
    def expected_per_event(self, target_sans: str = None) -> Dict:
        """Expected gains per event"""
        probs, _ = self.calculate_probabilities()
        avg_sans_per_event = 16
        
        if target_sans:
            return avg_sans_per_event * probs[target_sans]["probability"]
        else:
            return {name: avg_sans_per_event * data["probability"] for name, data in probs.items()}
    
    def probability_in_time(self, target_sans: str, time_seconds: float) -> Tuple[float, float]:
        """Probability within specific time"""
        probs, _ = self.calculate_probabilities()
        if target_sans not in probs:
            return 0.0, 0.0
            
        events_per_second = 0.5  # Every 2 seconds
        total_events = events_per_second * time_seconds
        expected_per_event = self.expected_per_event(target_sans)
        lambda_total = expected_per_event * total_events
        prob_at_least_one = 1 - math.exp(-lambda_total)
        
        return prob_at_least_one, lambda_total
    
    def time_for_expected_first(self, target_sans: str) -> float:
        """Expected time to get first one"""
        expected_per_event = self.expected_per_event(target_sans)
        events_per_second = 0.5
        
        if expected_per_event <= 0:
            return float('inf')
        
        return 1 / (expected_per_event * events_per_second)
    
    def time_for_certainty(self, target_sans: str, certainty: float = 0.99) -> float:
        """Time to reach certain probability (default 99%)"""
        expected_per_event = self.expected_per_event(target_sans)
        events_per_second = 0.5
        
        if expected_per_event <= 0:
            return float('inf')
        
        lambda_rate = expected_per_event * events_per_second
        return -math.log(1 - certainty) / lambda_rate
    
    def probability_all_in_time(self, time_seconds: float) -> Dict:
        """Probability for all sans in specific time"""
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
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
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
    try:
        data = request.json
        server_luck = int(data.get('server_luck', 8))
        time_seconds = float(data.get('time_seconds', 3600))
        include_limited = data.get('include_limited', [])
        custom_sans = data.get('custom_sans', {})
        selected_sans = data.get('selected_sans', [])
        custom_raw = data.get('custom_raw', [])
        
        print(f"=== DEBUG REQUEST START ===")
        print(f"Received custom_raw: {custom_raw}")
        print(f"Type of custom_raw: {type(custom_raw)}")
        print(f"Received include_limited: {include_limited}")
        print(f"Received selected_sans: {selected_sans}")
        print(f"Server luck: {server_luck}")
        print(f"Time seconds: {time_seconds}")
        
        # Merge default and custom sans data
        sans_data = DEFAULT_SANS_DATA.copy()
        sans_data.update(custom_sans)
        
        # Process raw sans - use ONLY custom raw sans (override defaults)
        # 确保custom_raw是列表格式
        if not isinstance(custom_raw, list):
            print(f"custom_raw is not a list, converting: {custom_raw}")
            if isinstance(custom_raw, str):
                custom_raw = [s.strip() for s in custom_raw.split(',')] if custom_raw else []
            else:
                custom_raw = []
        
        raw_sans = list(custom_raw)  # Use only the custom selected ones
        print(f"Final raw sans list: {raw_sans}")
        print(f"Sample check - is 'Little' in raw_sans? {'Little' in raw_sans}")
        print(f"=== DEBUG REQUEST END ===")
        
        calculator = SansCalculator()
        calculator.setup(sans_data, raw_sans, DEFAULT_LIMITED_SANS, include_limited, server_luck)
        
        probs, total_weight = calculator.calculate_probabilities()
        all_probabilities = calculator.probability_all_in_time(time_seconds)
        
        sorted_by_prob = sorted(all_probabilities.items(), 
                              key=lambda x: x[1]['probability_percent'], reverse=True)
        sorted_by_rarity = sorted(all_probabilities.items(), 
                                key=lambda x: x[1]['base_probability'])
        
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
        
        results = {
            'total_sans': len(probs),
            'total_weight': total_weight,
            'server_luck': server_luck,
            'time_seconds': time_seconds,
            'all_probabilities': all_probabilities,
            'sorted_by_prob': sorted_by_prob[:20],
            'sorted_by_rarity': sorted_by_rarity[:20],
            'selected_results': selected_results
        }
        
        return jsonify({'success': True, 'results': results})
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)