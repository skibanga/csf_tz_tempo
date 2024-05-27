import frappe
import requests
import json
from frappe.model.document import Document

class VehicleLocationLog(Document):
    def before_save(self):
        if not self.location:
            frappe.throw("Location name is required.")
        
        if not self.latitude and not self.longitude:
            coordinates = self.fetch_coordinates(self.location)
               
            if not coordinates:
                frappe.throw("Coordinates could not be fetched.")
            
            self.latitude = coordinates.get('latitude')
            self.longitude = coordinates.get('longitude')
            self.map = self.construct_map_field(coordinates)
            self.location_details = coordinates.get('display_name')

    def fetch_coordinates(self, location_name):
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={location_name}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            # Select the entry with the highest importance
            location = max(data, key=lambda x: x.get('importance', 0))
            return {
                'latitude': location.get('lat'),
                'longitude': location.get('lon'),
                'display_name': location.get('display_name')
            }
        except requests.exceptions.RequestException as e:
            frappe.throw(f"Error fetching coordinates: {str(e)}")

    def construct_map_field(self, coordinates):
        map_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(coordinates['longitude']), float(coordinates['latitude'])]
                    },
                    "properties": {
                        "icon": "car"  # Custom property for vehicle icon
                    }
                }
            ]
        }
        return json.dumps(map_data)  # Serialize map_data to a JSON string
