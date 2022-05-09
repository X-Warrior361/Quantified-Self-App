from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Tracker, Options, Log
from . import db
from .helpers import calculate_days, create_graph, get_value
from datetime import datetime, date as dt
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask_sqlalchemy import SQLAlchemy

''' app = Flask()
app.config['Database_Uri] = '//sqlite3/project.sqlite3'
db = SQLAlchemy()
db.init_app(app)'''

views = Blueprint('views', __name__, url_prefix='/')


@views.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Registration for new user
@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        name = request.form["user"]
        if len(request.form["password"]) <= 5:
            return render_template('register.html', error={'message': 'Password too short'})
        password = generate_password_hash(request.form["password"])         # Using hash to secure password

        if not bool(User.query.filter_by(name=name).first()):   # Checks if there is a user with the same name
            user = User()
            user.name = name
            user.password = password
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            user = User.query.filter_by(name=name).first()
            return redirect('/dashboard/{}'.format(user.id))

        return render_template('register.html', error={'message': 'User already registered'})

    return render_template('register.html')


@views.route('/login', methods=["POST"])
def login():
    name = request.form['name']
    user = User.query.filter_by(name=name).first()
    if user:
        password = request.form["password"]
        if check_password_hash(user.password, password):            # Validation of password through hash
            login_user(user, remember=True)
            return redirect('/dashboard/{}'.format(user.id))
        return render_template('index.html', error={'message': 'Incorrect Password'})

    return render_template('index.html', error={'message': "Username doesn't exist"})


@views.route('edit/<u_id>', methods=["GET", "POST"])
@login_required
def edit_user(u_id):
    user = User.query.filter_by(id=u_id).first()
    if request.method == "GET":
        return render_template('edit_user.html', user=user)

    elif request.method == "POST":
        name = request.form["user"]
        if len(request.form["password"]) <= 5:
            return render_template('edit_user.html', user=user, error={'message': 'Password too short'})
        password = generate_password_hash(request.form["password"])         # Using hash to secure password

        old_user = User.query.filter_by(name=name).first()
        if not old_user or old_user.id == int(u_id):   # Checks if there is a user with the same name
            user.name = name
            user.password = password
            db.session.commit()
            return redirect('/dashboard/{}'.format(user.id))

        return render_template('edit_user.html', error={'message': 'User already registered'}, user=user)


@views.route('/delete/<u_id>', methods=["GET"])
@login_required
def delete_user(u_id):
    user = User.query.filter_by(id=u_id).first()
    trackers = Tracker.query.filter_by(user_id=u_id).all()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.id))
    for tracker in trackers:
        if tracker.type == "mcq" or tracker.type == "bool":
            options = Options.query.filter_by(tracker_id=tracker.id).all()  # Deleting all the options before deleting the tracker
            for opt in options:
                db.session.delete(opt)

    db.session.delete(user)
    db.session.commit()

    return redirect('/dashboard/{}'.format(user.id))


@views.route('/dashboard/<u_id>', methods=["GET"])
@login_required
def dashboard(u_id):
    user = User.query.filter_by(id=u_id).first()
    if user != current_user:                                        # Checks if the user logged in is the correct user
        return redirect('/dashboard/{}'.format(current_user.id))
    trackers = Tracker.query.filter_by(user_id=user.id).all()       # Getting all the trackers of the user
    logs = []
    for tracker in trackers:
        log = Log.query.filter_by(tracker_id=tracker.id).order_by(Log.id.desc()).first()    # Getting the last log
        if log:
            value = get_value(log)
            dat = dt.today() - log.last.date()
            logs.append((tracker, calculate_days(dat.days), value))            # Calculating days since last log
        else:
            logs.append((tracker, 'Not Logged yet', 'None'))
    return render_template('dashboard.html', user=user, tracker=logs)

  
@views.route('/tracker/<u_id>/create', methods=["GET", "POST"])
@login_required
def add_tracker(u_id):
    user = User.query.filter_by(id=u_id).first()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.id))
    if request.method == 'GET':
        return render_template('tracker_create.html', user=user)
    elif request.method == 'POST':
        tracker = Tracker()
        tracker.name = request.form['name'].strip().title()
        tracker.description = request.form['description']
        tracker.type = request.form['type']
        tracker.user_id = user.id
        temp = Tracker.query.filter_by(name=tracker.name).first()     # Checks if there is a tracker with the same name
        if not temp:
            db.session.add(tracker)
            db.session.commit()
        else:
            return render_template('tracker_create.html', user=user, error='A tracker with the same name exists')

        if tracker.type == 'mcq':
            temp = Tracker.query.filter_by(name=tracker.name).first()
            names = list(map(str, request.form['options'].strip().split(',')))

            for n in names:
                opt = Options()                     # Adding options for multiple choice
                opt.name = n
                opt.tracker_id = temp.id
                db.session.add(opt)
            db.session.commit()

        elif tracker.type == 'bool':
            temp = Tracker.query.filter_by(name=tracker.name).first()
            names = [request.form['bool_1'], request.form['bool_2']]

            for n in names:
                opt = Options()                     # Adding options for bool
                opt.name = n
                opt.tracker_id = temp.id
                db.session.add(opt)
            db.session.commit()

    return redirect('/dashboard/{}'.format(user.id))


@views.route('/tracker/<t_id>/update', methods=["GET", "POST"])
@login_required
def update_tracker(t_id):
    tracker = Tracker.query.filter_by(id=t_id).first()
    user = User.query.filter_by(id=tracker.user_id).first()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.id))

    if request.method == "GET":
        if tracker.type == "mcq":
            options = Options.query.filter_by(tracker_id=t_id).all()
            return render_template('tracker_update.html', tracker=tracker, mcq=True, options=options)
        elif tracker.type == "bool":
            options = Options.query.filter_by(tracker_id=t_id).all()
            return render_template('tracker_update.html', tracker=tracker, bool=True, options=options)
        else:
            return render_template('tracker_update.html', tracker=tracker)

    elif request.method == 'POST':
        name = request.form['name'].strip()
        temp = Tracker.query.filter_by(name=name).first()
        if temp != tracker and temp is not None:    # Checks if there is a tracker with the same name
            if tracker.type == "mcq":
                options = Options.query.filter_by(tracker_id=t_id).all()
                return render_template('tracker_update.html', tracker=tracker, mcq=True, options=options,
                                       error="A tracker with same name already exists")
            elif tracker.type == "bool":
                options = Options.query.filter_by(tracker_id=t_id).all()
                return render_template('tracker_update.html', tracker=tracker, bool=True, options=options,
                                       error="A tracker with same name already exists")
            else:
                return render_template('tracker_update.html', tracker=tracker,
                                       error="A tracker with same name already exists")

        tracker.name = name
        tracker.description = request.form['description']
        if tracker.type == "mcq":
            total = Options.query.filter_by(tracker_id=t_id).all()
            for t in total:
                t.name = request.form["{}".format(t.id)]

            names = list(map(str, request.form['new'].strip().split(',')))      # Adding New Options
            for n in names:
                if n == '':
                    break
                opt = Options()
                opt.name = n
                opt.tracker_id = tracker.id
                db.session.add(opt)

        elif tracker.type == "bool":
            total = Options.query.filter_by(tracker_id=t_id).all()
            for t in total:
                t.name = request.form["{}".format(t.id)]

        db.session.commit()
        return redirect('/dashboard/{}'.format(user.id))


@views.route('/tracker/<t_id>/delete', methods=["GET"])
@login_required
def delete_tracker(t_id):
    tracker = Tracker.query.filter_by(id=t_id).first()
    user = User.query.filter_by(id=tracker.user_id).first()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.id))
    if tracker.type == "mcq" or tracker.type=="bool":
        options = Options.query.filter_by(tracker_id=t_id).all()  # Deleting all the options before deleting the tracker
        for opt in options:
            db.session.delete(opt)

    db.session.delete(tracker)
    db.session.commit()

    return redirect('/dashboard/{}'.format(user.id))


@views.route('/tracker/<u_id>/<t_id>/view', methods=["GET"])
@login_required
def view_tracker(u_id, t_id):
    user = User.query.filter_by(id=u_id).first()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.id))
    tracker = Tracker.query.filter_by(id=t_id, user_id=user.id).first()
    logs = Log.query.filter_by(tracker_id=tracker.id).order_by(Log.time_stamp).all() # Ordering by time stamp
    options = Options.query.filter_by(tracker_id=tracker.id).all()
    if logs:
        create_graph(tracker, logs, options)                # Creates Graph of the logs

    if tracker.type == 'bool':                              # Creating context differently for bool type trackers
        opt = []
        for log in logs:
            log.time_stamp = datetime.strptime(str(log.time_stamp), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
            dat = dt.today() - log.last.date()
            if log.value_bool:
                opt.append((log, options[0].name, calculate_days(dat.days)))
            else:
                opt.append((log, options[1].name, calculate_days(dat.days)))

        return render_template('track_view.html', logs=logs, tracker=tracker, user=user, opt=opt, bool=True)

    log = []
    for l in logs:
        l.time_stamp = datetime.strptime(str(l.time_stamp), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
        dat = dt.today() - l.last.date()
        log.append((l, calculate_days(dat.days)))

    return render_template('track_view.html', logs=log, tracker=tracker, user=user)


@views.route('/log/<u_id>/<t_id>/<prev>/add', methods=["GET", "POST"])
@login_required
def add_log(u_id, t_id, prev):
    user = User.query.filter_by(id=u_id).first()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.id))
    tracker = Tracker.query.filter_by(id=t_id, user_id=user.id).first()
    options = Options.query.filter_by(tracker_id=tracker.id).all()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temp = stamp[:-3].split()
    stamp = temp[0] + 'T' + temp[1]
    if request.method == "GET":
        return render_template('log_add.html', user=user, tracker=tracker, type=tracker.type, options=options,
                               prev=prev, stamp=stamp)

    elif request.method == "POST":
        log = Log()
        date = re.split('-|T|:', request.form['when'])      # Splitting the date and time
        log.time_stamp = datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]))
        # Checking if the date is in the past or not
        if log.time_stamp > datetime.now():
            return render_template('log_add.html', user=user, tracker=tracker, type=tracker.type, options=options,
                                   error="The date and time is in the future")

        log.note = request.form['notes']
        log.tracker_id = tracker.id
        if tracker.type == 'num':
            log.value_num = request.form['value']
        elif tracker.type == 'mcq':
            options = Options.query.filter_by(id=int(request.form['value'])).first()
            log.value_mcq = options.name.strip()
        elif tracker.type == 'time':
            log.value_time = request.form['hours'] + ':' + request.form['minutes'] + ':' + request.form['seconds']
        else:
            if request.form['value'] == '1':
                log.value_bool = True
            else:
                log.value_bool = False

        db.session.add(log)
        db.session.commit()
        if prev == "dash":
            return redirect('/dashboard/{}'.format(user.id))
        else:
            return redirect('/tracker/{}/{}/view'.format(u_id, t_id))


@views.route('/log/<l_id>/delete', methods=["GET"])
@login_required
def delete_log(l_id):
    log = Log.query.filter_by(id=l_id).first()
    tracker = Tracker.query.filter_by(id=log.tracker_id).first()
    user = User.query.filter_by(id=tracker.user_id).first()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.id))

    db.session.delete(log)
    db.session.commit()
    return redirect('/tracker/{}/{}/view'.format(user.id, tracker.id))


@views.route('/log/<l_id>/update', methods=["GET", "POST"])
@login_required
def update_log(l_id):
    log = Log.query.filter_by(id=l_id).first()
    tracker = Tracker.query.filter_by(id=log.tracker_id).first()
    options = Options.query.filter_by(tracker_id=tracker.id).all()
    user = User.query.filter_by(id=tracker.user_id).first()
    if user != current_user:
        return redirect('/dashboard/{}'.format(current_user.name))

    if request.method == "GET":
        stamp = str(log.time_stamp)
        temp = stamp[:-3].split()
        stamp = temp[0] + 'T' + temp[1]
        if tracker.type == 'time':
            time = log.value_time.split(':')
            return render_template('log_update.html', log=log, user=user, tracker=tracker, time=time, stamp=stamp)
        elif tracker.type == 'bool':
            return render_template('log_update.html', log=log, user=user, tracker=tracker, stamp=stamp, bool=True,
                                   options=options)

        return render_template('log_update.html', log=log, user=user, tracker=tracker, stamp=stamp, options=options)

    elif request.method == "POST":
        date = re.split('-|T|:', request.form['when'])
        log.time_stamp = datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]))
        if log.time_stamp > datetime.now():
            return render_template('log_add.html', user=user, tracker=tracker, type=tracker.type, options=options,
                                   error="The date and time is in the future")

        log.note = request.form['notes']
        if tracker.type == 'num':
            log.value_num = request.form['value']
        elif tracker.type == 'mcq':
            options = Options.query.filter_by(id=int(request.form['value'])).first()
            log.value_mcq = options.name.strip()
        elif tracker.type == 'time':
            log.value_time = request.form['hours'] + ':' + request.form['minutes'] + ':' + request.form['seconds']
        else:
            if request.form['value'] == '1':
                log.value_bool = True
            else:
                log.value_bool = False

        db.session.commit()
    return redirect('/tracker/{}/{}/view'.format(user.id, tracker.id))


@views.route('/logout')                     # For logging out the user
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.index'))
