import os
from dotenv import load_dotenv
from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import certifi

ca = certifi.where()

############################################################
# SETUP
############################################################

app = Flask(__name__)

load_dotenv()
password = '' #Replace this with password
# was having issues with certificate validation; had to allow invalid certificates as a work around
uri = f"mongodb+srv://instructor:{password}@cluster0.rrwdoo2.mongodb.net/web-architecture?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
app.config["MONGO_URI"] = uri

mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = mongo.db.plants.find()

    context = {
        'plants': plants_data,
    }

    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        new_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted'),
        }
        result = mongo.db.plants.insert_one(new_plant)
        return redirect(url_for('detail', plant_id=result.inserted_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    print(plant_to_show['name'])
    
    harvests = mongo.db.harvests.find()
    # need to pass plant_id as a string for the harvest list conditional
    context = {
        'plant' : plant_to_show,
        'harvests': harvests,
        'plant_id': plant_id,
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    new_harvest = {
        'quantity': request.form.get('harvested_amount'),
        'date': request.form.get('date_planted'),
        'plant_id': plant_id,
    }

    mongo.db.harvests.insert_one(new_harvest)
    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        updated_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted'),
        }
        mongo.db.plants.update_one({'_id': ObjectId(plant_id)}, { '$set': updated_plant})
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    mongo.db.plants.delete_one({'_id': ObjectId(plant_id)})
    
    mongo.db.harvests.delete_many({'plant_id': plant_id})
    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

