from flask import flash, abort, url_for, redirect, render_template, jsonify
from flask_login import current_user, login_required
from .forms import LoginForm, AddPoliceStationForm, RegistrationForm
from ..model import Police, User, Category, CrimeScene
from .. import db
from . import home
from ..PlotData import showmap
from datetime import datetime as dt


@home.route('/', methods=['GET', 'POST'])
def homepage():
    """
    Render the home page on / route
    """
    form = LoginForm()

    # policestations = Police.query.all()
    return render_template('home/index.html', title="welcome",
                           form=form, methods=['GET', 'POST'])

# add admin dashboard view
@home.route('/admin/dashboard')
# @login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
    # if not current_user.is_admin:
    #     abort(403)
    showmap()
    return render_template('home/admin_dashboard.html', title="dashboard")


@home.route('/admin/policestation', methods=['POST', 'GET'])
# @login_required
def police_station_data():
    # if not current_user.is_admin:
    #     abort(403)
    form = AddPoliceStationForm()
    if form.validate_on_submit():
        police_station = Police(StationName=form.StationName.data,
                                division=form.division.data)
        db.session.add(police_station)
        db.session.commit()
        flash("You have successfully added a Police Station.")
    police_stations = Police.query.all()
    return render_template('home/police_index.html',
                           title="PoliceStation",
                           police_stations=police_stations,
                           form=form)


@home.route('/admin/policestation/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_police(id):
    add_police = False
    police = Police.query.get_or_404(id)
    form = AddPoliceStationForm(obj=police)
    if form.validate_on_submit():
        police.StationName = form.StationName.data
        division = form.division.data
        db.session.commit()
        flash('You have successfully edited a police station')
        return redirect(url_for('home.police_station_data'))
    police_stations = Police.query.all()
    return render_template('home/police_index.html',
                           title="PoliceStation",
                           police_stations=police_stations,
                           form=form)


@home.route('/admin/policestation/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_police(id):
    police = Police.query.get_or_404(id)
    db.session.delete(police)
    db.session.commit()
    flash('You have successfully deleted the Police Station.')
    return redirect(url_for('home.police_station_data'))


@home.route('/admin/register_user', methods=['GET', 'POST'])
def register_user():
    """
    Handle requests for to the database through the registration form

    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            full_names=form.full_names.data,
            telephone=form.telephone.data,
            password=form.password.data
        )
        # add employee to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successively registered! You may now login.')

    # redirect to the login page
    return render_template('home/register.html', title="Register User",
                           form=form)


@home.route('/web/PathFinder/v1.0/data/to-day')
def collect_data():
    # datemask = '%m/%d/%Y'
    # today = datetime.datetime.strftime(datetime.datetime.today(),datemask)
    # today_cases = CaseFile.query.filter_by(date_posted = today)

    labels, actual_data = category_crimes_data()
    crimesdata = {
        'labels': labels,
        'data': actual_data
    }
    print('request made.............\n ')
    return jsonify({'crimesdata': crimesdata})


@home.route('/web/PathFinder/v1.0/data/')
def collect_summary_data():
    casesData = {
        'thefty': len(Category.query.filter_by(violet_type='Thefty').first().crimescene),
        'murder': len(Category.query.filter_by(violet_type='murder').first().crimescene),
        'kidnap': len(Category.query.filter_by(violet_type='kidnap').first().crimescene),
        'robbery': len(Category.query.filter_by(violet_type='robbery').first().crimescene)
    }
    return jsonify({'casesData': casesData})

    """
    returns the taple of categories list the count of crimes count
    list
    """


def category_crimes_data():
    crime_categories = []
    crime_categories_count = []
    for category in Category.query.all():
        crime_categories.append(category.violet_type)
        crime_categories_count.append(len(category.crimescene))
    return crime_categories, crime_categories_count


@home.route('/admin/dashboard/crimes/comp_vis/', methods=['GET', 'POST'])
def crime_comparision_view():
    return render_template('home/compare_categories.html', title="Analyze Crime Categories")


@home.route('/categories/data/line', methods=['GET'])
def get_categories_data():
    print('method called....')
    date_mask = '%Y'
    labels = []
    category_datasets = []
    plot_dataset = []
    for category in Category.query.all():
        dataset = {'data': {}, 'label': '', 'borderColor': ''}
        dataset['label'] = category.violet_type
        dataset['borderColor'] = category.category_color
        category_crimes = category.crimescene
        """
        find the crimes count of this category in each year
        """
        # map crimes count to years
        years_data = {}
        for category_crime in category_crimes:
            year_of_analysis = dt.strftime(
                category_crime.date_posted, date_mask)
            years_data[year_of_analysis] = years_data[year_of_analysis] + \
                1 if year_of_analysis in years_data.keys() else 1
        dataset['data'] = years_data
        category_datasets.append(dataset)

    # create labels
    for dataset in category_datasets:
        for year in dataset['data'].keys():
            if year not in labels:
                labels.append(year)

    # build the plot dataset
    for dataset in category_datasets:
        label = dataset['label']
        borderColor = dataset['borderColor']
        data = []
        for year in labels:
            try:
                count = dataset['data'][year]
            except KeyError:
                count = 0
            finally:
                data.append(count)
        plot_dataset.append({'data': data,
                             'label': label,
                             'borderColor': borderColor
                             }
                            )
    return jsonify({'data': plot_dataset, 'labels': labels})
