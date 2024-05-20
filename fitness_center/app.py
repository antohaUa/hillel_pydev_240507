"""Fitness center application."""
from db_utils import SqliteDb
from flask import Flask, render_template, request

app = Flask(__name__)


def render_db_data_template(query, single=True):
    """Render db data html template according single or multiple returned db rows data."""
    db = SqliteDb()
    if single:
        return render_template('db_data_single.html', result=db.exec_query(query=query))
    return render_template('db_data_multiple.html', result=db.exec_query(query=query, single=False))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login."""
    if request.method == 'GET':
        return render_template('login.html')
    return 'login endpoint'


@app.get('/user')
def user_get():
    """User get operations."""
    query = 'select * from user'
    return render_db_data_template(query, single=True)


@app.route('/user', methods=['POST', 'PUT'])
def user():
    """User operations."""
    return 'user endpoint'


@app.route('/user/funds', methods=['GET', 'POST'])
def user_funds():
    """Funds operations for certain user."""
    if request.method == 'GET':
        query = 'select funds from user'
        return render_db_data_template(query, single=True)
    return 'user funds endpoint'


@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    """User operations with reservations."""
    if request.method == 'GET':
        query = 'select * from reservation'
        return render_db_data_template(query, single=False)
    return 'user reservations endpoint'


@app.route('/user/reservations/<int:reservation_id>',
           methods=['GET', 'PUT', 'DELETE'])
def user_reservation(reservation_id):
    """Operations with certain reservation."""
    if request.method == 'GET':
        query = f'select * from reservation where id={reservation_id}'
        return render_db_data_template(query, single=True)
    return f'user reservation "{reservation_id}" endpoint'


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
def user_checkout():
    """Checkout list operations."""
    if request.method == 'GET':
        query = 'select * from services_balance'
        return render_db_data_template(query, single=False)
    return 'user_checkout_endpoint'


@app.get('/fitness_center')
def fitness_centers():
    """Info for all fitness centers."""
    query = 'select * from fitness_center'
    return render_db_data_template(query, single=False)


@app.get('/fitness_center/<int:fc_id>')
def fitness_center(fc_id):
    """Certain fitness center info."""
    query = f'select * from fitness_center where id={fc_id}'
    return render_db_data_template(query, single=True)


@app.get('/fitness_center/<int:fc_id>/trainer')
def fitness_center_trainers(fc_id):
    """Trainers info for certain fitness centers."""
    query = f'select * from trainer where fitness_center={fc_id}'
    return render_db_data_template(query, single=False)


@app.get('/fitness_center/<int:fc_id>/trainer/<int:trainer_id>')
def fitness_center_trainer(fc_id, trainer_id):
    """Certain trainer info."""
    query = f'select * from trainer where fitness_center={fc_id} and id={trainer_id}'
    return render_db_data_template(query, single=True)


@app.route('/fitness_center/<int:fc_id>/trainer/<int:trainer_id>/rating',
           methods=['GET', 'POST', 'PUT'])
def fitness_center_trainer_rating(fc_id, trainer_id):
    """Trainer rating operations."""
    if request.method == 'GET':
        query = f'select trainer.name, rating.points, rating.text from rating, trainer where trainer.id={trainer_id}'
        return render_db_data_template(query, single=True)
    return f'fitness_center "{fc_id}" trainer "{trainer_id}" rating endpoint'


@app.get('/fitness_center/<int:fc_id>/services')
def fitness_center_services(fc_id):
    """Services for certain fitness center."""
    query = f'select * from service where fitness_center={fc_id}'
    return render_db_data_template(query, single=False)


@app.get('/fitness_center/<int:fc_id>/services/<int:service_id>')
def fitness_center_service(fc_id, service_id):
    """Certain service info."""
    query = f'select * from service where fitness_center={fc_id} and id={service_id}'
    return render_db_data_template(query, single=False)


@app.get('/register')
def register_get():
    """Registration info."""
    return render_template('register.html')


@app.post('/register')
def register_post():
    """Do registration."""
    db = SqliteDb()
    form_dict = request.form.to_dict()
    values = f"(\'{form_dict['name']}\', \'{form_dict['login']}\', \'{form_dict['password']}', \'{form_dict['birth_date']}\', \'{form_dict['phone']}\')"
    query = f'insert into user (name, login, password, birth_date, phone) values {values}'
    db.exec_query(query=query, commit=True)
    return render_template('congratulation.html')


@app.get('/fitness_center/<int:fc_id>/loyalty_programs')
def fitness_center_loyalty(fc_id):
    """Loyalty program."""
    return f'fitness_center "{fc_id}" loyalty endpoint'


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080
    app.run(host=host, port=port, debug=True)
