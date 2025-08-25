import unittest 
from app import create_app
from app.models import db, PartDescription

class TestPartDescriptions(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.part_description = PartDescription(
            part='Test Part',
            brand='Test Brand',
            price=100.0
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part_description)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_part_description(self):
        payload = {
            'part': 'New Part',
            'brand': 'Test Brand',
            'price': 150.0,
        }

        response = self.client.post('/part-descriptions/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part'], 'New Part')

    def test_get_part_descriptions(self):
        response = self.client.get('/part-descriptions/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['part'], 'Test Part')

    def test_get_part_description_by_id(self):
        response = self.client.get('/part-descriptions/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part'], 'Test Part')

    def test_update_part_description(self):
        update_payload = {
            'part': 'Updated Part',
            'brand': 'Updated Brand',
            'price': 200.0,
        }
        response = self.client.put('/part-descriptions/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part'], 'Updated Part')

    def test_delete_part_description(self):
        response = self.client.delete('/part-descriptions/1')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/part-descriptions/1')
        self.assertEqual(response.status_code, 404)


# NEGATIVE TESTING #

    def test_create_part_description_invalid_data(self):
        payload = {
            'part': '',  
            'name': 'Test Name',
            'price': -50.0,  
        }

        response = self.client.post('/part-descriptions/', json=payload)
        self.assertEqual(response.status_code, 400)