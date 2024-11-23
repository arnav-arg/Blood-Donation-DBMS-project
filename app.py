# imports
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import BloodDonationSystem, BloodType, Donor, Acceptor, BloodBank, Donation, Transaction
from functools import wraps
import os
from werkzeug.security import generate_password_hash, check_password_hash

#---------------------------------------------------------------------------------------------------------------

# Basic initialisation
app = Flask(__name__)
app.secret_key = os.urandom(24)
system = BloodDonationSystem()

#---------------------------------------------------------------------------------------------------------------

# routes
@app.route('/')
def index():
    # stats
    stats = {
        'donor_count': system.session.query(Donor).count(),
        'acceptor_count': system.session.query(Acceptor).count(),
        'donation_count': system.session.query(Donation).count(),
        'transaction_count': system.session.query(Transaction).count(),
    }
    
    # Get recent donations
    recent_donations = system.session.query(Donation).order_by(Donation.created_at.desc()).limit(5).all()
    
    # Get blood stock levels
    stock_levels = system.get_blood_stock_levels()
    
    return render_template('index.html', stats=stats, recent_donations=recent_donations, stock_levels=stock_levels)

# Donor routes
@app.route('/donors')
def donors():
    donors = system.session.query(Donor).all()
    return render_template('donors/index.html', donors=donors)

@app.route('/donors/new', methods=['GET', 'POST'])
def new_donor():
    if request.method == 'POST':
        try:
            # Create the new donor
            donor = system.add_donor(
                name=request.form['name'],
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
                blood_type=request.form['blood_type'],
                contact_number=request.form['contact_number'],
                address=request.form['address'],
                medical_complications=request.form['medical_complications']
            )
            
            # Get the Donor_ID of the newly added donor
            donor_id = donor.donor_id  # Assuming your add_donor method returns the created donor object
            
            # Flash the success message with Donor_ID
            flash(f'Donor added successfully! Donor ID: {donor_id}', 'success')
            return redirect(url_for('donors'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('donors/new.html', blood_types=[bt.value for bt in BloodType])

@app.route('/donors/<int:donor_id>/edit', methods=['GET', 'POST'])
def edit_donor(donor_id):
    donor = system.session.query(Donor).get(donor_id)
    
    if request.method == 'POST':
        try:
            donor.name = request.form['name']
            donor.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            donor.blood_type = request.form['blood_type']
            donor.contact_number = request.form['contact_number']
            donor.address = request.form['address']
            donor.medical_complications = request.form['medical_complications']
            
            system.session.commit()
            flash('Donor updated successfully!', 'success')
            return redirect(url_for('donors'))
        except Exception as e:
            flash(str(e), 'danger')
            
    return render_template('donors/edit.html', 
                         donor=donor, 
                         blood_types=[bt.value for bt in BloodType])

@app.route('/donors/<int:donor_id>/delete', methods=['POST'])
def delete_donor(donor_id):
    try:
        donor = system.session.query(Donor).get(donor_id)
        system.session.delete(donor)
        system.session.commit()
        flash('Donor deleted successfully!', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('donors'))

# Acceptor routes
@app.route('/acceptors')
def acceptors():
    acceptors = system.session.query(Acceptor).all()
    return render_template('acceptors/index.html', acceptors=acceptors)

@app.route('/acceptors/new', methods=['GET', 'POST'])
def new_acceptor():
    if request.method == 'POST':
        try:
            # Create the new acceptor
            acceptor = system.add_acceptor(
                name=request.form['name'],
                blood_type=request.form['blood_type'],
                contact_number=request.form['contact_number'],
                address=request.form['address'],
                health_condition=request.form['health_condition']
            )
            
            # Get the Donor_ID of the newly added acceptor
            acceptor_id = acceptor.acceptor_id  # Assuming your add_donor method returns the created acceptor object
            
            # Flash the success message with Acceptor_ID
            flash(f'Acceptor added successfully! Acceptor ID: {acceptor_id}', 'success')
            return redirect(url_for('acceptors'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('acceptors/new.html', blood_types=[bt.value for bt in BloodType])


@app.route('/acceptors/<int:acceptor_id>/edit', methods=['GET', 'POST'])
def edit_acceptor(acceptor_id):
    acceptor = system.session.query(Acceptor).get(acceptor_id)
    
    if request.method == 'POST':
        try:
            acceptor.name = request.form['name']
            acceptor.blood_type = request.form['blood_type']
            acceptor.contact_number = request.form['contact_number']
            acceptor.address = request.form['address']
            acceptor.health_condition = request.form['health_condition']
            
            system.session.commit()
            flash('Acceptor updated successfully!', 'success')
            return redirect(url_for('acceptors'))
        except Exception as e:
            flash(str(e), 'danger')
            
    return render_template('acceptors/edit.html', 
                         acceptor=acceptor, 
                         blood_types=[bt.value for bt in BloodType])

@app.route('/acceptors/<int:acceptor_id>/delete', methods=['POST'])
def delete_acceptor(acceptor_id):
    try:
        acceptor = system.session.query(Acceptor).get(acceptor_id)
        system.session.delete(acceptor)
        system.session.commit()
        flash('Acceptor deleted successfully!', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('acceptors'))


# Donation routes
@app.route('/donations')
def donations():
    donations = system.session.query(Donation).all()
    return render_template('donations/index.html', donations=donations)

@app.route('/donations/new', methods=['GET', 'POST'])
def new_donation():
    if request.method == 'POST':
        try:
            system.record_donation(
                donor_id=int(request.form['donor_id']),
                blood_bank_id=int(request.form['blood_bank_id']),
                quantity=float(request.form['quantity']),
                donation_date=datetime.strptime(request.form['donation_date'], '%Y-%m-%d').date()
            )
            flash('Donation recorded successfully', 'success')
            return redirect(url_for('donations'))
        except Exception as e:
            flash(str(e), 'danger')
    
    donors = system.session.query(Donor).all()
    blood_banks = system.session.query(BloodBank).all()
    return render_template('donations/new.html', donors=donors, blood_banks=blood_banks)

# Blood Bank routes
@app.route('/blood-banks')
def blood_banks():
    blood_banks = system.session.query(BloodBank).all()
    return render_template('blood_banks/index.html', blood_banks=blood_banks)

@app.route('/blood-banks/new', methods=['GET', 'POST'])
def new_blood_bank():
    if request.method == 'POST':
        try:
            blood_bank = BloodBank(
                name=request.form['name'],
                location=request.form['location'],
                contact_number=request.form['contact_number']
            )
            system.session.add(blood_bank)
            system.session.commit()
            flash('Blood bank added successfully', 'success')
            return redirect(url_for('blood_banks'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('blood_banks/new.html')

# Stock routes
@app.route('/blood-stocks')
def blood_stocks():
    stock_levels = system.get_blood_stock_levels()
    return render_template('blood_stocks/index.html', stock_levels=stock_levels)

if __name__ == '__main__':
    app.run(debug=True)