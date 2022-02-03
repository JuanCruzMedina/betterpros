import unittest

from starlette.testclient import TestClient
from src.server.main import app

from src.server.repositories.conversations import remove_conversation_by_id
from src.server.repositories.users import remove_user_by_id

client = TestClient(app)


def header(token):
    return {
        'Authorization': f'Bearer {token}'
    }


class UsersTestCase(unittest.TestCase):
    create_conversation_url: str = "/conversations"
    sign_up_url = '/signup'
    ids_of_conversations: list[int] = []

    user_1 = {'user_name': 'Pi', 'email': 'pi@gmail.com', 'password': '1234', 'access_token': None,
              'user_id': None}
    user_2 = {'user_name': 'jhon', 'email': 'jhon@gmail.com', 'password': '1234', 'access_token': None,
              'user_id': None}
    user_3 = {'user_name': 'peter', 'email': 'peter@gmail.com', 'password': '1234', 'access_token': None,
              'user_id': None}

    @property
    def list_of_users(self):
        return [self.user_1, self.user_2, self.user_3]

    @staticmethod
    def get_user_url(value):
        return f"/user/{value}"

    @staticmethod
    def verify_login_data(response_with_login_data):
        data = response_with_login_data.json()
        assert data.get('user_id', None) is not None
        assert data.get('access_token', None) is not None

    @staticmethod
    def verify_conversation_id(response_with_conversation_id):
        data = response_with_conversation_id.json()
        assert data.get('conversation_id', None) is not None

    @staticmethod
    def verify_user_data(response_with_user_data):
        data = response_with_user_data.json()
        assert data.get('user_id', None) is not None
        assert data.get('user_name', None) is not None
        assert data.get('email', None) is not None

    @staticmethod
    def get_conversation_data(title: str = None, conversation_type: str = None, ids_of_invited_users: list[int] = None):
        return {"title": title, "type": conversation_type, "ids_of_invited_users": ids_of_invited_users}

    def setUp(self):
        # Create users
        for test_user in self.list_of_users:
            signup_data = dict(user_name=test_user['user_name'], email=test_user['email'],
                               password=test_user['password'])
            response = client.post(self.sign_up_url, json=signup_data)
            self.assertEqual(response.status_code, 201)
            self.verify_login_data(response)

            user_id: int = response.json().get('user_id')
            access_token: int = response.json().get('access_token')
            test_user['user_id'] = user_id
            test_user['access_token'] = access_token

        # Create p2p conversation
        create_conversation_data = self.get_conversation_data('happy chat', 'peer-to-peer', [self.user_2['user_id']])

        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_1['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 201)
        self.verify_conversation_id(create_conversation_response)

        # Save conversation_id
        new_conversation_id = create_conversation_response.json().get('conversation_id')
        self.ids_of_conversations.append(new_conversation_id)

    def test_get_user_success_(self):
        get_user_response = client.get(self.get_user_url(self.user_2['user_id']),
                                       headers=header(self.user_1['access_token']))
        self.assertEqual(get_user_response.status_code, 200)
        self.verify_user_data(get_user_response)

    def test_get_user_success_self_search(self):
        get_user_response = client.get(self.get_user_url(self.user_1['user_id']),
                                       headers=header(self.user_1['access_token']))
        self.assertEqual(get_user_response.status_code, 200)
        self.verify_user_data(get_user_response)

    def test_get_user_success_no_conversation(self):
        get_user_response = client.get(self.get_user_url(self.user_3['user_id']),
                                       headers=header(self.user_1['access_token']))
        self.assertEqual(get_user_response.status_code, 200)
        self.verify_user_data(get_user_response)

    def test_get_user_fail_user_not_found(self):
        get_user_response = client.get(self.get_user_url(123123), headers=header(self.user_1['access_token']))
        self.assertEqual(get_user_response.status_code, 404)

    def test_get_user_fail_error(self):
        get_user_response = client.get(self.get_user_url('bad_user_id'), headers=header(self.user_1['access_token']))
        self.assertEqual(get_user_response.status_code, 422)

    def tearDown(self):
        # Delete conversations
        for conversation_id in self.ids_of_conversations:
            remove_conversation_by_id(conversation_id)

        # Delete users
        for test_user in self.list_of_users:
            user_id: int = int(test_user['user_id'])
            remove_user_by_id(user_id)
