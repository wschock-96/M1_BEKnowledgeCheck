import unittest
from app import create_app
from app.models import db, SerializedPart, PartDescription

class TestSerializedParts(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            desc = PartDescription(
                id=1,
                part="Test Part",
                brand="Test Brand",
                price=99.99
            )
            db.session.add(desc)

            sp = SerializedPart(
                id=1,
                desc_id=desc.id
            )
            db.session.add(sp)
            db.session.commit()

    def test_add_serialized_part(self):
        payload = {
            'desc_id': 1
        }
        response = self.client.post('/serialized-parts/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn('description', response.json)

    def test_get_serialized_parts(self):
        response = self.client.get('/serialized-parts/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['description']['part'], 'Test Part')

    def test_get_serialized_part_by_id(self):
        response = self.client.get('/serialized-parts/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part'], 'Test Part')

    def test_update_serialized_part(self):
        update_payload = {
            'desc_id': 1
        }
        response = self.client.put('/serialized-parts/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['desc_id'], {'desc_id':1, 'id': 1, 'ticket_id': None})

    def test_delete_serialized_part(self):
        response = self.client.delete('/serialized-parts/1')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/serialized-parts/1')
        self.assertEqual(response.status_code, 404)





    


