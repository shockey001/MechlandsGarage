import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    update_last_login, count_users, User, bcrypt
)

from functools import wraps

# from content import BLOG_POSTS, EVENTS, GALLERY_ITEMS, SHOP_PRODUCTS, OPEN_POSITIONS

from content import OPEN_POSITIONS
# from models import (
#     list_blog_posts, get_blog_post_by_slug,
#     list_events,
#     list_gallery_items,
#     list_products, get_product,
# )
from models import (
    list_blog_posts, get_blog_post_by_slug, get_blog_post_by_id,
    create_blog_post, update_blog_post, delete_blog_post,
    list_events, get_event_by_id, create_event, update_event, delete_event,
    list_gallery_items, get_gallery_item, create_gallery_item, delete_gallery_item,
    list_products, get_product, create_product, update_product, delete_product,
    list_vehicles, get_vehicle, create_vehicle, delete_vehicle,
    list_car_specs, get_car_spec, create_car_spec, delete_car_spec
)
from wtforms import PasswordField

from route_service import get_route_distance, RouteServiceError
from vin_service import decode_vin, VinServiceError



# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-dev-key')



app = Flask(__name__)

# Require a properly configured secret key.
secret_key = os.environ.get("SECRET_KEY")

if not secret_key or secret_key == "fallback-dev-key":
    raise RuntimeError(
        "SECRET_KEY is missing or insecure. "
        "Configure it in the application environment."
    )

# Application and session security.
app.config.update(
    SECRET_KEY=secret_key,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=(
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower()
        in ("true", "1", "yes")
    ),
)




# Initialize bcrypt with this app
bcrypt.init_app(app)

# Initialize the database (creates tables if they don't exist)
init_db()

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'          # where to redirect if not logged in
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'error'

# Forms

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    slug = StringField('Slug (URL)', validators=[DataRequired(), Length(min=3, max=200)])
    date = StringField('Date (YYYY-MM-DD)', validators=[DataRequired(), Length(min=10, max=10)])
    excerpt = TextAreaField('Excerpt', validators=[DataRequired(), Length(min=10, max=500)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=20)])
    submit = SubmitField('Save Post')


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    slug = StringField('Slug (URL)', validators=[DataRequired(), Length(min=3, max=200)])
    date = StringField('Date (YYYY-MM-DD)', validators=[DataRequired(), Length(min=10, max=10)])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    status = SelectField('Status', choices=[('upcoming', 'Upcoming'), ('past', 'Past')])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Save Event')


class GalleryItemForm(FlaskForm):
    image = StringField('Image Filename', validators=[DataRequired(), Length(max=200)])
    caption = StringField('Caption', validators=[DataRequired(), Length(max=300)])
    category = SelectField('Category', choices=[
        ('ice', 'ICE'),
        ('ev', 'EV'),
        ('tuning', 'Tuning'),
        ('engineering', 'Engineering'),
    ])
    submit = SubmitField('Add Item')


class ProductForm(FlaskForm):
    sku = StringField('SKU (unique)', validators=[DataRequired(), Length(max=50)])
    category = SelectField('Category', choices=[
        ('spares', 'Spares'),
        ('tools', 'Tools'),
        ('accessories', 'Accessories'),
    ])
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    price = StringField('Price in KES (leave blank for "Request Price")', validators=[Length(max=20)])
    submit = SubmitField('Save Product')

class VehicleForm(FlaskForm):
    title = StringField('Listing Title', validators=[DataRequired(), Length(max=150)])
    make = StringField('Make (e.g. Toyota)', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model (e.g. Axio)', validators=[DataRequired(), Length(max=50)])
    year = StringField('Year', validators=[DataRequired()])
    price = StringField('Price (KES)', validators=[DataRequired()])
    mileage = StringField('Mileage (km)', validators=[DataRequired()])
    fuel_type = SelectField('Fuel Type', choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Hybrid', 'Hybrid'), ('Electric', 'Electric')])
    transmission = SelectField('Transmission', choices=[('Automatic', 'Automatic'), ('Manual', 'Manual')])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = StringField('Image URL (optional)')
    submit = SubmitField('Save Vehicle')


@login_manager.user_loader
def load_user(user_id):
    row = get_user_by_id(int(user_id))
    if row:
        return User(row)
    return None

# ============ ADMIN ACCESS CONTROL ============

def admin_required(f):
    """Decorator: only allow users with role='admin'."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        if current_user.role != 'admin':
            flash('You do not have permission to access that page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function




# ============ SEARCHABLE STATIC PAGES ============
# Pages that don't come from content.py but should be searchable
SEARCHABLE_PAGES = [
    {
        'title': 'Services',
        'url_endpoint': 'services',
        'description': 'ICE repair, EV servicing, conversions, tuning, and engineering services.',
        'keywords': 'services repair diagnostics engine brakes suspension electrical tuning conversion ev ice',
    },
    {
        'title': 'Shop',
        'url_endpoint': 'shop',
        'description': 'Auto spares, tools, and accessories.',
        'keywords': 'shop store buy parts spares tools accessories',
    },
    {
        'title': 'About Mechlands Garage',
        'url_endpoint': 'about',
        'description': 'Our story, philosophy, and the founder behind Mechlands Garage.',
        'keywords': 'about founder story philosophy gachoki ndwiga team',
    },
    {
        'title': 'Investors',
        'url_endpoint': 'investors',
        'description': 'Investment opportunities in Kenya\'s automotive transition.',
        'keywords': 'investors investment funding capital opportunity partner',
    },
    {
        'title': 'Business Plan',
        'url_endpoint': 'business_plan',
        'description': 'Full business plan — market analysis, phases, and financials.',
        'keywords': 'business plan strategy market financials phases',
    },
    {
        'title': 'Contact',
        'url_endpoint': 'contact',
        'description': 'Get in touch with Mechlands Garage.',
        'keywords': 'contact reach email phone message inquiry',
    },
    {
        'title': 'Blog',
        'url_endpoint': 'blog',
        'description': 'Technical writing, industry insight, and honest advice.',
        'keywords': 'blog articles writing insight technical',
    },
    {
        'title': 'Events',
        'url_endpoint': 'events',
        'description': 'Open days, workshops, and gatherings.',
        'keywords': 'events workshops open day gatherings schedule',
    },
    {
        'title': 'Gallery',
        'url_endpoint': 'gallery',
        'description': 'Photos of real work from Mechlands Garage.',
        'keywords': 'gallery photos images work portfolio',
    },
]


# ---- Contact form definition ----
# class ContactForm(FlaskForm):
#     name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     phone = StringField('Phone (optional)', validators=[Length(max=30)])
#     service = SelectField('Service of Interest', choices=[
#         ('ice', 'ICE Repair & Maintenance'),
#         ('ev', 'EV Diagnostics & Servicing'),
#         ('conversion', 'ICE-to-EV Conversion'),
#         ('tuning', 'Tuning & Customization'),
#         ('engineering', 'Engineering & Prototyping'),
#         ('investor', 'Investment / Partnership'),
#         ('other', 'Other'),
#     ])
#     message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
#     submit = SubmitField('Send Message')

class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone (optional)', validators=[Length(max=30)])
    service = SelectField('Service of Interest', choices=[
        ('ice', 'ICE Repair & Maintenance'),
        ('ev', 'EV Diagnostics & Servicing'),
        ('conversion', 'ICE-to-EV Conversion'),
        ('tuning', 'Tuning & Customization'),
        ('engineering', 'Engineering & Prototyping'),
        ('car_sales', 'Car Sales & Sourcing'),
        ('retrofitting', 'EV Retrofitting'),
        ('investor', 'Investment / Partnership'),
        ('other', 'Other'),
    ])
    # THIS is the field that was missing or misnamed:
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')

class InvestorInquiryForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone (optional)', validators=[Length(max=30)])
    investor_type = SelectField('I am a', choices=[
        ('individual', 'Individual investor'),
        ('fund', 'Investment fund / institution'),
        ('operator', 'Industry operator / partner'),
        ('grant', 'Grant / development program'),
        ('other', 'Other'),
    ])
    interest_level = SelectField('Interest level', choices=[
        ('exploring', 'Exploring — want more information'),
        ('considering', 'Considering — interested in details'),
        ('ready', 'Ready — want to discuss terms'),
        ('supporting', 'Supporting — ready to commit'),
    ])
    amount_range = SelectField('Indicative amount (optional)', choices=[
        ('not_specified', 'Prefer not to say'),
        ('under_200k', 'Under KES 200,000'),
        ('200k_1m', 'KES 200,000 – 1M'),
        ('1m_5m', 'KES 1M – 5M'),
        ('5m_plus', 'KES 5M+'),
    ])
    question = TextAreaField('Your question or message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Send Inquiry')


class ShopOrderForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone / WhatsApp', validators=[DataRequired(), Length(min=7, max=30)])
    delivery = SelectField('Delivery Preference', choices=[
        ('pickup', 'Pick up from workshop'),
        ('delivery', 'Delivery (I will provide address)'),
        ('discuss', 'Discuss with me'),
    ])
    items = TextAreaField('Items You Want', validators=[DataRequired(), Length(min=3, max=2000)])
    notes = TextAreaField('Additional Notes (optional)', validators=[Length(max=1000)])
    submit = SubmitField('Send Order Request')

class JobApplicationForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone / WhatsApp', validators=[DataRequired(), Length(min=7, max=30)])
    position = SelectField('Position Applying For', choices=[])  # populated at request time
    experience = StringField('Years of Experience', validators=[Length(max=50)])
    message = TextAreaField('Cover Message', validators=[DataRequired(), Length(min=20, max=3000)])
    submit = SubmitField('Submit Application')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate position choices from open positions only
        self.position.choices = [
            (p['slug'], p['title']) for p in OPEN_POSITIONS if p['status'] == 'open'
        ]
        # If no open positions, add a placeholder
        if not self.position.choices:
            self.position.choices = [('none', 'No positions currently open')]

class CarSpecForm(FlaskForm):
    make = StringField('Make (e.g. Toyota)', validators=[DataRequired()])
    model = StringField('Model (e.g. Axio)', validators=[DataRequired()])
    year = StringField('Years Available (e.g. 2012-2018)')
    body_type = StringField('Body Type (e.g. Sedan)')
    engine_cc = StringField('Engine Size (cc)')
    fuel_type = StringField('Fuel Type (e.g. Petrol)')
    fuel_efficiency = StringField('Fuel Efficiency (e.g. 15 km/L)')
    reliability_score = StringField('Reliability Score (1-10)')
    maintenance_cost = StringField('Maintenance Cost (e.g. Low / KES 20k/yr)')
    resale_value = StringField('Resale Value (e.g. High)')
    spares_availability = StringField('Spares Availability (e.g. Excellent)')
    notes = TextAreaField('Notes / Known Issues')
    submit = SubmitField('Save Car Specs')



# ---- Routes ----
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/investors')
def investors():
    return render_template('investors.html')

@app.route('/business-plan')
def business_plan():
    return render_template('business_plan.html')

@app.route('/investor-inquiry', methods=['GET', 'POST'])
def investor_inquiry():
    form = InvestorInquiryForm()
    if form.validate_on_submit():
        submission = {
            'timestamp': datetime.now().isoformat(),
            'type': 'investor_inquiry',
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'investor_type': form.investor_type.data,
            'interest_level': form.interest_level.data,
            'amount_range': form.amount_range.data,
            'question': form.question.data,
        }
        data_dir = os.path.join(app.root_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        submissions_file = os.path.join(data_dir, 'submissions.jsonl')
        with open(submissions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(submission) + '\n')

        flash('Thank you — your inquiry has been received. We will respond personally.', 'success')
        return redirect(url_for('investor_inquiry'))

    return render_template('investor_inquiry.html', form=form)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    # Check if we arrived here via a specific link (e.g., from a Car or Retrofitting page)
    if request.method == 'GET':
        subject = request.args.get('subject', '')
        category = request.args.get('category', '')

        if subject:
            form.message.data = subject
        if category:
            form.service.data = category

    if form.validate_on_submit():
        # Determine the type based on the selected service
        submission_type = 'contact'
        if form.service.data == 'car_sales':
            submission_type = 'cars'
        elif form.service.data == 'investor':
            submission_type = 'investor_inquiry'

        # Build the submission dictionary
        submission = {
            'timestamp': datetime.now().isoformat(),
            'type': submission_type,
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'service': form.service.data,
            'message': form.message.data,
        }

        # Save to JSONL
        data_dir = os.path.join(app.root_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        submissions_file = os.path.join(data_dir, 'submissions.jsonl')

        with open(submissions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(submission) + '\n')

        flash('Thank you — your message has been received. We will respond shortly.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)



# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     form = ContactForm()
#     if form.validate_on_submit():
#         submission = {
#             'timestamp': datetime.now().isoformat(),
#             'name': form.name.data,
#             'email': form.email.data,
#             'phone': form.phone.data,
#             'service': form.service.data,
#             'message': form.message.data,
#         }
#         data_dir = os.path.join(app.root_path, 'data')
#         os.makedirs(data_dir, exist_ok=True)
#         submissions_file = os.path.join(data_dir, 'submissions.jsonl')
#         with open(submissions_file, 'a', encoding='utf-8') as f:
#             f.write(json.dumps(submission) + '\n')
#
#         flash('Thank you — your message has been received. We will respond shortly.', 'success')
#         return redirect(url_for('contact'))
#
#     return render_template('contact.html', form=form)

# ============ MEDIA PAGES ============

@app.route('/blog')
def blog():
    # Sort posts by date, newest first
    posts = sorted(list_blog_posts(), key=lambda p: p['date'], reverse=True)
    return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = get_blog_post_by_slug(slug)
    if post is None:
        return render_template('404.html'), 404
    return render_template('blog_post.html', post=post)

@app.route('/events')
def events():
    all_events = list_events()
    upcoming = [e for e in all_events if e['status'] == 'upcoming']
    past = [e for e in all_events if e['status'] == 'past']
    return render_template('events.html', upcoming=upcoming, past=past)

@app.route('/gallery')
def gallery():
    items = list_gallery_items()
    return render_template('gallery.html', items=items)

# ============ SHOP ============

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/shop/<category>')
def shop_category(category):
    valid = ['spares', 'tools', 'accessories']
    if category not in valid:
        return render_template('404.html'), 404
    products = list_products(category=category)
    return render_template('shop_category.html', category=category, products=products)

@app.route('/shop/order', methods=['GET', 'POST'])
def shop_order():
    form = ShopOrderForm()
    if form.validate_on_submit():
        submission = {
            'timestamp': datetime.now().isoformat(),
            'type': 'shop_order',
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'delivery': form.delivery.data,
            'items': form.items.data,
            'notes': form.notes.data,
        }
        data_dir = os.path.join(app.root_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        submissions_file = os.path.join(data_dir, 'submissions.jsonl')
        with open(submissions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(submission) + '\n')

        flash('Thank you — your order request has been received. We will contact you shortly to confirm.', 'success')
        return redirect(url_for('shop_order'))

    return render_template('shop_order.html', form=form)

# ============ SEARCH ============

@app.route('/careers')
def careers():
    positions = [p for p in OPEN_POSITIONS if p['status'] == 'open']
    return render_template('careers.html', positions=positions)


@app.route('/careers/apply/<position_slug>', methods=['GET', 'POST'])
def careers_apply(position_slug):
    position = next((p for p in OPEN_POSITIONS if p['slug'] == position_slug), None)
    if not position or position['status'] != 'open':
        return render_template('404.html'), 404

    form = JobApplicationForm()
    # Pre-select the position from the URL
    if request.method == 'GET':
        form.position.data = position_slug

    if form.validate_on_submit():
        submission = {
            'timestamp': datetime.now().isoformat(),
            'type': 'job_application',
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'position': form.position.data,
            'position_title': next(
                (p['title'] for p in OPEN_POSITIONS if p['slug'] == form.position.data),
                form.position.data
            ),
            'experience': form.experience.data,
            'message': form.message.data,
        }
        data_dir = os.path.join(app.root_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        submissions_file = os.path.join(data_dir, 'submissions.jsonl')
        with open(submissions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(submission) + '\n')

        flash('Thank you — your application has been received. We will be in touch if your profile matches our needs.', 'success')
        return redirect(url_for('careers_apply', position_slug=position_slug))

    return render_template('careers_apply.html', form=form, position=position)

# ============ PUBLIC: CAR SALES ============
@app.route('/cars')
def car_sales():
    vehicles = list_vehicles()
    return render_template('cars.html', vehicles=vehicles)

@app.route('/retrofitting')
def retrofitting():
    return render_template('retrofitting.html')

# ============ ADMIN: CAR SALES ============
@app.route('/admin/cars')
@login_required
@admin_required
def admin_cars():
    vehicles = list_vehicles(status=None) # Show all, including sold
    return render_template('admin/cars_list.html', vehicles=vehicles)

@app.route('/admin/cars/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_cars_new():
    form = VehicleForm()
    if form.validate_on_submit():
        create_vehicle(
            title=form.title.data,
            make=form.make.data,
            model=form.model.data,
            year=int(form.year.data),
            price=int(form.price.data),
            mileage=int(form.mileage.data),
            fuel_type=form.fuel_type.data,
            transmission=form.transmission.data,
            description=form.description.data,
            image_url=form.image_url.data
        )
        flash('Vehicle added to listings.', 'success')
        return redirect(url_for('admin_cars'))
    return render_template('admin/vehicle_form.html', form=form)

@app.route('/admin/cars/<int:vehicle_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_cars_delete(vehicle_id):
    delete_vehicle(vehicle_id)
    flash('Vehicle deleted.', 'success')
    return redirect(url_for('admin_cars'))




import re

def _stem(word):
    """Reduce a word to a rough stem for plural matching."""
    w = word.lower()
    if len(w) > 4:
        if w.endswith('ies'):
            return w[:-3] + 'y'         # batteries -> battery
        if w.endswith(('ses', 'xes', 'zes', 'ches', 'shes')):
            return w[:-2]               # boxes -> box, churches -> church
        if w.endswith('s'):
            return w[:-1]               # brakes -> brake, pads -> pad
    if len(w) > 3 and w.endswith('s'):
        return w[:-1]                   # cars -> car
    return w

# def _stem(word):
#     """Reduce a word to a rough stem for plural matching."""
#     w = word.lower()
#     if len(w) > 4:
#         if w.endswith('ies'):
#             return w[:-3] + 'y'   # batteries -> battery
#         if w.endswith('es'):
#             return w[:-2]         # brakes -> brak, boxes -> box
#         if w.endswith('s'):
#             return w[:-1]         # pads -> pad
#     if len(w) > 3 and w.endswith('s'):
#         return w[:-1]             # cars -> car
#     return w


def _tokenize(text):
    """Split text into a set of lowercase word tokens."""
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def _matches(query, haystack_text):
    """
    Check if every word in the query matches something in the haystack.
    A word "matches" if:
      - exact token appears in haystack, OR
      - its stem appears among haystack stems
    """
    query_words = re.findall(r'[a-z0-9]+', query.lower())
    if not query_words:
        return False

    haystack_tokens = _tokenize(haystack_text)
    haystack_stems = {_stem(t) for t in haystack_tokens}

    for qw in query_words:
        # Exact match?
        if qw in haystack_tokens:
            continue
        # Stem match?
        if _stem(qw) in haystack_stems:
            continue
        # No match for this word — whole query fails
        return False

    return True


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()

    results = {
        'products': [],
        'blog': [],
        'events': [],
        'pages': [],
    }

    if query:
        # --- Search Products ---
        for product in list_products():
            haystack = (product['name'] + ' ' + product['description'] + ' ' + product['category'])
            if _matches(query, haystack):
                results['products'].append(product)

        # --- Search Blog Posts ---
        for post in list_blog_posts():
            haystack = (post['title'] + ' ' + post['excerpt'] + ' ' + post['body'])
            if _matches(query, haystack):
                results['blog'].append(post)

        # --- Search Events ---
        for event in list_events():
            haystack = (event['title'] + ' ' + event['description'] + ' ' + event['location'])
            if _matches(query, haystack):
                results['events'].append(event)

        # --- Search Static Pages ---
        for page in SEARCHABLE_PAGES:
            haystack = (page['title'] + ' ' + page['description'] + ' ' + page['keywords'])
            if _matches(query, haystack):
                results['pages'].append(page)

    total = (len(results['products']) + len(results['blog'])
             + len(results['events']) + len(results['pages']))

    return render_template('search.html', query=query, results=results, total=total)



# ============ CAREERS ============



# ============ SEARCH ============
#
# def _tokenize(text):
#     """Convert text into a set of lowercase word tokens, with basic plural handling."""
#     import re
#     # Keep letters and numbers only, split on everything else
#     words = re.findall(r'[a-z0-9]+', text.lower())
#     tokens = set()
#     for w in words:
#         tokens.add(w)
#         # Basic plural stemming: "brakes" -> "brake", "pads" -> "pad"
#         if len(w) > 3:
#             if w.endswith('ies'):
#                 tokens.add(w[:-3] + 'y')  # "batteries" -> "battery"
#             elif w.endswith('es'):
#                 tokens.add(w[:-2])        # "brakes" -> "brak" (fallback)
#                 tokens.add(w[:-1])        # "brakes" -> "brake"
#             elif w.endswith('s'):
#                 tokens.add(w[:-1])        # "pads" -> "pad"
#     return tokens
#
#
# def _matches(query_tokens, haystack_text):
#     """Check if every query token matches some token in the haystack."""
#     haystack_tokens = _tokenize(haystack_text)
#     # Every query token must be present (AND logic)
#     return query_tokens.issubset(haystack_tokens)
#
#
# @app.route('/search')
# def search():
#     query = request.args.get('q', '').strip()
#
#     results = {
#         'products': [],
#         'blog': [],
#         'events': [],
#         'pages': [],
#     }
#
#     if query:
#         query_tokens = _tokenize(query)
#
#         # --- Search Products ---
#         for product in SHOP_PRODUCTS:
#             haystack = (product['name'] + ' ' + product['description'] + ' ' + product['category'])
#             if _matches(query_tokens, haystack):
#                 results['products'].append(product)
#
#         # --- Search Blog Posts ---
#         for post in BLOG_POSTS:
#             haystack = (post['title'] + ' ' + post['excerpt'] + ' ' + post['body'])
#             if _matches(query_tokens, haystack):
#                 results['blog'].append(post)
#
#         # --- Search Events ---
#         for event in EVENTS:
#             haystack = (event['title'] + ' ' + event['description'] + ' ' + event['location'])
#             if _matches(query_tokens, haystack):
#                 results['events'].append(event)
#
#         # --- Search Static Pages ---
#         for page in SEARCHABLE_PAGES:
#             haystack = (page['title'] + ' ' + page['description'] + ' ' + page['keywords'])
#             if _matches(query_tokens, haystack):
#                 results['pages'].append(page)
#
#     total = (len(results['products']) + len(results['blog'])
#              + len(results['events']) + len(results['pages']))
#
#     return render_template('search.html', query=query, results=results, total=total)
#


# ============ SEARCH ============
#
# @app.route('/search')
# def search():
#     query = request.args.get('q', '').strip()
#     q_lower = query.lower()
#
#     results = {
#         'products': [],
#         'blog': [],
#         'events': [],
#         'pages': [],
#     }
#
#     if query:
#         # --- Search Products ---
#         for product in SHOP_PRODUCTS:
#             haystack = (product['name'] + ' ' + product['description'] + ' ' + product['category']).lower()
#             if q_lower in haystack:
#                 results['products'].append(product)
#
#         # --- Search Blog Posts ---
#         for post in BLOG_POSTS:
#             haystack = (post['title'] + ' ' + post['excerpt'] + ' ' + post['body']).lower()
#             if q_lower in haystack:
#                 results['blog'].append(post)
#
#         # --- Search Events ---
#         for event in EVENTS:
#             haystack = (event['title'] + ' ' + event['description'] + ' ' + event['location']).lower()
#             if q_lower in haystack:
#                 results['events'].append(event)
#
#         # --- Search Static Pages ---
#         for page in SEARCHABLE_PAGES:
#             haystack = (page['title'] + ' ' + page['description'] + ' ' + page['keywords']).lower()
#             if q_lower in haystack:
#                 results['pages'].append(page)
#
#     total = (len(results['products']) + len(results['blog'])
#              + len(results['events']) + len(results['pages']))
#
#     return render_template('search.html', query=query, results=results, total=total)
#


# ============ AUTHENTICATION ============



@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user_row = get_user_by_email(form.email.data)
        if user_row and bcrypt.check_password_hash(user_row['password_hash'], form.password.data):
            user = User(user_row)
            login_user(user, remember=False)
            update_last_login(int(user.id))

            # Redirect to the page they were trying to access, or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))

        # Login failed — don't reveal which field was wrong (security)
        flash('Invalid email or password.', 'error')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ============ ADMIN DASHBOARD ============

@app.route('/admin')
@login_required
@admin_required
def admin_home():
    from models import count_submissions_by_type, count_users
    counts = count_submissions_by_type()
    total_submissions = sum(counts.values())
    total_users = count_users()
    return render_template('admin/home.html',
                           counts=counts,
                           total_submissions=total_submissions,
                           total_users=total_users)


@app.route('/admin/submissions')
@login_required
@admin_required
def admin_submissions():
    from models import read_submissions
    submissions = read_submissions()

    # Optional filter by type
    filter_type = request.args.get('type', '')
    if filter_type:
        submissions = [s for s in submissions if s.get('type') == filter_type]

    return render_template('admin/submissions.html',
                           submissions=submissions,
                           filter_type=filter_type)


# ============ ADMIN: BLOG ============

@app.route('/admin/blog')
@login_required
@admin_required
def admin_blog():
    posts = list_blog_posts()
    return render_template('admin/blog_list.html', posts=posts)


@app.route('/admin/blog/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_blog_new():
    form = BlogPostForm()
    if form.validate_on_submit():
        result = create_blog_post(
            slug=form.slug.data.strip().lower().replace(' ', '-'),
            title=form.title.data.strip(),
            date=form.date.data.strip(),
            excerpt=form.excerpt.data.strip(),
            body=form.body.data,
        )
        if result:
            flash('Blog post created.', 'success')
            return redirect(url_for('admin_blog'))
        flash('That slug is already in use — try a different one.', 'error')
    return render_template('admin/blog_form.html', form=form, post=None)


@app.route('/admin/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_blog_edit(post_id):
    post = get_blog_post_by_id(post_id)
    if not post:
        return render_template('404.html'), 404

    form = BlogPostForm(data=post)
    if form.validate_on_submit():
        ok = update_blog_post(
            post_id=post_id,
            slug=form.slug.data.strip().lower().replace(' ', '-'),
            title=form.title.data.strip(),
            date=form.date.data.strip(),
            excerpt=form.excerpt.data.strip(),
            body=form.body.data,
        )
        if ok:
            flash('Blog post updated.', 'success')
            return redirect(url_for('admin_blog'))
        flash('That slug is already in use.', 'error')
    return render_template('admin/blog_form.html', form=form, post=post)


@app.route('/admin/blog/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_blog_delete(post_id):
    delete_blog_post(post_id)
    flash('Blog post deleted.', 'success')
    return redirect(url_for('admin_blog'))


# ============ ADMIN: EVENTS ============

@app.route('/admin/events')
@login_required
@admin_required
def admin_events():
    events = list_events()
    return render_template('admin/events_list.html', events=events)


@app.route('/admin/events/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_events_new():
    form = EventForm()
    if form.validate_on_submit():
        result = create_event(
            slug=form.slug.data.strip().lower().replace(' ', '-'),
            title=form.title.data.strip(),
            date=form.date.data.strip(),
            location=form.location.data.strip(),
            status=form.status.data,
            description=form.description.data.strip(),
        )
        if result:
            flash('Event created.', 'success')
            return redirect(url_for('admin_events'))
        flash('That slug is already in use.', 'error')
    return render_template('admin/event_form.html', form=form, event=None)


@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_events_edit(event_id):
    event = get_event_by_id(event_id)
    if not event:
        return render_template('404.html'), 404

    form = EventForm(data=event)
    if form.validate_on_submit():
        ok = update_event(
            event_id=event_id,
            slug=form.slug.data.strip().lower().replace(' ', '-'),
            title=form.title.data.strip(),
            date=form.date.data.strip(),
            location=form.location.data.strip(),
            status=form.status.data,
            description=form.description.data.strip(),
        )
        if ok:
            flash('Event updated.', 'success')
            return redirect(url_for('admin_events'))
        flash('That slug is already in use.', 'error')
    return render_template('admin/event_form.html', form=form, event=event)


@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_events_delete(event_id):
    delete_event(event_id)
    flash('Event deleted.', 'success')
    return redirect(url_for('admin_events'))


# ============ ADMIN: GALLERY ============

@app.route('/admin/gallery')
@login_required
@admin_required
def admin_gallery():
    items = list_gallery_items()
    return render_template('admin/gallery_list.html', items=items)


@app.route('/admin/gallery/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_gallery_new():
    form = GalleryItemForm()
    if form.validate_on_submit():
        create_gallery_item(
            image=form.image.data.strip(),
            caption=form.caption.data.strip(),
            category=form.category.data,
        )
        flash('Gallery item added.', 'success')
        return redirect(url_for('admin_gallery'))
    return render_template('admin/gallery_form.html', form=form)


@app.route('/admin/gallery/<int:item_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_gallery_delete(item_id):
    delete_gallery_item(item_id)
    flash('Gallery item deleted.', 'success')
    return redirect(url_for('admin_gallery'))


# ============ ADMIN: PRODUCTS ============

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    products = list_products()
    return render_template('admin/products_list.html', products=products)


@app.route('/admin/products/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_products_new():
    form = ProductForm()
    if form.validate_on_submit():
        price_str = (form.price.data or '').strip()
        price = int(price_str) if price_str.isdigit() else None

        result = create_product(
            sku=form.sku.data.strip(),
            category=form.category.data,
            name=form.name.data.strip(),
            description=form.description.data.strip(),
            price=price,
        )
        if result:
            flash('Product created.', 'success')
            return redirect(url_for('admin_products'))
        flash('That SKU is already in use.', 'error')
    return render_template('admin/product_form.html', form=form, product=None)


@app.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_products_edit(product_id):
    product = get_product(product_id)
    if not product:
        return render_template('404.html'), 404

    form = ProductForm(data=product)
    if form.validate_on_submit():
        price_str = (form.price.data or '').strip()
        price = int(price_str) if price_str.isdigit() else None

        ok = update_product(
            product_id=product_id,
            sku=form.sku.data.strip(),
            category=form.category.data,
            name=form.name.data.strip(),
            description=form.description.data.strip(),
            price=price,
        )
        if ok:
            flash('Product updated.', 'success')
            return redirect(url_for('admin_products'))
        flash('That SKU is already in use.', 'error')
    return render_template('admin/product_form.html', form=form, product=product)


@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_products_delete(product_id):
    delete_product(product_id)
    flash('Product deleted.', 'success')
    return redirect(url_for('admin_products'))


# ============ ADMIN: CAR SPECS ============
@app.route('/admin/car-specs')
@login_required
@admin_required
def admin_car_specs():
    specs = list_car_specs()
    return render_template('admin/car_specs_list.html', specs=specs)

@app.route('/admin/car-specs/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_car_specs_new():
    form = CarSpecForm()
    if form.validate_on_submit():
        # Handle empty numbers gracefully
        cc = int(form.engine_cc.data) if form.engine_cc.data and form.engine_cc.data.isdigit() else None
        score = int(form.reliability_score.data) if form.reliability_score.data and form.reliability_score.data.isdigit() else None

        create_car_spec(
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            body_type=form.body_type.data,
            engine_cc=cc,
            fuel_type=form.fuel_type.data,
            fuel_efficiency=form.fuel_efficiency.data,
            reliability_score=score,
            maintenance_cost=form.maintenance_cost.data,
            resale_value=form.resale_value.data,
            spares_availability=form.spares_availability.data,
            notes=form.notes.data
        )
        flash('Car specs added to database.', 'success')
        return redirect(url_for('admin_car_specs'))
    return render_template('admin/car_spec_form.html', form=form)

@app.route('/admin/car-specs/<int:car_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_car_specs_delete(car_id):
    delete_car_spec(car_id)
    flash('Car spec deleted.', 'success')
    return redirect(url_for('admin_car_specs'))


# ============ TOOLS ============

@app.route('/tools')
def tools():
    return render_template('tools.html')


@app.route('/tools/loan-calculator')
def loan_calculator():
    return render_template('loan_calculator.html')


@app.route('/tools/insurance-calculator')
def insurance_calculator():
    return render_template('insurance_calculator.html')


@app.route('/tools/fuel-efficiency')
def fuel_efficiency():
    return render_template('fuel_efficiency.html')

@app.route('/tools/ev-vs-ice')
def ev_vs_ice():
    import config_kenya as ck
    config = {
        'petrol_price': ck.PETROL_PRICE_KES,
        'diesel_price': ck.DIESEL_PRICE_KES,
        'electricity_price': ck.ELECTRICITY_PRICE_KES,
        'petrol_sedan_consumption': ck.PETROL_SEDAN_L_PER_100KM,
        'petrol_suv_consumption': ck.PETROL_SUV_L_PER_100KM,
        'diesel_pickup_consumption': ck.DIESEL_PICKUP_L_PER_100KM,
        'ev_consumption': ck.EV_KWH_PER_100KM,
        'ice_maintenance': ck.ICE_MAINTENANCE_PER_10K_KM,
        'ev_maintenance': ck.EV_MAINTENANCE_PER_10K_KM,
        'insurance_rate': ck.INSURANCE_RATE_COMPREHENSIVE,
        'ice_depreciation': ck.ICE_ANNUAL_DEPRECIATION,
        'ev_depreciation': ck.EV_ANNUAL_DEPRECIATION,
    }
    return render_template('ev_vs_ice.html', config=config)


@app.route('/tools/route-cost')
def route_cost():
    import config_kenya as ck
    config = {
        'petrol_price': ck.PETROL_PRICE_KES,
        'diesel_price': ck.DIESEL_PRICE_KES,
        'electricity_price': ck.ELECTRICITY_PRICE_KES,
        'petrol_sedan_consumption': ck.PETROL_SEDAN_L_PER_100KM,
        'petrol_suv_consumption': ck.PETROL_SUV_L_PER_100KM,
        'diesel_pickup_consumption': ck.DIESEL_PICKUP_L_PER_100KM,
        'ev_consumption': ck.EV_KWH_PER_100KM,
    }
    return render_template('route_cost.html', config=config)

@app.route('/tools/car-compare')
def car_compare():
    specs = list_car_specs()
    return render_template('car_compare.html', specs=specs)


@app.route('/api/route-distance', methods=['POST'])
def api_route_distance():
    """API endpoint: called by the calculator via JavaScript."""
    data = request.get_json(silent=True) or {}
    start = (data.get('start') or '').strip()
    end = (data.get('end') or '').strip()

    if not start or not end:
        return {'error': 'Both start and destination are required.'}, 400

    try:
        result = get_route_distance(start, end)
        return result
    except RouteServiceError as e:
        return {'error': str(e)}, 400

@app.route('/tools/maintenance-cost')
def maintenance_cost():
    import config_kenya as ck
    config = {
        'intervals': ck.SERVICE_INTERVALS_KM,
        'costs_ice': ck.MAINTENANCE_COSTS_ICE,
        'costs_ev': ck.MAINTENANCE_COSTS_EV,
        'age_multipliers': ck.VEHICLE_AGE_MULTIPLIER,
    }
    return render_template('maintenance_cost.html', config=config)

@app.route('/tools/vin-decoder')
def vin_decoder():
    return render_template('vin_decoder.html')


@app.route('/api/vin-decode', methods=['POST'])
def api_vin_decode():
    """API endpoint: called by the VIN decoder via JavaScript."""
    data = request.get_json(silent=True) or {}
    vin = (data.get('vin') or '').strip()

    try:
        result = decode_vin(vin)
        return result
    except VinServiceError as e:
        return {'error': str(e)}, 400



if __name__ == '__main__':
    app.run(debug=True)