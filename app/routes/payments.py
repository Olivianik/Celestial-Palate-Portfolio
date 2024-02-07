from flask import Flask, jsonify, request, Blueprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from datetime import datetime
from app.database import DBSession
from datab import Payment, Base, Customer

app = Flask(__name__)

payments = Blueprint('payments', __name__)


@payments.route('/', methods=['GET'])
def all_payments():
    session = DBSession()
    payments = session.query(Payment).options(
        joinedload(Payment.customer)).all()
    payment_list = [
        {
            'id': p.id,
            'customer_id': p.customer_id,
            'amount': p.amount,
            'status': p.status,
            'created_at': p.created_at,
            'updated_at': p.updated_at
        }
        for p in payments
    ]
    session.close()
    return jsonify(payments=payment_list)


@payments.route('<payment_id>', methods=['GET'])
def get_payment(payment_id):
    session = DBSession()
    payment = session.query(Payment).filter_by(id=payment_id).first()
    session.close()

    if payment:
        payment_info = {
            'id': payment.id,
            'customer_id': payment.customer_id,
            'amount': payment.amount,
            'status': payment.status,
            'created_at': payment.created_at,
            'updated_at': payment.updated_at
        }
        return jsonify(payment=payment_info)
    else:
        return jsonify(message="Payment not found"), 404


@payments.route('/<string:customer_id>/payments', methods=['POST'])
def create_payment(customer_id):
    if request.method == 'POST':
        session = DBSession()

        customer = session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            session.close()
            return jsonify(message=f"Customer with id {customer_id} not found"), 404

        if not request.json or 'amount' not in request.json or 'status' not in request.json:
            session.close()
            return jsonify(message="Invalid JSON data"), 400

        new_payment = Payment(
            customer_id=customer_id,
            amount=request.json['amount'],
            status=request.json['status'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(new_payment)
        session.commit()
        session.close()

        return jsonify(message="Payment created successfully"), 201



@payments.route('/<payment_id>', methods=['PUT'])
def update_payment(payment_id):
    session = DBSession()
    payment = session.query(Payment).filter_by(id=payment_id).first()
    if payment:
        if request.json:
            payment.amount = request.json.get('amount')
            payment.status = request.json.get('status')
        payment.updated_at = datetime.utcnow() # type: ignore
        session.commit()
        session.close()
        return jsonify(message="Payment updated successfully")
    else:
        session.close()
        return jsonify(message="Payment not found"), 404