"""Fitness center application."""
import datetime as dt
from functools import wraps
from itertools import groupby

from flask import Flask, flash, redirect, render_template, request, session

import db_model
from db_orm import Db
from private_data import KEY
from utils import send_email

app = Flask(__name__, template_folder='templates')

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


def convert_db_query_data(query_data):
    """Convert query row/rows data to dict or list of dicts."""
    if query_data is None:
        return {}
    elif type(query_data) is list:
        return [el._asdict() for el in query_data]
    return query_data._asdict()


def get_trainer_free_slots(date_str, service_id, trainer_id):
    """Get trainer free slots for certain date and certain service."""
    # trainer schedule
    db = Db()
    columns = (db_model.TrainerSchedule.start_time, db_model.TrainerSchedule.end_time)
    data = db.session.query(*columns).filter(db_model.TrainerSchedule.date == date_str,
                                             db_model.TrainerSchedule.trainer == trainer_id).first()
    schedule_data = convert_db_query_data(data)

    # trainer capacity
    columns = (db_model.TrainerCapacity.service, db_model.TrainerCapacity.max_attendees)
    data = db.session.query(*columns).filter(db_model.TrainerCapacity.trainer == trainer_id).all()
    capacity_data = convert_db_query_data(data)

    # reservations
    columns = (db_model.Reservation.time.label('reservation.time'),
               db_model.Service.duration.label('service.duration'),
               db_model.Service.id.label('service.id'))
    data = db.session.query(*columns).join(db_model.Service).filter(db_model.Reservation.date == date_str,
                                                                    db_model.Reservation.trainer == trainer_id).all()
    reservation_data = convert_db_query_data(data)

    # service duration
    data = db.session.query(db_model.Service.duration).filter(db_model.Service.id == service_id).first()
    service_data = convert_db_query_data(data)

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


@app.get('/')
def start():
    """Start page."""
    return redirect('/fitness_center')


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
        db = Db()
        data = db.session.query(db_model.User).filter_by(login=form_dict['login']).first()
        if data.password == form_dict['password']:
            session['user_id'] = data.id
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
        db = Db()
        columns = (db_model.User.name, db_model.User.login, db_model.User.birth_date,
                   db_model.User.phone, db_model.User.email)
        data = db.session.query(*columns).filter_by(id=session.get('user_id')).first()
        return render_template('user.html', result=convert_db_query_data(data))
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        db = Db()
        (db.session.query(db_model.User).filter(db_model.User.id == session.get('user_id')).update(
            {'name': form_dict.get('name'), 'login': form_dict.get('login'), 'birth_date': form_dict.get('birth_date'),
             'phone': form_dict.get('phone'), 'email': form_dict.get('email')}))
        db.session.commit()
        return render_template('congratulation.html', text='User data updated', return_page='/user')


@app.route('/user/funds', methods=['GET', 'POST'])
@auth
def user_funds():
    """Funds operations for certain user."""
    if request.method == 'GET':
        db = Db()
        data = db.session.query(db_model.User.id, db_model.User.name, db_model.User.funds).filter_by(
            id=session.get('user_id')).first()
        return render_template('user_funds.html', result=convert_db_query_data(data))
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
        db = Db()
        columns = (db_model.Reservation.id, db_model.Reservation.date, db_model.Reservation.time,
                   db_model.Trainer.name.label('trainer.name'),
                   db_model.Service.name.label('service.name'),
                   db_model.User.name.label('user.name'))
        data = (db.session.query(*columns).join(db_model.User).join(db_model.Service).join(db_model.Trainer)).filter(
            db_model.User.id == session.get('user_id')).all()
        return render_template('reservations.html', result=convert_db_query_data(data))
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        db = Db()
        new_reservation = db_model.Reservation(trainer=form_dict['trainer'], user=session.get('user_id'),
                                               service=form_dict['service'], date=form_dict['date'],
                                               time=form_dict['start_time'])
        db.session.add(new_reservation)
        db.session.commit()
        return render_template('congratulation.html', text='New reservation created', return_page='/user/reservations')


@app.route('/user/reservations/<int:reservation_id>', methods=['GET', 'POST'])
@auth
def user_reservation(reservation_id):
    """Show/modify with certain reservation."""
    if request.method == 'GET':
        db = Db()
        columns = (db_model.Reservation.id, db_model.Reservation.date, db_model.Reservation.time,
                   db_model.Trainer.name.label('trainer.name'),
                   db_model.Service.name.label('service.name'),
                   db_model.User.name.label('user.name'))
        data = (db.session.query(*columns).join(db_model.User).join(db_model.Service).join(db_model.Trainer)).filter(
            db_model.User.id == session.get('user_id'), db_model.Reservation.id == reservation_id).first()
        return render_template('reservation.html', result=convert_db_query_data(data))
    return f'user reservation "{reservation_id}" endpoint'


@app.route('/user/reservations/<int:reservation_id>/delete', methods=['GET'])
@auth
def user_reservation_delete(reservation_id):
    """Delete certain reservation."""
    if request.method == 'GET':
        db = Db()
        db.session.query(db_model.Reservation).filter_by(id=reservation_id, user=session.get('user_id')).delete()
        db.session.commit()
        return redirect('/user/reservations')


@app.route('/user/checkout', methods=['GET', 'POST'])
@auth
def user_checkout():
    """Checkout list operations."""
    if request.method == 'GET':
        db = Db()
        columns = (db_model.User.id, db_model.User.name,
                   db_model.Service.name.label('service.name'),
                   db_model.ServicesBalance.amount)
        data = (db.session.query(*columns).join(db_model.User).join(db_model.Service)).filter(
            db_model.User.id == session.get('user_id')).all()
        return render_template('user_checkout.html', result=convert_db_query_data(data))
    if request.method == 'POST':
        return 'user_checkout_endpoint'


@app.get('/fitness_center')
def fitness_centers():
    """Info for all fitness centers."""
    db = Db()
    columns = (db_model.FitnessCenter.id, db_model.FitnessCenter.address,
               db_model.FitnessCenter.name, db_model.FitnessCenter.contacts)
    data = db.session.query(*columns).all()
    return render_template('fitness_centers.html', result=convert_db_query_data(data))


@app.get('/fitness_center/<int:fc_id>')
def fitness_center(fc_id):
    """Certain fitness center info."""
    db = Db()
    columns = (db_model.FitnessCenter.id, db_model.FitnessCenter.address,
               db_model.FitnessCenter.name, db_model.FitnessCenter.contacts)
    data = db.session.query(*columns).filter_by(id=fc_id).first()
    return render_template('fitness_center.html', result=convert_db_query_data(data), fc_id=fc_id)


@app.get('/fitness_center/<int:fc_id>/trainer')
def fitness_center_trainers(fc_id):
    """Trainers info for certain fitness centers."""
    db = Db()
    columns = (db_model.Trainer.id.label('trainer.id'),
               db_model.FitnessCenter.name.label('fitness_center.name'),
               db_model.Trainer.name.label('trainer.name'),
               db_model.Trainer.age.label('trainer.age'),
               db_model.Trainer.sex.label('trainer.sex'))
    data = (db.session.query(*columns).join(db_model.FitnessCenter)).filter(
        db_model.Trainer.fitness_center == fc_id).all()
    return render_template('trainers.html', result=convert_db_query_data(data), fc_id=fc_id)


@app.get('/fitness_center/<int:fc_id>/trainer/<int:trainer_id>')
def fitness_center_trainer(fc_id, trainer_id):
    """Certain trainer info."""
    db = Db()
    columns = (db_model.FitnessCenter.name.label('fitness_center.name'),
               db_model.Trainer.name.label('trainer.name'),
               db_model.Trainer.age.label('trainer.age'),
               db_model.Trainer.sex.label('trainer.sex'))
    data = (db.session.query(*columns).join(db_model.FitnessCenter)).filter(
        db_model.Trainer.fitness_center == fc_id, db_model.Trainer.id).first()

    # service selection for reservation
    columns = (db_model.TrainerCapacity.service.label('service.id'),
               db_model.Service.name.label('service.name'))
    service_data = (db.session.query(*columns).join(db_model.Service).join(db_model.Trainer)).filter(
        db_model.TrainerCapacity.trainer == trainer_id, db_model.Trainer.fitness_center == fc_id).all()

    return render_template('trainer.html', result=convert_db_query_data(data),
                           service=convert_db_query_data(service_data), trainer=trainer_id, fc_id=fc_id)


@app.route('/fitness_center/<int:fc_id>/trainer/<int:trainer_id>/rating', methods=['GET', 'POST'])
@auth
def fitness_center_trainer_rating(fc_id, trainer_id):
    """Trainer rating operations."""
    if request.method == 'GET':
        db = Db()
        columns = (db_model.Rating.points.label('rating.points'),
                   db_model.Trainer.name.label('trainer.name'),
                   db_model.Rating.text.label('rating.text'),
                   db_model.User.name.label('user.name'),
                   db_model.User.id.label('user.id'))
        rows_data = (db.session.query(*columns)
                     .join(db_model.User, db_model.User.id == db_model.Rating.user, isouter=True)
                     .join(db_model.Trainer, db_model.Trainer.id == db_model.Rating.trainer, isouter=True)
                     .filter(db_model.Trainer.fitness_center == fc_id, db_model.Trainer.id == trainer_id)).all()
        data = convert_db_query_data(rows_data)

        # default values
        rating_values = {'points': 100, 'text': '', 'fc_id': fc_id, 'trainer_id': trainer_id}
        # if rating record from current user exist in db we change defaults to values from db
        if curr_user_rating := [el for el in data if el['user.id'] == session.get('user_id')]:
            rating_values['points'] = curr_user_rating[0]['rating.points']
            rating_values['text'] = curr_user_rating[0]['rating.text']
        return render_template('rating.html', result=data, defaults=rating_values, fc_id=fc_id)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        db = Db()
        columns = (db_model.Rating.id.label('rating.id'), db_model.User.id.label('user.id'))
        rows_data = (db.session.query(*columns)
                     .join(db_model.User, db_model.User.id == db_model.Rating.user, isouter=True)
                     .join(db_model.Trainer, db_model.Trainer.id == db_model.Rating.trainer, isouter=True)
                     .filter(db_model.Trainer.fitness_center == fc_id, db_model.Trainer.id == trainer_id,
                             db_model.User.id == session.get('user_id'))).all()
        select_data = convert_db_query_data(rows_data)

        # if rating record exists do update , if not exists -> insert
        if select_data:
            (db.session.query(db_model.Rating)
             .filter(db_model.Rating.trainer == trainer_id, db_model.Rating.user == session.get('user_id'))
             .update({'trainer': trainer_id, 'user': session.get('user_id'), 'points': form_dict['points'],
                      'text': form_dict['text']}))
            db.session.commit()
        else:
            new_rating = db_model.Rating(trainer=trainer_id, user=session.get('user_id'),
                                         points=form_dict['points'], text=form_dict['text'])
            db.session.add(new_rating)
            db.session.commit()
        return render_template('congratulation.html', text='Rating was added',
                               return_page=f'/fitness_center/{fc_id}/trainer/{trainer_id}/rating')


@app.get('/fitness_center/<int:fc_id>/services')
def fitness_center_services(fc_id):
    """Services for certain fitness center."""
    db = Db()
    columns = (db_model.Service.id.label('service.id'),
               db_model.Service.name.label('service.name'),
               db_model.Service.description, db_model.Service.duration, db_model.Service.price,
               db_model.FitnessCenter.name.label('fitness_center.name'))
    data = (db.session.query(*columns).join(db_model.FitnessCenter)).filter(
        db_model.Service.fitness_center == fc_id).all()
    return render_template('services.html', result=convert_db_query_data(data), fc_id=fc_id)


@app.get('/fitness_center/<int:fc_id>/services/<int:service_id>')
def fitness_center_service(fc_id, service_id):
    """Certain service info."""
    db = Db()
    columns = (db_model.Service.name.label('service.name'),
               db_model.Service.description, db_model.Service.duration, db_model.Service.price,
               db_model.FitnessCenter.name.label('fitness_center.name'))
    data = (db.session.query(*columns).join(db_model.FitnessCenter)).filter(
        db_model.Service.fitness_center == fc_id, db_model.Service.id == service_id).first()

    # trainer selection for reservation
    columns = (db_model.TrainerCapacity.trainer.label('trainer.id'),
               db_model.Trainer.name.label('trainer.name'))
    trainer_data = (db.session.query(*columns).join(db_model.Trainer)).filter(
        db_model.TrainerCapacity.service == service_id, db_model.Trainer.fitness_center == fc_id).all()
    return render_template('service.html', result=convert_db_query_data(data),
                           trainer=convert_db_query_data(trainer_data), service=service_id, fc_id=fc_id)


@app.get('/register')
def register_get():
    """Registration info."""
    return render_template('register.html')


@app.post('/register')
def register_post():
    """Do registration."""
    try:
        form_dict = request.form.to_dict()
        email = form_dict.get('email')
        db = Db()
        user_exists = db.session.query(db_model.User).filter(db_model.User.login == form_dict['login']).first()
        if user_exists is None:
            new_user = db_model.User(name=form_dict['name'], login=form_dict['login'], password=form_dict['password'],
                                     birth_date=form_dict['birth_date'], phone=form_dict['phone'], email=form_dict['email'])
            db.session.add(new_user)
            db.session.commit()
            if email:
                subject = 'Registration completed successfully!'
                text = '\nSuccessful registration in our fitness center.'
                send_email.delay(email, subject, text)
            return render_template('congratulation.html', text='New user account was created', return_page='/login')
        return render_template('register.html', err='Error: login already exists')
    except Exception as g_exc:
        return render_template('register.html', err=g_exc)


@app.get('/fitness_center/<int:fc_id>/loyalty_programs')
def fitness_center_loyalty(fc_id):
    """Loyalty program."""
    return f'fitness_center "{fc_id}" loyalty endpoint'


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8080
    app.run(host=host, port=port, debug=True)
