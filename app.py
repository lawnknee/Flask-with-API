"""Flask app for adopt app."""

from flask import Flask, render_template, redirect, flash

from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Pet
from forms import AddPetForm, EditPetForm

from petfinder import get_pet_from_API, get_updated_token

from projects_secrets import API_KEY, API_SECRET

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///adopt"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "SECRET!"

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
auth_token = None

@app.before_first_request
def refresh_credentials():
    """Just once, get token and store it globally."""
    global auth_token
    auth_token = get_updated_token()

@app.route('/')
def load_homepage():
    """Loads homepage that shows pet list and availability"""

    pets = Pet.query.all()

    random_pet = get_pet_from_API(auth_token)

    return render_template(
        "home.html",
        pets=pets,
        random_pet=random_pet
    )
    
@app.route('/add', methods=["GET", "POST"])
def show_add_pet_form():
    """Add pet form; handle adding."""
    
    form = AddPetForm()
    
    if form.validate_on_submit():
        name = form.name.data
        species = form.species.data
        photo_url = form.photo_url.data or None
        age = form.age.data
        notes = form.notes.data

        new_pet = Pet(
            name=name, 
            species=species, 
            photo_url=photo_url, 
            age=age, 
            notes=notes)
        db.session.add(new_pet)
        db.session.commit()
        flash(f'Added {name} as pet!')
        return redirect('/')

    else:
        return render_template('add_pet_form.html', form=form)

@app.route('/<int:pet_id>', methods=["GET", "POST"])
def display_edit_pet_form(pet_id):
    """Displays information about the pet with option to make edits to the pet."""
    
    pet = Pet.query.get_or_404(pet_id)
    form = EditPetForm(obj=pet)

    if form.validate_on_submit():
        photo_url = form.photo_url.data
        notes = form.notes.data
        available = form.available.data
        
        pet.photo_url = photo_url
        pet.notes = notes
        pet.available = available
        db.session.commit()
        
        flash(f'Edit to {pet.name} saved!')
        return redirect('/')
    else:
        return render_template('edit_pet_form.html', form=form, pet=pet)
    





