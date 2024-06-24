"""Flask app test scenarios."""
import logging

import pytest
import requests

_log = logging.getLogger('Main')
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]  %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
_log.addHandler(console_handler)
_log.setLevel(logging.DEBUG)

base_url = 'http://127.0.0.1:8080'
auth = {'username': 'user', 'password': 'user'}
request_timeout = 5

USER_DATA = {'name': 'Test', 'funds': 100, 'login': 'pytest_usr', 'password': 'pytest_pwd', 'birth_date': '2005-01-01',
             'phone': '123', 'email': ''}


class TestFitnessCenter:
    """Endpoints check."""

    @pytest.fixture()
    def session(self):
        """Session fixture."""
        _log.info('Session login')
        session = requests.Session()
        content = {'login': USER_DATA['login'], 'password': USER_DATA['password']}
        response = session.post(f'{base_url}/login', data=content)
        if response.status_code != 200:
            pytest.fail('Unsuccessful login')
        yield session
        response = session.get(f'{base_url}/logout')
        if response.status_code not in (200, 401):
            pytest.fail('Unsuccessful logout')
        _log.info('Session end')

    def test_register_get(self):
        """Registration get check."""
        _log.info('Register GET check...')
        response_data = requests.get(f'{base_url}/register', timeout=request_timeout)
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Register for Free' in response_data.text

    def test_register_post(self):
        """Registration post check."""
        _log.info('Register POST check...')
        response_data = requests.post(f'{base_url}/register', data=USER_DATA, timeout=request_timeout)
        assert response_data.status_code == 200, f'Content was not created {response_data.text}'
        assert 'Congratulations' in response_data.text

    def test_login_get(self):
        """Login get check."""
        _log.info('Login GET check...')
        rd = requests.get(f'{base_url}/login', timeout=request_timeout)
        assert rd.status_code == 200, 'Error during login get'
        assert 'Welcome to Fitness center!' in rd.text

    def test_login_post(self):
        """Login post check."""
        _log.info('Login POST check...')
        content = {'login': USER_DATA['login'], 'password': USER_DATA['password']}
        rd = requests.post(f'{base_url}/login', data=content, timeout=request_timeout)
        assert rd.status_code == 200, 'Content was not created'
        assert USER_DATA['name'] in rd.text, 'Username not fount on html page after login'

    def test_logout(self, session):
        """Logout get check."""
        _log.info('Logout GET check...')
        rd = session.get(f'{base_url}/logout', timeout=request_timeout)
        assert rd.status_code == 200, 'Error during logout'
        assert 'Welcome to Fitness center!' in rd.text

    def test_user_get_not_authenticated(self):
        """User get check."""
        _log.info('User info GET check without auth...')
        response_data = requests.get(f'{base_url}/user', timeout=request_timeout)
        assert response_data.status_code == 200, 'User able access restricted context'
        assert 'Welcome to Fitness center!' in response_data.text

    def test_user_get(self, session):
        """User get check."""
        _log.info('User info GET check...')
        response_data = session.get(f'{base_url}/user')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_user_post(self, session):
        """User post check."""
        _log.info('User POST check...')
        content = {}
        response_data = session.post(f'{base_url}/user', json=content)
        assert response_data.status_code == 200, 'Content was not created'
        assert response_data.text == 'user edit endpoint'

    def test_user_funds_get(self, session):
        """User funds get check."""
        _log.info('User funds GET check...')
        response_data = session.get(f'{base_url}/user/funds')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_user_funds_post(self, session):
        """User funds post check."""
        _log.info('User funds GET check...')
        content = {}
        response_data = session.post(f'{base_url}/user/funds', json=content)
        assert response_data.status_code == 200, 'Content was not created'
        assert response_data.text == 'user funds endpoint'

    def test_user_pre_reservation_post(self, session):
        """User pre reservations post check."""
        _log.info('User pre reservation POST check...')
        content = {'date': '2024-06-10', 'service': 4, 'trainer': 1}
        rd = session.post(f'{base_url}/user/pre_reservation', data=content)
        assert rd.status_code == 200, f'Content was not created\n {rd.text}'
        assert 'Available start time' in rd.text

    def test_user_reservations_get(self, session):
        """User reservations get check."""
        _log.info('User reservations GET check...')
        response_data = session.get(f'{base_url}/user/reservations')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Reservations:' in response_data.text

    def test_user_reservations_post(self, session):
        """User reservations post check."""
        _log.info('User reservations POST check...')
        content = {'date': '2024-06-10', 'service': 4, 'trainer': 1, 'start_time': '17-30'}
        rd = session.post(f'{base_url}/user/reservations', data=content)
        assert rd.status_code == 200, f'Content was not created\n {rd.text}'
        assert 'Congratulations' in rd.text

    def test_user_reservation_get(self, session):
        """User reservation get check."""
        _log.info('User reservation GET check...')
        rd = session.get(f'{base_url}/user/reservations/{1}')
        assert rd.status_code == 200, 'Error during context get'
        assert 'Db Data' in rd.text

    def test_user_reservation_delete(self, session):
        """User reservation delete check."""
        _log.info('User reservation DELETE check...')
        response_data = session.get(f'{base_url}/user/reservations/{1}/delete')
        assert response_data.status_code == 200, 'Content was not delete'
        assert 'Reservations:' in response_data.text

    def test_user_checkout_get(self, session):
        """User checkout get check."""
        _log.info('User checkout GET check...')
        response_data = session.get(f'{base_url}/user/checkout')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_user_checkout_post(self, session):
        """User checkout post check."""
        _log.info('User checkout POST check...')
        content = {}
        response_data = session.post(f'{base_url}/user/checkout', json=content)
        assert response_data.status_code == 200, 'Content was not created'
        assert response_data.text == 'user_checkout_endpoint'

    def test_fitness_centers_get(self, session):
        """Fitness centers get check."""
        _log.info('Fitness centers GET check...')
        response_data = session.get(f'{base_url}/fitness_center')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_fitness_center_get(self, session):
        """Fitness center get check."""
        _log.info('Fitness center GET check...')
        center_id = 1
        response_data = session.get(f'{base_url}/fitness_center/{center_id}')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_fitness_center_trainers_get(self, session):
        """Trainers get check."""
        _log.info('Fitness center trainers GET check...')
        fc_id = 1
        rd = session.get(f'{base_url}/fitness_center/{fc_id}/trainer')
        assert rd.status_code == 200, 'Error during context get'
        assert 'Db Data' in rd.text

    def test_fitness_center_trainer_get(self, session):
        """Fitness center trainer get check."""
        _log.info('Fitness center trainer GET check...')
        fc_id = 1
        t_id = 1
        rd = session.get(f'{base_url}/fitness_center/{fc_id}/trainer/{t_id}')
        assert rd.status_code == 200, 'Error during context get'
        assert 'Trainer' in rd.text

    def test_fitness_center_trainer_rating_get(self, session):
        """Fitness center trainer rating get check."""
        _log.info('Fitness center trainer rating GET check...')
        fc_id = 1
        t_id = 1
        rd = session.get(f'{base_url}/fitness_center/{fc_id}/trainer/{t_id}/rating')
        assert rd.status_code == 200, 'Error during context get'
        assert 'Trainer rating' in rd.text

    def test_fitness_center_trainer_rating_post(self, session):
        """Fitness center trainer rating post check."""
        _log.info('Fitness center trainer rating POST check...')
        center_id = 1
        curr_uuid = 1
        content = {'trainer': 1, 'user': 1, 'points': '100', 'text': 'Perfect'}
        response_data = session.post(f'{base_url}/fitness_center/{center_id}/trainer/{curr_uuid}/rating', data=content)
        assert response_data.status_code == 200, 'Content was not created'
        assert 'Congratulations' in response_data.text

    def test_fitness_center_services_get(self, session):
        """Fitness center services get check."""
        _log.info('Fitness center services GET check...')
        center_id = 1
        response_data = session.get(f'{base_url}/fitness_center/{center_id}/services')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_fitness_center_service_get(self, session):
        """Fitness center get check."""
        _log.info('Fitness center service GET check...')
        center_id = 1
        service_id = 1
        response_data = session.get(f'{base_url}/fitness_center/{center_id}/services/{service_id}')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Service:' in response_data.text

    def test_fitness_center_loyalty_programs_get(self, session):
        """Loyalty get check."""
        _log.info('Fitness center loyalty programs GET check...')
        center_id = 1
        response_data = session.get(f'{base_url}/fitness_center/{center_id}/loyalty_programs')
        assert response_data.status_code == 200, 'Error during context get'
        assert response_data.text == f'fitness_center "{center_id}" loyalty endpoint'

