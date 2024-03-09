import unittest
from unittest.mock import patch
from flask import jsonify
from flask_jwt_extended import create_access_token
from main import create_app
from app.models import User


class TestUserEndpoints(unittest.TestCase):    
    def setUp(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config.from_prefixed_env()
        self.app = app.test_client()
        with app.app_context():
            # Create a test user
            self.test_user = User(
                firstname='test',
                lastname='user',
                email='testuser@example.com',
                description='Test description'
            )
            self.test_user.save()

            # Generate a JWT token for the test user
            self.jwt_token = create_access_token(identity=self.test_user.email)

    def tearDown(self):
        with self.app.application.app_context():
            # Delete the test user after each test
            self.test_user.delete()

    def test_get_user_details(self):
        response = self.app.get('/users/detail', headers={'Authorization': f'Bearer {self.jwt_token}'})
        print(response)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['details']['fullname'], 'John Doe')

    @unittest.skip
    def test_update_user_desc(self):
        with patch('app.views.user.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = self.test_user

            new_description = 'Updated description'
            response = self.app.put('/users/update', json={'description': new_description}, headers={'Authorization': f'Bearer {self.jwt_token}'})
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertEqual(data['message'], 'Description updated')

            # Verify that the user's description was updated
            updated_user = User.query.filter_by(email=self.test_user.email).first()
            self.assertEqual(updated_user.description, new_description)

    @unittest.skip
    def test_delete_user(self):
        response = self.app.delete('/users/deactivate', headers={'Authorization': f'Bearer {self.jwt_token}'})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['message'], 'User deactivated')

        # Verify that the user was deleted
        deleted_user = User.query.filter_by(email=self.test_user.email).first()
        self.assertIsNone(deleted_user)

    @unittest.skip
    def test_get_limited_users(self):
        # Simulate an admin user
        admin_jwt_token = create_access_token(identity='admin', additional_claims={'is_admin': True})

        response = self.app.get('/users/limit?page=1&per_page=3', headers={'Authorization': f'Bearer {admin_jwt_token}'})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('users', data)

if __name__ == '__main__':
    unittest.main()


