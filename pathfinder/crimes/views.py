import random
from flask import Flask, flash, request, abort, render_template, jsonify, redirect, url_for
from flask_login import login_manager, login_required, current_user

from werkzeug.utils import secure_filename
import flask_excel as excel
from .forms import CrimeCategory
from ..model import Category, Police, CrimeScene
from .. import db
from . import crimes
from collections import OrderedDict
app = Flask(__name__)
excel.init_excel(app)

"""
returns a random color from the color list

"""


def get_color():
    color_list = ['red', 'green', 'lime', 'orange',
                  'pink', 'yellow', 'purple', 'black', 'white']
    return random.choice(color_list)


"""
check if color has been assigned to any category @return None or category

"""


def check_category_by_color(color):
    category = Category.query.filter_by(category_color=color).first()
    if category:
        return category, False
    return None, color


@crimes.route('/admin/crime-category', methods=['POST', 'GET'])
# @login_required
def crimeCategory():
    # if not current_user.is_admin:
    #     abort(403)
    form = CrimeCategory()
    if form.validate_on_submit():
        """
        generate the color for the category
        """
        color_not_obtained = True
        while color_not_obtained:
            color_assigned, color = check_category_by_color(get_color())
            if color_assigned is None:
                color_not_obtained = False
                category = Category(
                    violet_type=form.violet_type.data, category_color=color)
                db.session.add(category)
                db.session.commit()
                flash('You have successfully added a crime category!')
    categories = Category.query.all()
    return render_template('crimes/category_index.html',
                           title="Crime Category",
                           categories=categories,
                           form=form)


@crimes.route('/admin/crime-category/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_crime(id):
    add_crime = False
    crime = Category.query.get_or_404(id)
    form = CrimeCategory(obj=crime)
    if form.validate_on_submit():
        crime.violet_type = form.violet_type.data
        db.session.commit()
        flash('You have successfully edited the Crime Category.')

        # redirect to the departments page
        return redirect(url_for('crimes.crimeCategory'))
    categories = Category.query.all()
    return render_template('crimes/category_index.html',
                           title="Crime Category",
                           categories=categories, action="Add",
                           form=form)


@crimes.route('/admin/crime-category/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_crime(id):
    crime = Category.query.get_or_404(id)
    db.session.delete(crime)
    db.session.commit()
    flash('You have successfully deleted the Crime Category.')

    # redirect to the departments page
    return redirect(url_for('crimes.crimeCategory'))


@crimes.route('/admin/add-crime', methods=['POST', 'GET'])
# @login_required
def addCrime():
    # if not current_user.is_admin:
    #     abort(403)
    if request.form:
        # print(request.form)
        crime = CrimeScene(longitude=request.form.get("longitude"),
                           latitude=request.form.get('latitude'),
                           description=request.form.get('description'),
                           location=request.form.get('location'),
                           category_id=request.form.get('category'),
                           user_id=current_user.id,
                           police_id=request.form.get('police')
                           )
        db.session.add(crime)
        db.session.commit()
        flash('You have successively registered a Crime')
    categories = Category.query.all()
    police_stations = Police.query.all()
    return render_template('crimes/add_crime.html',
                           categories=categories,
                           police_stations=police_stations,
                           title="Add Crime")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@crimes.route('/admin/add_crime_excel', methods=['GET'])
# @login_required
def add_excel_file():
    return render_template('crimes/add_crime_excel.html',
                           title="Add Excel Data")


@crimes.route('/admin/store_excel_data', methods=['POST', 'GET'])
# @login_required
def store_excel_data():
    total_crimes = []
    if request.method == 'POST':
        files = request.get_array(field_name="crimes_excel")

        for file in files:
            crimes = {}
            crimes['reference_number'] = file[0]
            crimes['longitude'] = file[1]
            crimes['latitude'] = file[2]
            crimes['location_description'] = file[3]
            crimes['image_file'] = file[4]
            crimes['date_posted'] = file[5]
            crimes['user_id'] = file[6]
            crimes['police_id'] = file[7]
            crimes['category'] = file[8]
            crimes['location'] = file[9]
            crimes['Arrest'] = file[10]
            crimes['Domestic'] = file[11]
            total_crimes.append(crimes)
            # print(total_crimes)

        for crime in total_crimes:
            crime_scene = CrimeScene(
                longitude=crime["longitude"],
                latitude=crime["latitude"],
                description=crime["location_description"],
                date_posted=crime["date_posted"],
                location=crime["location"],
                category_id=crime["category"],
                user_id=crime["user_id"],
                police_id=crime["police_id"],
                arrest=crime['Arrest'],
                domestic=crime['Domestic']
            )
            db.session.add(crime_scene)
            db.session.commit()

        print()
        return jsonify({"result": total_crimes})
    # return render_template('crimes/add_crime_excel.html',
    #                         title="Add Excel Data")
    pass


@crimes.route('/admin/view_crimes')
# @login_required
def view_crimes():
    allcrimes = CrimeScene.query.all()
    return render_template('crimes/view_crimes.html',
                           allcrimes=allcrimes,
                           title="View Crimes"
                           )
