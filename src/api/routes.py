"""
This module takes care of starting the API Server, Loading the DB, and Adding the endpoints
"""

from flask import Flask, request, jsonify, url_for, Blueprint, redirect
from api.models import db, User, Customer, Appointment
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt, decode_token
)
from api.decorators import admin_required
from datetime import datetime, timedelta

# Google Imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
# End Google Imports

api = Blueprint('api', __name__)
CORS(api)

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = "path_to_your_client_secrets.json"  # Download from Google Cloud Console

# === Google Calendar Authorization Route ===
@api.route('/calendar/authorize/<int:user_id>', methods=['GET'])
def authorize_google_calendar(user_id):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='your_redirect_uri'
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return jsonify({"authorization_url": authorization_url}), 200

# === Google Calendar OAuth2 Callback ===
@api.route('/calendar/oauth2callback', methods=['GET'])
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='your_redirect_uri'
    )
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    
    # Store credentials in your database (credentials field needed in User model)
    
    return redirect('/calendar-connected')

# === Get Available Slots ===
@api.route('/appointments/available-slots/<int:user_id>', methods=['GET'])
@jwt_required()
def get_available_slots(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    credentials = Credentials.from_authorized_user_info(user.credentials)
    service = build('calendar', 'v3', credentials=credentials)

    # Logic to get available slots here
    # Check user's calendar for free slots
    
    return jsonify({"available_slots": available_slots}), 200

# === Schedule Appointment ===
@api.route('/appointments/schedule', methods=['POST'])
@jwt_required()
def schedule_appointment():
    user_id = request.json.get("user_id")
    customer_id = get_jwt_identity()
    datetime_str = request.json.get("datetime")
    duration = request.json.get("duration", 60)  # default 60 minutes

    if not all([user_id, datetime_str]):
        return jsonify({"msg": "Missing required fields"}), 400

    appointment_datetime = datetime.fromisoformat(datetime_str)

    # Create appointment in database
    appointment = Appointment(
        user_id=user_id,
        customer_id=customer_id,
        datetime=appointment_datetime,
        duration=duration,
        status="pending"
    )
    db.session.add(appointment)

    # Create Google Calendar event
    user = User.query.get(user_id)
    credentials = Credentials.from_authorized_user_info(user.credentials)
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': f'Appointment with Customer #{customer_id}',
        'start': {
            'dateTime': appointment_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (appointment_datetime + timedelta(minutes=duration)).isoformat(),
            'timeZone': 'UTC',
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    appointment.google_event_id = created_event['id']

    db.session.commit()

    return jsonify(appointment.serialize()), 201

# === User Login Route ===
@api.route('/user/login', methods=['POST'])
def handle_user_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is None or password is None:
        return jsonify({"msg": "No email or password"}), 400
    user = User.query.filter_by(email=email).one_or_none()
    if user is None:
        return jsonify({"msg": "No such user"}), 404
    if user.password != password:
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=user.id, additional_claims={"role": "owner"})
    return jsonify(access_token=access_token), 201

# === Customer Signup Route ===
@api.route('/customer/signup', methods=['POST'])
def handle_customer_signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    first_name = request.json.get("first_name", None)
    last_name = request.json.get("last_name", None)
    address = request.json.get("address", None)
    phone = request.json.get("phone", None)
    
    if email is None or password is None or first_name is None or last_name is None or address is None or phone is None:
        return jsonify({"msg": "Some fields are missing in your request"}), 400

    customer = Customer.query.filter_by(email=email).one_or_none()
    if customer:
        return jsonify({"msg": "An account associated with the email already exists"}), 409

    customer = Customer(
        email=email, password=password, first_name=first_name, last_name=last_name,
        address=address, phone=phone, is_active=True
    )
    db.session.add(customer)
    db.session.commit()
    db.session.refresh(customer)

    return jsonify({"msg": "Account successfully created!", "customer": customer.serialize()}), 201

# === Customer Login Route ===
@api.route('/customer/login', methods=['POST'])
def handle_customer_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is None or password is None:
        return jsonify({"msg": "No email or password"}), 400

    customer = Customer.query.filter_by(email=email).one_or_none()
    if customer is None:
        return jsonify({"msg": "No such user"}), 404
    if customer.password != password:
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=customer.id, additional_claims={"role": "customer"})
    return jsonify(access_token=access_token, customer_id=customer.id), 201

# === Edit Customer Info by ID (Admin only) ===
@api.route('/customer/edit/<int:cust_id>', methods=['PUT'])
@admin_required()
def handle_customer_edit(cust_id):
    email = request.json.get("email")
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    address = request.json.get("address")
    phone = request.json.get("phone")
    
    if email is None or first_name is None or last_name is None or address is None or phone is None:
        return jsonify({"msg": "Some fields are missing in your request"}), 400

    customer = Customer.query.filter_by(id=cust_id).one_or_none()
    if customer is None:
        return jsonify({"msg": "No customer found"}), 404

    customer.email = email
    customer.first_name = first_name
    customer.last_name = last_name
    customer.address = address
    customer.phone = phone
    db.session.commit()
    db.session.refresh(customer)

    return jsonify({"msg": "Account successfully edited!", "customer": customer.serialize()}), 201

# === Customer Self-Edit Route ===
@api.route('/customer/edit-by-customer', methods=['PUT'])
@jwt_required()
def handle_customer_edit_by_customer():
    email = request.json.get("email")
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    address = request.json.get("address")
    phone = request.json.get("phone")
    
    if email is None or first_name is None or last_name is None or address is None or phone is None:
        return jsonify({"msg": "Some fields are missing in your request"}), 400

    customer = Customer.query.filter_by(id=get_jwt_identity()).first()
    if customer is None:
        return jsonify({"msg": "No customer found"}), 404

    customer.email = email
    customer.first_name = first_name
    customer.last_name = last_name
    customer.address = address
    customer.phone = phone
    db.session.commit()
    db.session.refresh(customer)

    return jsonify({"msg": "Account successfully updated!"}), 200

# === Delete Customer by ID (Admin only) ===
@api.route('/customer/delete/<int:cust_id>', methods=['DELETE'])
@admin_required()
def delete(cust_id):
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if user is None:
        return jsonify({"msg": "This feature is only available to authorized staff"}), 401
    
    customer = Customer.query.get(cust_id)
    if customer is None:
        return jsonify({"msg": "This customer does not exist"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({"msg": "Account deleted successfully"}), 204

# Sitemap for the blueprint API
@api.route('/')
def sitemap():
    return generate_sitemap(api)
