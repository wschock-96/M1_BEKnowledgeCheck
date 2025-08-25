import unittest
from app import create_app
from app.models import db, Mechanic
from app.util.auth import encode_auth_token
from werkzeug.security import generate_password_hash


class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name='Test Mechanic',
            email='test@mechanic.com',
            salary=50000.0,
            password=generate_password_hash('123'))
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_auth_token(1)
        self.client = self.app.test_client()

    def test_login_mechanic(self):
        payload = {
            'email': 'test@mechanic.com',
            'password': '123'
        }

        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_mechanic_update(self):
        update_payload = {
            'name': 'Updated Mechanic',
            'email': 'test@mechnaic.com',
            'salary': 60000.0,
            'password': '123'
        }

        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        response = self.client.put('/mechanics/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Mechanic')

    def test_mechanic_get(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test Mechanic')

    def test_mechanic_delete(self):
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)

        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 404)

    def test_create_mechanic(self):
        payload = {
            'name': 'New Mechanic',
            'email': 'mechanic@email.com',
            'password': '123',
            'salary': 70000.0
        }
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'New Mechanic')


# NEGATIVE TESTS #

    def test_login_mechanic_unknown_email(self):
        payload = {'email': 'nouser@example.com', 'password': '123'}
        resp = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(resp.status_code, 401)

    def test_mechanic_update_invalid_fields(self):
        payload = {
            'name': 'Updated Mechanic',
            'salary': -10.0,
            'parts': 'invalid field',
            'password': '12'
        }
        headers = {'Authorization': f'Bearer {self.token}'}
        resp = self.client.put('/mechanics/1', json=payload, headers=headers)
        self.assertEqual(resp.status_code, 400)

    