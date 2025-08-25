import unittest
from app import create_app
from app.models import db, ServiceTicket, Customer, Mechanic, PartDescription, SerializedPart
from app.util.auth import encode_auth_token
from datetime import date

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.ticket = ServiceTicket(
            id=1,
            date=date(2025, 12, 25),
            customer_id=1,
            service_desc='rotate tires',
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(Customer(
                id=1,
                name='Test Customer',
                email='customer1@example.com', 
                phone='1234567890'            
            ))
            db.session.add(Mechanic(
                id=6,
                name='Test Mechanic',
                email='testmechanic@email.com',
                salary=50000.0,
                password='123'
            ))
            pd = PartDescription(
                id=1,
                part='Test Part',
                brand='Acme',     
                price=10.00              
            )
            db.session.add(SerializedPart(
                ticket_id=1,        
                desc_id=1,
                id=1 
                ))
            db.session.add(pd)
            db.session.add(self.ticket)
            db.session.commit()
        self.token = encode_auth_token(1, role='admin')
        self.client = self.app.test_client()


    def test_create_service_ticket(self):
        payload = {
            'customer_id': 1,
            'date': '2025-12-25',
            'service_desc': 'rotate tires'
        }

        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        response = self.client.post('/service-tickets/', json=payload, headers=headers)
        self.assertEqual(response.status_code, 201, msg=response.get_data(as_text=True))
        self.assertEqual(response.json['service_desc'], 'rotate tires')

    def test_get_service_tickets(self):
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['service_desc'], 'rotate tires')

    def test_add_mechanic_to_ticket(self):
        response = self.client.put('/service-tickets/1/add-mechanic/6',)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_remove_mechanic_from_ticket(self):
        response = self.client.put('/service-tickets/1/remove-mechanic/6')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    def test_add_part_to_ticket(self):
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)





    