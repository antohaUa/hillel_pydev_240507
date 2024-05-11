"""Fitness center application."""
from flask import Flask

app = Flask(__name__)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login."""
    return 'login endpoint'


@app.route('/user', methods=['GET', 'POST', 'PUT'])
def user():
    """User operations."""
    return 'user endpoint'


@app.route('/user/funds', methods=['GET', 'POST'])
def user_funds():
    """Funds operations for certain user."""
    return 'user funds endpoint'


@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    """User operations with reservations."""
    return 'user reservations endpoint'


@app.route('/user/reservations/<uuid:reservation_id>',
           methods=['GET', 'PUT', 'DELETE'])
def user_reservation(reservation_id):
    """Operations with certain reservation."""
    return f'user reservation "{reservation_id}" endpoint'


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
def user_checkout():
    """Checkout list operations."""
    return 'user checkout endpoint'


@app.get('/fitness_center')
def fitness_centers():
    """Info for all fitness centers."""
    return 'fitness centers endpoint'


@app.get('/fitness_center/<int:fc_id>')
def fitness_center(fc_id):
    """Certain fitness center info."""
    return f'fitness_center "{fc_id}" endpoint'


@app.get('/fitness_center/<int:fc_id>/trainer')
def fitness_center_trainers(fc_id):
    """Trainers info for certain fitness centers."""
    return f'fitness_center "{fc_id}" trainers endpoint'


@app.get('/fitness_center/<int:fc_id>/trainer/<uuid:trainer_id>')
def fitness_center_trainer(fc_id, trainer_id):
    """Certain trainer info."""
    return f'fitness_center "{fc_id}" trainer "{trainer_id}" endpoint'


@app.route('/fitness_center/<int:fc_id>/trainer/<uuid:trainer_id>/rating',
           methods=['GET', 'POST', 'PUT'])
def fitness_center_trainer_rating(fc_id, trainer_id):
    """Trainer rating operations."""
    return f'fitness_center "{fc_id}" trainer "{trainer_id}" rating endpoint'


@app.get('/fitness_center/<int:fc_id>/services')
def fitness_center_services(fc_id):
    """Services for certain fitness center."""
    return f'fitness_center "{fc_id}" services endpoint'


@app.get('/fitness_center/<int:fc_id>/services/<int:service_id>')
def fitness_center_service(fc_id, service_id):
    """Certain service info."""
    return f'fitness_center "{fc_id}" service "{service_id}" endpoint'


@app.get('/register')
def register_get():
    """Registration info."""
    return 'registration info endpoint'


@app.post('/register')
def register_post():
    """Do registration."""
    return 'registration post endpoint'


@app.get('/fitness_center/<int:fc_id>/loyalty_programs')
def fitness_center_loyalty(fc_id):
    """Loyalty program."""
    return f'fitness_center "{fc_id}" loyalty endpoint'


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080
    app.run(host=host, port=port, debug=True)
