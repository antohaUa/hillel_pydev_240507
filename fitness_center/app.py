"""Fitness center application."""
import datetime as dt
from functools import wraps
from itertools import groupby

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session)

from db_utils import exec_db_query
from private_data import KEY

app = Flask(__name__)

app.secret_key = KEY
delta = 15  # 15 min delta to divide schedule according services duration into slots


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


def get_trainer_free_slots(date_str, service_id, trainer_id):
    """Get trainer free slots for certain date and certain service."""
    # trainer schedule
    select_data = {'trainer_schedule': ['start_time', 'end_time']}
    where_data = {'date': date_str, 'trainer': trainer_id}
    schedule_data = exec_db_query(single=True, select_data=select_data, where_data=where_data)

    # trainer capacity
    select_data = {'trainer_capacity': ['service', 'max_attendees']}
    where_data = {'trainer': trainer_id}
    capacity_data = exec_db_query(single=False, select_data=select_data, where_data=where_data)

    # reservations
    select_data = {'reservation': ['reservation.time', 'service.duration', 'service.id']}
    join_data = {'service': 'service.id=reservation.service'}
    where_data = {'reservation.date': date_str, 'reservation.trainer': trainer_id}
    reservation_data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)

    # service duration
    select_data = {'service': ['duration']}
    where_data = {'id': service_id}
    service_data = exec_db_query(single=True, select_data=select_data, where_data=where_data)

    # fill time slots according trainer schedule and time delta
    time_slots = []
    curr_time = dt.datetime.strptime(schedule_data['start_time'], '%H-%M')
    end_time = dt.datetime.strptime(schedule_data['end_time'], '%H-%M')
    while curr_time < end_time:
        time_slots.append(curr_time)
        curr_time += dt.timedelta(minutes=delta)

    # for not yet reserved slots we make assumption that as minimum one reservation possible
    max_capacity = [1] * len(time_slots)
    attendees = [0] * len(time_slots)
    for curr_r in reservation_data:
        r_start_time = dt.datetime.strptime(curr_r['reservation.time'], '%H-%M')
        slots_num = int(curr_r['service.duration'] / delta)
        idx = time_slots.index(r_start_time)
        for i in range(idx, idx + slots_num):
            # we can't do reservation for slots used already by other services
            if curr_r['service.id'] != service_id:
                max_capacity[i] = 0
            else:
                attendees[i] += 1
                capacity_filter = [el['max_attendees'] for el in capacity_data if el['service'] == curr_r['service.id']]
                max_capacity[i] = capacity_filter[0]

    # free slots -> max_attendees - attendees > 0
    allowed_attendees = [max_capacity[idx] - attendees[idx] for idx, _ in enumerate(time_slots)]

    # we need to exclude time if service does not fit certain slots group by duration
    # for example we can't reserve 17-30 -> 17-45 -> 18-00 ( end time) if service duration = 45 min
    z_num = service_data['duration'] / delta - 1  # num of slots to be zeroed
    tmp = [list(group) for k, group in groupby(allowed_attendees, lambda x: x == 0)]
    result = [lst[i] if len(lst) > z_num and i <= len(lst) - z_num - 1 else 0 for lst in tmp for i, _ in enumerate(lst)]

    # final result that we will convert to json
    free_slots = [time_val.strftime('%H-%M') for idx, time_val in enumerate(time_slots) if result[idx] != 0]
    return free_slots


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


@app.route('/user/pre_reservation', methods=['POST'])
@auth
def user_pre_reservations():
    """Check free slot select endpoint."""
    form_dict = request.form.to_dict()
    free_slots = get_trainer_free_slots(date_str=form_dict['date'], service_id=int(form_dict['service']),
                                        trainer_id=int(form_dict['trainer']))
    return render_template('pre_reservation.html', form_data=form_dict, free_slots=free_slots)


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
        return render_template('reservations.html', result=data)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        insert_data = {
            'reservation': {'trainer': form_dict['trainer'], 'user': session.get('user_id'),
                            'service': form_dict['service'], 'date': form_dict['date'],
                            'time': form_dict['start_time']}}
        exec_db_query(insert_data=insert_data)
        return render_template('congratulation.html', text='New reservation created', return_page='/user/reservations')


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

    # service selection for reservation
    select_data = {'trainer_capacity': ['service.name', 'service.id']}
    join_data = {'service': 'service.id=trainer_capacity.service', 'trainer': 'trainer.id=trainer_capacity.trainer'}
    where_data = {'trainer_capacity.trainer': trainer_id, 'trainer.fitness_center': fc_id}
    service_data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
    return render_template('trainer.html', result=data, service=service_data, trainer=trainer_id)


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

    # trainer selection for reservation
    select_data = {'trainer_capacity': ['trainer.name', 'trainer.id']}
    join_data = {'trainer': 'trainer.id=trainer_capacity.trainer'}
    where_data = {'trainer_capacity.service': service_id, 'trainer.fitness_center': fc_id}
    trainer_data = exec_db_query(single=False, select_data=select_data, join_data=join_data, where_data=where_data)
    return render_template('service.html', result=data, trainer=trainer_data, service=service_id)


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
