"""Flask app test scenarios."""
import logging
from uuid import uuid4

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


class TestFitnessCenter:
    """Endpoints check."""

    @pytest.fixture(scope='class')
    def session(self):
        """Session fixture."""
        _log.info('Session login')
        session = requests.Session()
        response = session.post(f'{base_url}/login', json=auth)
        if response.status_code != 200:
            pytest.fail('Unsuccessful login')
        yield session
        _log.info('Session end')

    def test_login_get(self):
        """Login get check."""
        _log.info('Login GET check...')
        rd = requests.get(f'{base_url}/login', timeout=request_timeout)
        assert rd.status_code == 200, 'Error during login get'
        assert 'Welcome to Fitness center!' in rd.text

    def test_login_post(self):
        """Login post check."""
        _log.info('Login POST check...')
        content = {}
        rd = requests.post(f'{base_url}/login', json=content,
                           timeout=request_timeout)
        assert rd.status_code == 200, 'Content was not created'
        assert rd.text == 'login endpoint'

    def test_user_get(self, session):
        """User get check."""
        _log.info('Users GET check...')
        response_data = session.get(f'{base_url}/user')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_user_post(self, session):
        """User post check."""
        _log.info('User POST check...')
        content = {}
        response_data = session.post(f'{base_url}/user', json=content)
        assert response_data.status_code == 200, 'Content was not created'
        assert response_data.text == 'user endpoint'

    def test_user_put(self, session):
        """User put check."""
        _log.info('User PUT check...')
        content = {}
        response_data = session.put(f'{base_url}/user', json=content)
        assert response_data.status_code == 200, 'Content was not updated'
        assert response_data.text == 'user endpoint'

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

    def test_user_reservations_get(self, session):
        """User reservations get check."""
        _log.info('User reservations GET check...')
        response_data = session.get(f'{base_url}/user/reservations')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Db Data' in response_data.text

    def test_user_reservations_post(self, session):
        """User reservations post check."""
        _log.info('User reservations POST check...')
        content = {}
        rd = session.post(f'{base_url}/user/reservations', json=content)
        assert rd.status_code == 200, 'Content was not created'
        assert rd.text == 'user reservations endpoint'

    def test_user_reservation_get(self, session):
        """User reservation get check."""
        _log.info('User reservation GET check...')
        curr_id = 1
        rd = session.get(f'{base_url}/user/reservations/{1}')
        assert rd.status_code == 200, 'Error during context get'
        assert 'Db Data' in rd.text

    def test_user_reservation_put(self, session):
        """User reservation put check."""
        _log.info('User reservation PUT check...')
        content = {}
        r_id = 1
        rd = session.put(f'{base_url}/user/reservations/{r_id}', json=content)
        assert rd.status_code == 200, 'Content was not modified'
        assert rd.text == f'user reservation "{r_id}" endpoint'

    def test_user_reservation_delete(self, session):
        """User reservation delete check."""
        _log.info('User reservation DELETE check...')
        r_id = 1
        response_data = session.delete(f'{base_url}/user/reservations/{r_id}')
        assert response_data.status_code == 200, 'Content was not delete'
        assert response_data.text == f'user reservation "{r_id}" endpoint'

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

    def test_user_checkout_put(self, session):
        """User checkout put check."""
        _log.info('User checkout PUT check...')
        content = {}
        response_data = session.put(f'{base_url}/user/checkout', json=content)
        assert response_data.status_code == 200, 'Content was not updated'
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
        assert 'Db Data' in rd.text

    def test_fitness_center_trainer_rating_get(self, session):
        """Fitness center trainer rating get check."""
        _log.info('Fitness center trainer rating GET check...')
        fc_id = 1
        t_id = 1
        rd = session.get(f'{base_url}/fitness_center/{fc_id}/trainer/{t_id}/rating')
        assert rd.status_code == 200, 'Error during context get'
        assert 'Db Data' in rd.text

    def test_fitness_center_trainer_rating_post(self, session):
        """Fitness center trainer rating post check."""
        _log.info('Fitness center trainer rating POST check...')
        center_id = 1
        curr_uuid = 1
        content = {}
        response_data = session.post(f'{base_url}/fitness_center/{center_id}/trainer/{curr_uuid}/rating',
                                     json=content)
        assert response_data.status_code == 200, 'Content was not created'
        assert response_data.text == f'fitness_center "{center_id}" trainer "{curr_uuid}" rating endpoint'

    def test_fitness_center_trainer_rating_put(self, session):
        """Fitness center trainer rating put check."""
        _log.info('Fitness center trainer rating PUT check...')
        center_id = 1
        curr_uuid = 1
        content = {}
        response_data = session.put(f'{base_url}/fitness_center/{center_id}/trainer/{curr_uuid}/rating',
                                    json=content)
        assert response_data.status_code == 200, 'Content was not created'
        assert f'fitness_center "{center_id}" trainer "{curr_uuid}" rating endpoint'

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
        assert 'Db Data' in response_data.text

    def test_register_get(self, session):
        """Registration get check."""
        _log.info('Register GET check...')
        response_data = session.get(f'{base_url}/register')
        assert response_data.status_code == 200, 'Error during context get'
        assert 'Register for Free' in response_data.text

    def test_register_post(self, session):
        """Registration post check."""
        _log.info('Register POST check...')
        content = {'name': 'Test', 'funds': 0, 'login': 'pytest2', 'password': 'pytest', 'birth_date': '2005-01-01',
                   'phone': '123'}
        response_data = session.post(f'{base_url}/register', data=content)
        assert response_data.status_code == 200, f'Content was not created {response_data.text}'
        assert 'Congratulations' in response_data.text

    def test_fitness_center_loyalty_programs_get(self, session):
        """Loyalty get check."""
        _log.info('Fitness center loyalty programs GET check...')
        center_id = 1
        response_data = session.get(f'{base_url}/fitness_center/{center_id}/loyalty_programs')
        assert response_data.status_code == 200, 'Error during context get'
        assert response_data.text == f'fitness_center "{center_id}" loyalty endpoint'
