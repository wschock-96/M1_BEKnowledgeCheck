import unittest
from app import create_app
from app.models import db, Customer


class TestCustomers(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(name='Test', email='test@test.com', phone='0987654321')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_customer(self):
        payload = {
            'name': 'John Doe',
            'email': 'johndoe@email.com',
            'phone': '1234567890'
        }

        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')
    
    def test_get_customers(self):
        response = self.client.get('/customers/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')

    def test_get_customer_by_id(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test')

    def test_update_customer(self):
        update_payload = {
            'name': 'Updated Name',
            'email': 'updatedemail@email.com',
            'phone': '1234567890'
        }
        response = self.client.put('/customers/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Name')

    def test_update_customer_invalid_id(self):
        update_payload = {
            'name': 'Invalid ID',
            'email': 'invalid@email.com',
            'phone': '1234567890'
        }
        response = self.client.put('/customers/99999', json=update_payload)
        self.assertEqual(response.status_code, 404)


    def test_delete_customer(self):
        response = self.client.delete('/customers/1')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 404)
    

# NEGATIVE TESTING #

    def test_create_customer_missing_fields(self):
        payload = {
            'name': 'Jane Doe',
            'phone': '1234567890'
        }

        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 400)


    