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
    if not query:
        return [(sans, 0) for sans in sans_list[:10]]
    
    query = query.lower()
    results = []
    
    for sans in sans_list:
        sans_lower = sans.lower()
        
        if sans_lower == query:
            score = 1.0
        elif sans_lower.startswith(query):
            score = 0.8
        elif re.search(r'\b' + re.escape(query) + r'\b', sans_lower):
            score = 0.6
        elif query in sans_lower:
            score = 0.4
        else:
            pattern = '.*'.join(query)
            if re.search(pattern, sans_lower):
                score = 0.2
            else:
                score = 0.0
        
        if score > 0:
            results.append((sans, score))
    
    results.sort(key=lambda x: (-x[1], x[0]))
    return results[:15]

class SansCalculator:
    def __init__(self):
        self.sans_list = []
    
    def setup(self, sans_data: Dict, raw_sans: List[str], limited_sans: List[str], include_limited: List[str], server_luck: int):
        self.sans_list = []
        self.server_luck = server_luck
        raw_set = set(raw_sans)
        limited_set = set(limited_sans)
        
        for name, chance in sans_data.items():
            if name in limited_set and name not in include_limited:
                continue
                
            is_raw = name in raw_set
            self.sans_list.append({
                "name": name,
                "chance": chance,
                "is_raw": is_raw
            })
    
    def calculate_probabilities(self):
        if not self.sans_list:
            return {}, 0.0
        
        final_probs = {}
        
        for sans in self.sans_list:
            chance = sans["chance"]
            
            if not sans["is_raw"]:
                chance = chance / self.server_luck
            
            chance = max(1, chance)
            success_prob = 1.0 / chance
            final_probs[sans["name"]] = success_prob
        
        total = sum(final_probs.values())
        if total > 0:
            for name in final_probs:
                final_probs[name] /= total
        
        total_weight = sum(1.0 / sans["chance"] if sans["is_raw"] else self.server_luck / sans["chance"] for sans in self.sans_list)
        
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
        probs, _ = self.calculate_probabilities()
        avg_sans_per_event = 16
        
        if target_sans:
            return avg_sans_per_event * probs[target_sans]["probability"]
        else:
            return {name: avg_sans_per_event * data["probability"] for name, data in probs.items()}
    
    def probability_in_time(self, target_sans: str, time_seconds: float):
        probs, _ = self.calculate_probabilities()
        if target_sans not in probs:
            return 0.0, 0.0
            
        events_per_second = 0.5
        total_events = events_per_second * time_seconds
        expected_per_event = self.expected_per_event(target_sans)
        lambda_total = expected_per_event * total_events
        prob_at_least_one = 1 - math.exp(-lambda_total)
        
        return prob_at_least_one, lambda_total
    
    def time_for_expected_first(self, target_sans: str):
        expected_per_event = self.expected_per_event(target_sans)
        events_per_second = 0.5
        
        if expected_per_event <= 0:
            return float('inf')
        
        return 1 / (expected_per_event * events_per_second)
    
    def time_for_certainty(self, target_sans: str, certainty: float = 0.99):
        expected_per_event = self.expected_per_event(target_sans)
        events_per_second = 0.5
        
        if expected_per_event <= 0:
            return float('inf')
        
        lambda_rate = expected_per_event * events_per_second
        return -math.log(1 - certainty) / lambda_rate
    
    def probability_all_in_time(self, time_seconds: float):
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
        
        sans_data = DEFAULT_SANS_DATA.copy()
        sans_data.update(custom_sans)
        
        if not isinstance(custom_raw, list):
            if isinstance(custom_raw, str):
                custom_raw = [s.strip() for s in custom_raw.split(',')] if custom_raw else []
            else:
                custom_raw = []
        
        raw_sans = list(custom_raw)
        
        calculator = SansCalculator()
        calculator.setup(sans_data, raw_sans, DEFAULT_LIMITED_SANS, include_limited, server_luck)
        
        probs, total_weight = calculator.calculate_probabilities()
        all_probabilities = calculator.probability_all_in_time(time_seconds)
        
        sorted_by_prob = sorted(all_probabilities.items(), key=lambda x: x[1]['probability_percent'], reverse=True)
        sorted_by_rarity = sorted(all_probabilities.items(), key=lambda x: x[1]['base_probability'])
        
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
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
