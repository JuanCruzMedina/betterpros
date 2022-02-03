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


class ConversationsTestCase(unittest.TestCase):
    create_conversation_url: str = "/conversations"
    sign_up_url = '/signup'
    log_in_url = '/login'

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
    def get_conversation_url(value):
        return f"/conversation/{value}"

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
    def verify_conversation_data(response_with_conversation_data):
        data = response_with_conversation_data.json()
        assert data.get('conversation_id', None) is not None
        assert data.get('title', None) is not None
        assert data.get('type', None) is not None
        assert len(data.get('ids_of_invited_users', [])) > 0

    @staticmethod
    def get_conversation_data(title: str = None, conversation_type: str = None, ids_of_invited_users: list[int] = None):
        return {"title": title, "type": conversation_type, "ids_of_invited_users": ids_of_invited_users}

    def setUp(self):
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

    def test_create_conversation_fail_title(self):
        create_conversation_data = self.get_conversation_data(conversation_type='peer-to-peer',
                                                              ids_of_invited_users=[self.user_2['user_id']])
        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_1['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 422)

    def test_create_conversation_fail_type(self):
        create_conversation_data = self.get_conversation_data('happy chat', 'p2p', [self.user_2['user_id']])
        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_1['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 400)

    def test_create_conversation_fail_empty_invited_users(self):
        create_conversation_data = self.get_conversation_data('happy chat', 'peer-to-peer', [])
        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_1['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 400)

    def test_create_conversation_fail_auto_invite(self):
        create_conversation_data = self.get_conversation_data('happy chat', 'peer-to-peer', [self.user_1['user_id']])
        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_1['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 400)

    def test_create_p2p_conversation_success(self):
        create_conversation_data = self.get_conversation_data('happy chat', 'peer-to-peer', [self.user_2['user_id']])

        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_1['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 201)
        self.verify_conversation_id(create_conversation_response)
        remove_conversation_by_id(create_conversation_response.json().get('conversation_id'))

    def test_create_group_chat_conversation_success(self):
        create_conversation_data = {
            "title": "work chat",
            "type": "group chat",
            "ids_of_invited_users": [
                self.user_2['user_id']
            ]
        }
        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_1['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 201)
        self.verify_conversation_id(create_conversation_response)
        remove_conversation_by_id(create_conversation_response.json().get('conversation_id'))

    def test_get_conversation_success(self):
        # Create conversation p2p between user_2 and user_3
        create_conversation_data = self.get_conversation_data('happy chat', 'peer-to-peer', [self.user_3['user_id']])

        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_2['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 201)
        self.verify_conversation_id(create_conversation_response)
        new_conversation_id = create_conversation_response.json().get('conversation_id')

        # Get conversation
        get_conversation_response = client.get(self.get_conversation_url(new_conversation_id),
                                               headers=header(self.user_2['access_token']))
        self.assertEqual(get_conversation_response.status_code, 200)
        self.verify_conversation_data(get_conversation_response)

        remove_conversation_by_id(get_conversation_response.json().get('conversation_id'))

    def test_get_conversation_not_found(self):
        get_conversation_response = client.get(self.get_conversation_url(123123),
                                               headers=header(self.user_2['access_token']))
        self.assertEqual(get_conversation_response.status_code, 404)

    def test_get_conversation_unauthorized(self):
        # Create conversation p2p between user_2 and user_3
        create_conversation_data = self.get_conversation_data(title='happy chat', conversation_type='peer-to-peer',
                                                              ids_of_invited_users=[self.user_3['user_id']])

        create_conversation_response = client.post(self.create_conversation_url,
                                                   headers=header(self.user_2['access_token']),
                                                   json=create_conversation_data)
        self.assertEqual(create_conversation_response.status_code, 201)
        self.verify_conversation_id(create_conversation_response)
        new_conversation_id = create_conversation_response.json().get('conversation_id')

        # Get conversation
        get_conversation_response = client.get(self.get_conversation_url(new_conversation_id),
                                               headers=header(self.user_1['access_token']))
        self.assertEqual(get_conversation_response.status_code, 423)

        remove_conversation_by_id(get_conversation_response.json().get('conversation_id'))

    def tearDown(self):
        for test_user in self.list_of_users:
            user_id: int = int(test_user['user_id'])
            remove_user_by_id(user_id)
