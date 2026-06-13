import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

class HospitalFinder:
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="attendance_system")
        
        # Sample hospital database
        self.hospitals = [
            {
                'id': 1,
                'name': 'City Eye Hospital',
                'address': '123 Medical Avenue, City Center',
                'phone': '+91 98765 43210',
                'specialty': 'Ophthalmology',
                'emergency': True,
                'lat': 17.3850,
                'lon': 78.4867,
                'timing': '24/7',
                'rating': 4.5
            },
            {
                'id': 2,
                'name': 'Vision Care Center',
                'address': '45 Health Street, Downtown',
                'phone': '+91 98765 43211',
                'specialty': 'Eye Care',
                'emergency': True,
                'lat': 17.3860,
                'lon': 78.4870,
                'timing': '8 AM - 8 PM',
                'rating': 4.3
            },
            {
                'id': 3,
                'name': 'Retina Specialists Clinic',
                'address': '78 Wellness Road, Uptown',
                'phone': '+91 98765 43212',
                'specialty': 'Retina & Ophthalmology',
                'emergency': False,
                'lat': 17.3845,
                'lon': 78.4860,
                'timing': '9 AM - 6 PM',
                'rating': 4.7
            },
            {
                'id': 4,
                'name': 'Community Health Center',
                'address': '12 Main Road, Sector 5',
                'phone': '+91 98765 43213',
                'specialty': 'General Hospital with Eye Care',
                'emergency': True,
                'lat': 17.3870,
                'lon': 78.4880,
                'timing': '24/7',
                'rating': 4.0
            },
            {
                'id': 5,
                'name': 'Advanced Eye Institute',
                'address': '234 Laser Street, Medical District',
                'phone': '+91 98765 43214',
                'specialty': 'Laser Eye Surgery',
                'emergency': False,
                'lat': 17.3830,
                'lon': 78.4850,
                'timing': '10 AM - 7 PM',
                'rating': 4.8
            }
        ]
    
    def get_user_location(self):
        """Get user's current location (simplified)"""
        # For demo, return a default location (Hyderabad)
        return (17.3850, 78.4867)
    
    def find_nearby_hospitals(self, user_location=None, radius_km=10):
        """Find hospitals within radius"""
        if user_location is None:
            user_location = self.get_user_location()
        
        nearby_hospitals = []
        
        for hospital in self.hospitals:
            hospital_location = (hospital['lat'], hospital['lon'])
            distance = geodesic(user_location, hospital_location).kilometers
            
            if distance <= radius_km:
                hospital_copy = hospital.copy()
                hospital_copy['distance'] = round(distance, 2)
                hospital_copy['distance_text'] = f"{hospital_copy['distance']} km"
                nearby_hospitals.append(hospital_copy)
        
        # Sort by distance
        nearby_hospitals.sort(key=lambda x: x['distance'])
        
        return nearby_hospitals
    
    def get_hospital_by_id(self, hospital_id):
        """Get hospital by ID"""
        for hospital in self.hospitals:
            if hospital['id'] == hospital_id:
                return hospital
        return None
    
    def get_directions_link(self, hospital):
        """Get Google Maps directions link"""
        return f"https://www.google.com/maps/dir/?api=1&destination={hospital['lat']},{hospital['lon']}"
    
    def search_hospitals_by_name(self, query):
        """Search hospitals by name"""
        results = []
        query = query.lower()
        
        for hospital in self.hospitals:
            if query in hospital['name'].lower() or query in hospital['specialty'].lower():
                results.append(hospital)
        
        return results
    
    def get_emergency_hospitals(self):
        """Get hospitals with emergency services"""
        return [h for h in self.hospitals if h['emergency']]
    
    def get_hospitals_by_specialty(self, specialty):
        """Get hospitals by specialty"""
        results = []
        specialty = specialty.lower()
        
        for hospital in self.hospitals:
            if specialty in hospital['specialty'].lower():
                results.append(hospital)
        
        return results