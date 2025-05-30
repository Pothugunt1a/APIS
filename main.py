from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shashikala.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database Models
class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(120))
    message = db.Column(db.Text)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    email = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    primary_address = db.Column(db.String(200), nullable=False)
    apt_unit_suite = db.Column(db.String(50))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    products = db.relationship('Product', backref='artist', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product', backref='cart_items')


# Create database tables
with app.app_context():
    db.create_all()


# Routes
@app.route('/api/donate', methods=['POST'])
def donate():
    data = request.json
    try:
        donation = Donation(name=data['name'],
                            amount=data['amount'],
                            email=data.get('email'),
                            message=data.get('message'))
        db.session.add(donation)
        db.session.commit()
        return jsonify({"message": "Donation recorded successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    required_fields = [
        'first_name', 'last_name', 'email', 'contact', 'primary_address',
        'city', 'state', 'zipcode'
    ]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    try:
        registration = Registration(**data)
        db.session.add(registration)
        db.session.commit()
        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    try:
        contact = Contact(name=data['name'],
                          email=data['email'],
                          message=data['message'])
        db.session.add(contact)
        db.session.commit()
        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/api/donations', methods=['GET'])
def get_donations():
    donations = Donation.query.all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'amount': d.amount,
        'email': d.email,
        'message': d.message
    } for d in donations])


@app.route('/api/registrations', methods=['GET'])
def get_registrations():
    registrations = Registration.query.all()
    return jsonify([{
        'id': r.id,
        'first_name': r.first_name,
        'last_name': r.last_name,
        'email': r.email,
        'contact': r.contact
    } for r in registrations])


@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    try:
        product = Product(name=data['name'],
                          description=data.get('description', ''),
                          price=data['price'],
                          stock=data['stock'])
        db.session.add(product)
        db.session.commit()
        return jsonify({
            "message": "Product added successfully",
            "id": product.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'stock': p.stock
    } for p in products])


@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    try:
        cart_item = CartItem(user_id=data['user_id'],
                             product_id=data['product_id'],
                             quantity=data.get('quantity', 1))
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({"message": "Item added to cart"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/api/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': item.id,
        'product': {
            'id': item.product.id,
            'name': item.product.name,
            'price': item.product.price
        },
        'quantity': item.quantity,
        'total': item.product.price * item.quantity
    } for item in cart_items])


@app.route('/api/cart/update/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    data = request.json
    try:
        cart_item = CartItem.query.get_or_404(cart_item_id)
        cart_item.quantity = data['quantity']
        db.session.commit()
        return jsonify({"message": "Cart updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/api/cart/remove/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    try:
        cart_item = CartItem.query.get_or_404(cart_item_id)
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Item removed from cart"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Artist APIs
# Artist Authentication
@app.route('/api/auth/artist/signup', methods=['POST'])
def artist_signup():
    data = request.json
    try:
        artist = Artist(
            username=data['email'],
            email=data['email'],
            name=f"{data['firstName']} {data['lastName']}",
            bio=data.get('bio', '')
        )
        db.session.add(artist)
        db.session.commit()
        return jsonify({
            "message": "Artist registered successfully",
            "artistId": artist.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/artist/login', methods=['POST'])
def artist_login():
    data = request.json
    try:
        artist = Artist.query.filter_by(email=data['email']).first()
        if artist:
            # Add proper password verification here
            return jsonify({
                "token": "generated_token",
                "artistId": artist.id
            })
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Profile Management
@app.route('/api/artist/profile', methods=['GET', 'PUT'])
def artist_profile():
    artist_id = request.headers.get('X-Artist-Id')
    
    if request.method == 'GET':
        artist = Artist.query.get_or_404(artist_id)
        return jsonify({
            "id": artist.id,
            "name": artist.name,
            "email": artist.email,
            "bio": artist.bio
        })
    
    elif request.method == 'PUT':
        data = request.json
        try:
            artist = Artist.query.get_or_404(artist_id)
            artist.name = data.get('name', artist.name)
            artist.bio = data.get('bio', artist.bio)
            db.session.commit()
            return jsonify({"message": "Profile updated successfully"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

# Content Management
@app.route('/api/artist/artworks', methods=['GET', 'POST'])
def manage_artworks():
    artist_id = request.headers.get('X-Artist-Id')
    
    if request.method == 'GET':
        artworks = Product.query.filter_by(artist_id=artist_id).all()
        return jsonify([{
            'id': art.id,
            'name': art.name,
            'description': art.description,
            'price': art.price
        } for art in artworks])
    
    elif request.method == 'POST':
        data = request.json
        try:
            artwork = Product(
                name=data['name'],
                description=data['description'],
                price=data['price'],
                stock=data.get('stock', 1),
                artist_id=artist_id
            )
            db.session.add(artwork)
            db.session.commit()
            return jsonify({"message": "Artwork added successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

# Event Management
@app.route('/api/events', methods=['GET', 'POST'])
def manage_events():
    if request.method == 'GET':
        events = Event.query.all()
        return jsonify([{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'date': e.date.isoformat()
        } for e in events])
    
    elif request.method == 'POST':
        data = request.json
        try:
            event = Event(
                title=data['title'],
                description=data['description'],
                date=data['date']
            )
            db.session.add(event)
            db.session.commit()
            return jsonify({"message": "Event created successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def event_operations(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.isoformat()
        })
    
    elif request.method == 'PUT':
        data = request.json
        try:
            event.title = data.get('title', event.title)
            event.description = data.get('description', event.description)
            event.date = data.get('date', event.date)
            db.session.commit()
            return jsonify({"message": "Event updated successfully"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(event)
            db.session.commit()
            return jsonify({"message": "Event deleted successfully"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
