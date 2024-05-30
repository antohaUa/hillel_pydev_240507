"""Fitness center application."""
from functools import wraps

from db_utils import exec_db_query
from flask import Flask, flash, redirect, render_template, request, session

app = Flask(__name__)

app.secret_key = b'242gdf$$@#{]\xecghTD11'


def auth(func):
    """Auth decorator."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return func(*args, **kwargs)

    return wrapper


def render_db_template(data):
    """Render common html template according single or multiple returned db rows data."""
    # for multiline data we receive list structure
    template_name = 'db_data_multiple.html' if type(data) is list else 'db_data_single.html'
    return render_template(template_name, result=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login."""
    if request.method == 'GET':
        if session.get('user_id'):
            return redirect('/user')
        return render_template('login.html')
    elif request.method == 'POST':
        form_dict = request.form.to_dict()
        form_login = form_dict['login']
        form_password = form_dict['password']
        select_data = {'user': ['id', 'login', 'password']}
        where_data = {'login': form_login}
        data = exec_db_query(single=True, select_data=select_data, where_data=where_data)
        if data.get('password') == form_password:
            session['user_id'] = data.get('id')
            return redirect('/user')
        flash('Login unsuccessful. Please check your username and password.', 'error')
        app.logger.warning(f'{form_login} failed to log in')
    return redirect('/login')


@app.get('/logout')
@auth
def logout():
    """Logout."""
    session.pop('user_id', None)
    return redirect('/login')


@app.route('/user', methods=['GET', 'POST'])
@auth
def user():
    """User operations."""
    if request.method == 'GET':
        select_data = {'user': ['id', 'name', 'login', 'password', 'birth_date', 'phone']}
        where_data = {'id': session.get('user_id')}
        data = exec_db_query(single=True, select_data=select_data, where_data=where_data)
        return render_db_template(data=data)
    if request.method == 'POST':
        return 'user edit endpoint'


@app.route('/user/funds', methods=['GET', 'POST'])
@auth
def user_funds():
    """Funds operations for certain user."""
    if request.method == 'GET':
        select_data = {'user': ['name', 'funds']}
        where_data = {'id': session.get('user_id')}
        data = exec_db_query(single=True, select_data=select_data, where_data=where_data)
        return render_db_template(data=data)
    return 'user funds endpoint'


@app.route('/user/reservations', methods=['GET', 'POST'])
@auth
def user_reservations():
    """User operations with reservations."""
    if request.method == 'GET':
        select_data = {
            'reservation': ['reservation.id', 'reservation.date', 'reservation.time',
                            'trainer.name', 'service.name', 'user.name']}
        join_data = {'trainer': 'trainer.id=reservation.trainer',
                     'service': 'service.id=reservation.service',
                     'user': 'user.id=reservation.user'}
        where_data = {'user.id': session.get('user_id')}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
        return render_db_template(data=data)
    return 'user reservations endpoint'


@app.route('/user/reservations/<int:reservation_id>', methods=['GET', 'POST'])
@auth
def user_reservation(reservation_id):
    """Show/modify with certain reservation."""
    if request.method == 'GET':
        select_data = {
            'reservation': ['reservation.id', 'reservation.date', 'reservation.time',
                            'trainer.name', 'service.name', 'user.name']}
        join_data = {'trainer': 'trainer.id=reservation.trainer',
                     'service': 'service.id=reservation.service',
                     'user': 'user.id=reservation.user'}
        where_data = {'reservation.id': reservation_id, 'user.id': session.get('user_id')}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
        return render_db_template(data=data)
    return f'user reservation "{reservation_id}" endpoint'


@app.route('/user/reservations/<int:reservation_id>/delete', methods=['GET'])
@auth
def user_reservation_delete(reservation_id):
    """Delete certain reservation."""
    if request.method == 'GET':
        table_name = 'reservation'
        where_data = {'id': reservation_id, 'user': session.get('user_id')}
        exec_db_query(delete_data=table_name, where_data=where_data)
        return redirect('/user/reservations')


@app.route('/user/checkout', methods=['GET', 'POST'])
@auth
def user_checkout():
    """Checkout list operations."""
    if request.method == 'GET':
        select_data = {
            'services_balance': ['user.id', 'user.name', 'service.name', 'amount']}
        join_data = {'service': 'service.id=services_balance.service',
                     'user': 'user.id=services_balance.user'}
        where_data = {'user.id': session.get('user_id')}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
        return render_db_template(data=data)
    if request.method == 'POST':
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


@app.route('/fitness_center/<int:fc_id>/trainer/<int:trainer_id>/rating', methods=['GET', 'POST'])
@auth
def fitness_center_trainer_rating(fc_id, trainer_id):
    """Trainer rating operations."""
    if request.method == 'GET':
        select_data = {'rating': ['trainer.name', 'rating.points', 'rating.text', 'user.name', 'user.id']}
        join_data = {'user': 'user.id=rating.user', 'trainer': 'trainer.id=rating.trainer'}
        where_data = {'trainer.fitness_center': fc_id, 'trainer.id': trainer_id}
        data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data,
                             join_type='left join')
        # default values
        rating_values = {'points': 100, 'text': '', 'fc_id': fc_id, 'trainer_id': trainer_id}
        # if rating record from current user exist in db we change defaults to values from db
        if curr_user_rating := [el for el in data if el['user.id'] == session.get('user_id')]:
            rating_values['points'] = curr_user_rating[0]['rating.points']
            rating_values['text'] = curr_user_rating[0]['rating.text']
        return render_template('rating.html', result=data, defaults=rating_values)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        select_data = {'rating': ['user.id']}
        join_data = {'user': 'user.id=rating.user', 'trainer': 'trainer.id=rating.trainer'}
        where_data = {'trainer.fitness_center': fc_id, 'trainer.id': trainer_id, 'user.id': session.get('user_id')}
        select_data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data,
                                    join_type='left join')
        rating_data = {'rating': {'trainer': trainer_id, 'user': session.get('user_id'), 'points': form_dict['points'],
                                  'text': form_dict['text']}}
        # if rating record exists do update , if not exists -> insert
        if select_data:
            where_data = {'trainer': trainer_id, 'user': session.get('user_id')}
            exec_db_query(update_data=rating_data, where_data=where_data)
        else:
            exec_db_query(insert_data=rating_data)
        return render_template('congratulation.html', text='Rating was added',
                               return_page=f'/fitness_center/{fc_id}/trainer/{trainer_id}/rating')


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
