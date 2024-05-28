"""Fitness center application."""
from db_utils import SqliteDb
from flask import Flask, render_template, request

app = Flask(__name__)


def exec_db_query(**kwargs):
    """Execute certain DB query."""
    db = SqliteDb()
    if select_data := kwargs.get('select_data'):
        return db.select(select_data=select_data, join_data=kwargs.get('join_data'), single=kwargs.get('single', True),
                         where_data=kwargs.get('where_data'), join_type=kwargs.get('join_type', 'join'))
    elif insert_data := kwargs.get('insert_data'):
        db.insert(insert_data=insert_data)


def render_db_template(data):
    """Render common html template according single or multiple returned db rows data."""
    # for multiline data we receive list structure
    template_name = 'db_data_multiple.html' if type(data) == list else 'db_data_single.html'
    return render_template(template_name, result=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login."""
    if request.method == 'GET':
        return render_template('login.html')
    return 'login endpoint'


@app.get('/user')
def user_get():
    """User get operations."""
    select_data = {'user': ['id', 'name', 'funds', 'login', 'password', 'birth_date', 'phone']}
    data = exec_db_query(single=True, select_data=select_data)
    return render_db_template(data=data)


@app.route('/user', methods=['POST', 'PUT'])
def user():
    """User operations."""
    return 'user endpoint'


@app.route('/user/funds', methods=['GET', 'POST'])
def user_funds():
    """Funds operations for certain user."""
    if request.method == 'GET':
        select_data = {'user': ['name', 'funds']}
        data = exec_db_query(single=True, select_data=select_data)
        return render_db_template(data=data)
    return 'user funds endpoint'


@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    """User operations with reservations."""
    if request.method == 'GET':
        select_data = {
            'reservation': ['reservation.id', 'reservation.date', 'reservation.time',
                            'trainer.name', 'service.name', 'user.name']}
        join_data = {'trainer': 'trainer.id=reservation.trainer',
                     'service': 'service.id=reservation.service',
                     'user': 'user.id=reservation.user'}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data)
        return render_db_template(data=data)
    return 'user reservations endpoint'


@app.route('/user/reservations/<int:reservation_id>',
           methods=['GET', 'PUT', 'DELETE'])
def user_reservation(reservation_id):
    """Operations with certain reservation."""
    if request.method == 'GET':
        select_data = {
            'reservation': ['reservation.id', 'reservation.date', 'reservation.time',
                            'trainer.name', 'service.name', 'user.name']}
        join_data = {'trainer': 'trainer.id=reservation.trainer',
                     'service': 'service.id=reservation.service',
                     'user': 'user.id=reservation.user'}
        where_data = {'reservation.id': reservation_id}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
        return render_db_template(data=data)
    return f'user reservation "{reservation_id}" endpoint'


@app.route('/user/checkout', methods=['GET', 'POST', 'PUT'])
def user_checkout():
    """Checkout list operations."""
    if request.method == 'GET':
        select_data = {
            'services_balance': ['user.id', 'user.name', 'service.name', 'amount']}
        join_data = {'service': 'service.id=services_balance.service',
                     'user': 'user.id=services_balance.user'}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data)
        return render_db_template(data=data)
    return 'user_checkout_endpoint'


@app.get('/fitness_center')
def fitness_centers():
    """Info for all fitness centers."""
    select_data = {'fitness_center': ['id', 'address', 'name', 'contacts']}
    data = exec_db_query(single=False, select_data=select_data)
    return render_db_template(data=data)


@app.get('/fitness_center/<int:fc_id>')
def fitness_center(fc_id):
    """Certain fitness center info."""
    select_data = {'fitness_center': ['id', 'address', 'name', 'contacts']}
    where_data = {'id': fc_id}
    data = exec_db_query(single=True, select_data=select_data, where_data=where_data)
    return render_db_template(data=data)


@app.get('/fitness_center/<int:fc_id>/trainer')
def fitness_center_trainers(fc_id):
    """Trainers info for certain fitness centers."""
    select_data = {'trainer': ['fitness_center.name', 'trainer.name', 'trainer.age', 'trainer.sex']}
    join_data = {'fitness_center': 'fitness_center.id=trainer.fitness_center'}
    where_data = {'fitness_center.id': fc_id}
    data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
    return render_db_template(data=data)


@app.get('/fitness_center/<int:fc_id>/trainer/<int:trainer_id>')
def fitness_center_trainer(fc_id, trainer_id):
    """Certain trainer info."""
    select_data = {'trainer': ['fitness_center.name', 'trainer.name', 'trainer.age', 'trainer.sex']}
    join_data = {'fitness_center': 'fitness_center.id=trainer.fitness_center'}
    where_data = {'fitness_center.id': fc_id, 'trainer.id': trainer_id}
    data = exec_db_query(single=True, select_data=select_data, join_data=join_data, where_data=where_data)
    return render_db_template(data=data)


@app.route('/fitness_center/<int:fc_id>/trainer/<int:trainer_id>/rating',
           methods=['GET', 'POST', 'PUT'])
def fitness_center_trainer_rating(fc_id, trainer_id):
    """Trainer rating operations."""
    if request.method == 'GET':
        select_data = {'rating': ['trainer.name', 'rating.points', 'rating.text', 'user.name']}
        join_data = {'user': 'user.id=rating.user', 'trainer': 'trainer.id=rating.trainer'}
        where_data = {'trainer.fitness_center': fc_id, 'trainer.id': trainer_id}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data,
                             join_type='left join')
        return render_template('rating.html', result=data, fc_id=fc_id, trainer_id=trainer_id)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        # now we need to use some hardcode cause still no functional how to do log in and use current user id
        user_id = 3
        insert_data = {'rating': {'trainer': trainer_id, 'user': user_id, 'points': form_dict['points'],
                                  'text': form_dict['text']}}
        exec_db_query(insert_data=insert_data)
        return render_template('congratulation.html', text='Rating was added',
                               return_page=f'/fitness_center/{fc_id}/trainer/{trainer_id}/rating')
    return f'fitness_center "{fc_id}" trainer "{trainer_id}" rating endpoint'


@app.get('/fitness_center/<int:fc_id>/services')
def fitness_center_services(fc_id):
    """Services for certain fitness center."""
    select_data = {
        'service': ['service.name', 'service.description', 'service.duration', 'service.price', 'fitness_center.name']}
    join_data = {'fitness_center': 'fitness_center.id=service.fitness_center'}
    where_data = {'service.fitness_center': fc_id}
    data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
    return render_db_template(data=data)


@app.get('/fitness_center/<int:fc_id>/services/<int:service_id>')
def fitness_center_service(fc_id, service_id):
    """Certain service info."""
    select_data = {
        'service': ['service.name', 'service.description', 'service.duration', 'service.price', 'fitness_center.name']}
    join_data = {'fitness_center': 'fitness_center.id=service.fitness_center'}
    where_data = {'service.fitness_center': fc_id, 'service.id': service_id}
    data = exec_db_query(single=True, select_data=select_data, join_data=join_data, where_data=where_data)
    return render_db_template(data=data)


@app.get('/register')
def register_get():
    """Registration info."""
    return render_template('register.html')


@app.post('/register')
def register_post():
    """Do registration."""
    form_dict = request.form.to_dict()
    insert_data = {'user': {'name': form_dict['name'], 'login': form_dict['login'], 'password': form_dict['password'],
                            'birth_date': form_dict['birth_date'], 'phone': form_dict['phone']}}
    exec_db_query(insert_data=insert_data)
    return render_template('congratulation.html', text='New user account was created', return_page='/login')


@app.get('/fitness_center/<int:fc_id>/loyalty_programs')
def fitness_center_loyalty(fc_id):
    """Loyalty program."""
    return f'fitness_center "{fc_id}" loyalty endpoint'


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080
    app.run(host=host, port=port, debug=True)
