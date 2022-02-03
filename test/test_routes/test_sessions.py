
from fastapi.testclient import TestClient
from src.server.main import app
import unittest

from src.server.repositories.users import remove_user_by_id

client = TestClient(app)

TEST_USER = 'test user'
TEST_EMAIL = 'test@gmail.com'
TEST_PASSWORD = 'betterpros'


class SessionsTest(unittest.TestCase):
    sign_up_url = '/signup'
    log_in_url = '/login'

    @staticmethod
    def remove_user_by_response(response):
        user_id = response.json().get('user_id')
        remove_user_by_id(user_id)

    @staticmethod
    def verify_login_data(response_with_login_data):
        data = response_with_login_data.json()
        assert data.get('user_id', None) is not None
        assert data.get('access_token', None) is not None

    def test_signup_success(self):
        signup_data = dict(user_name=TEST_USER, email=TEST_EMAIL, password=TEST_PASSWORD)
        response = client.post(self.sign_up_url, json=signup_data)
        self.assertEqual(response.status_code, 201)
        self.verify_login_data(response)
        self.remove_user_by_response(response)

    def test_signup_error(self):
        signup_data = dict(user_name=TEST_USER, email=TEST_EMAIL, password=TEST_PASSWORD)

        response_ok = client.post(self.sign_up_url, json=signup_data)
        self.assertEqual(response_ok.status_code, 201)
        self.verify_login_data(response_ok)

        response_error = client.post(self.sign_up_url, json=signup_data)
        self.assertEqual(response_error.status_code, 400)

        self.remove_user_by_response(response_ok)

    def test_signup_fail(self):
        response = client.post(self.sign_up_url, json=dict(user_name=TEST_USER, password=TEST_PASSWORD))
        self.assertEqual(response.status_code, 422)

        response = client.post(self.sign_up_url, json=dict(email=TEST_EMAIL, password=TEST_PASSWORD))
        self.assertEqual(response.status_code, 422)

        response = client.post(self.sign_up_url, json=dict(user_name=TEST_USER, email=TEST_EMAIL))
        self.assertEqual(response.status_code, 422)

    def test_login_success(self):
        signup_data = dict(user_name=TEST_USER, email=TEST_EMAIL, password=TEST_PASSWORD)
        signup_response = client.post(self.sign_up_url, json=signup_data)

        self.assertEqual(signup_response.status_code, 201)
        self.verify_login_data(signup_response)

        login_data = dict(email=TEST_EMAIL, password=TEST_PASSWORD)
        login_response = client.post(self.log_in_url, json=login_data)

        self.assertEqual(login_response.status_code, 200)
        self.verify_login_data(login_response)

        self.assertEqual(signup_response.json().get('user_id'), login_response.json().get('user_id'))

        self.remove_user_by_response(signup_response)

    def test_login_fail(self):
        signup_data = dict(user_name=TEST_USER, email=TEST_EMAIL, password=TEST_PASSWORD)
        signup_response = client.post(self.sign_up_url, json=signup_data)
        self.assertEqual(signup_response.status_code, 201)
        self.verify_login_data(signup_response)

        login_data = dict(email='tolong' * 300, password=TEST_PASSWORD)
        login_response = client.post(self.log_in_url, json=login_data)
        self.assertEqual(login_response.status_code, 401)

        login_data = dict(email=TEST_EMAIL, password='tolong' * 300)
        login_response = client.post(self.log_in_url, json=login_data)
        self.assertEqual(login_response.status_code, 401)

        self.remove_user_by_response(signup_response)
