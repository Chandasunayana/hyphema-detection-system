import random
import string

class VisionScreener:
    
    def __init__(self):
        self.snellen_chart = {
            '6/6': 'Normal vision',
            '6/9': 'Mild vision loss',
            '6/12': 'Moderate vision loss',
            '6/18': 'Moderate-severe vision loss',
            '6/24': 'Severe vision loss',
            '6/36': 'Profound vision loss',
            '6/60': 'Near blindness'
        }
    
    def generate_snellen_row(self, size):
        """
        Generate a row of letters for Snellen chart
        """
        # Letters typically used in Snellen charts
        letters = ['E', 'F', 'P', 'T', 'O', 'Z', 'L', 'P', 'E', 'D']
        
        # Randomly select 5 letters
        row = random.sample(letters, 5)
        return ' '.join(row)
    
    def simulate_vision_test(self, responses):
        """
        Simulate vision test based on user responses
        In production, this would be an interactive test
        """
        # For demo: generate random vision score
        scores = list(self.snellen_chart.keys())
        weights = [0.3, 0.25, 0.2, 0.1, 0.07, 0.05, 0.03]
        
        vision_score = random.choices(scores, weights=weights)[0]
        
        return {
            'score': vision_score,
            'interpretation': self.snellen_chart[vision_score],
            'needs_attention': vision_score > '6/9'
        }
    
    def interpret_vision_score(self, score):
        """
        Interpret vision score
        """
        return self.snellen_chart.get(score, 'Unknown')
    
    def get_vision_recommendation(self, score):
        """
        Get recommendation based on vision score
        """
        if score <= '6/9':
            return "Vision appears normal. Regular check-ups recommended."
        elif score <= '6/12':
            return "Mild vision impairment. Consider consulting an optometrist."
        elif score <= '6/18':
            return "Moderate vision impairment. Schedule eye examination soon."
        elif score <= '6/24':
            return "Significant vision impairment. Professional consultation recommended."
        else:
            return "Severe vision impairment. Immediate eye examination required."