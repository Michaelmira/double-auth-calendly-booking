from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    first_name = db.Column(db.String(120), unique=False, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)
    address = db.Column(db.String(250), unique=False, nullable=False)
    phone = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return f'<Customer {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "phone": self.phone
        }
    

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    first_name = db.Column(db.String(120), unique=False, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)

    # GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE
    calendar_credentials = db.Column(db.JSON)




    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "first_name": self.first_name,
            "last_name": self.last_name
        }

# GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE Copy This Class. Start
class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duration in minutes
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'confirmed', 'cancelled'
    google_event_id = db.Column(db.String(255))  # To store Google Calendar event ID

    user = db.relationship('User', backref='appointments')
    customer = db.relationship('Customer', backref='appointments')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "customer_id": self.customer_id,
            "datetime": self.datetime.isoformat(),
            "duration": self.duration,
            "status": self.status
        }
    
# GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE GOOGLE Copy This Class. End