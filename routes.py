from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, Donor, Acceptor, BloodBank, Donation, BloodStock, Transaction, HealthcareCenter, CenterAffiliation
from forms import (DonorForm, AcceptorForm, BloodBankForm, DonationForm, BloodStockForm,
                  TransactionForm, HealthcareCenterForm, CenterAffiliationForm)
from datetime import date

main = Blueprint('main', __name__)

# Donor routes
@main.route('/donor')
def donor_list():
    donors = Donor.query.all()
    return render_template('donor/list.html', donors=donors)

@main.route('/donor/new', methods=['GET', 'POST'])
def donor_create():
    form = DonorForm()
    if form.validate_on_submit():
        donor = Donor(
            Name=form.name.data,
            Date_Of_Birth=form.date_of_birth.data,
            Blood_Type=form.blood_type.data,
            Contact_Number=form.contact_number.data,
            Address=form.address.data,
            Medical_Complications=form.medical_complications.data
        )
        db.session.add(donor)
        db.session.commit()
        flash('Donor added successfully!', 'success')
        return redirect(url_for('main.donor_list'))
    return render_template('donor/form.html', form=form, title='New Donor')

@main.route('/donor/<int:id>/edit', methods=['GET', 'POST'])
def donor_edit(id):
    donor = Donor.query.get_or_404(id)
    form = DonorForm(obj=donor)
    if form.validate_on_submit():
        donor.Name = form.name.data
        donor.Date_Of_Birth = form.date_of_birth.data
        donor.Blood_Type = form.blood_type.data
        donor.Contact_Number = form.contact_number.data
        donor.Address = form.address.data
        donor.Medical_Complications = form.medical_complications.data
        db.session.commit()
        flash('Donor updated successfully!', 'success')
        return redirect(url_for('main.donor_list'))
    return render_template('donor/form.html', form=form, title='Edit Donor')

@main.route('/donor/<int:id>/delete', methods=['POST'])
def donor_delete(id):
    donor = Donor.query.get_or_404(id)
    db.session.delete(donor)
    db.session.commit()
    flash('Donor deleted successfully!', 'success')
    return redirect(url_for('main.donor_list'))

# Donation routes
@main.route('/donation')
def donation_list():
    donations = Donation.query.all()
    return render_template('donation/list.html', donations=donations)

@main.route('/donation/new', methods=['GET', 'POST'])
def donation_create():
    form = DonationForm()
    form.donor_id.choices = [(d.Donor_ID, d.Name) for d in Donor.query.all()]
    form.blood_bank_id.choices = [(b.Blood_Bank_ID, b.Name) for b in BloodBank.query.all()]
    
    if form.validate_on_submit():
        donation = Donation(
            Donor_ID=form.donor_id.data,
            Donation_Date=form.donation_date.data,
            Quantity=form.quantity.data,
            Blood_Bank_ID=form.blood_bank_id.data
        )
        db.session.add(donation)
        
        # Update blood stock
        donor = Donor.query.get(form.donor_id.data)
        stock = BloodStock.query.filter_by(
            Blood_Bank_ID=form.blood_bank_id.data,
            Blood_Type=donor.Blood_Type
        ).first()
        
        if stock:
            stock.Quantity += form.quantity.data
            stock.Last_Updated = date.today()
        else:
            stock = BloodStock(
                Blood_Bank_ID=form.blood_bank_id.data,
                Blood_Type=donor.Blood_Type,
                Quantity=form.quantity.data,
                Last_Updated=date.today()
            )
            db.session.add(stock)
            
        db.session.commit()
        flash('Donation recorded successfully!', 'success')
        return redirect(url_for('main.donation_list'))
    return render_template('donation/form.html', form=form, title='New Donation')

# Similar routes for other models (Acceptor, BloodBank, Transaction, etc.)
# [Additional routes would follow the same pattern]
# Acceptor routes
@main.route('/acceptor')
def acceptor_list():
    acceptors = Acceptor.query.all()
    return render_template('acceptor/list.html', acceptors=acceptors)

@main.route('/acceptor/new', methods=['GET', 'POST'])
def acceptor_create():
    form = AcceptorForm()
    if form.validate_on_submit():
        acceptor = Acceptor(
            Name=form.name.data,
            Blood_Type=form.blood_type.data,
            Contact_Number=form.contact_number.data,
            Address=form.address.data,
            Health_Condition=form.health_condition.data
        )
        db.session.add(acceptor)
        db.session.commit()
        flash('Acceptor added successfully!', 'success')
        return redirect(url_for('main.acceptor_list'))
    return render_template('acceptor/form.html', form=form, title='New Acceptor')

@main.route('/acceptor/<int:id>/edit', methods=['GET', 'POST'])
def acceptor_edit(id):
    acceptor = Acceptor.query.get_or_404(id)
    form = AcceptorForm(obj=acceptor)
    if form.validate_on_submit():
        acceptor.Name = form.name.data
        acceptor.Blood_Type = form.blood_type.data
        acceptor.Contact_Number = form.contact_number.data
        acceptor.Address = form.address.data
        acceptor.Health_Condition = form.health_condition.data
        db.session.commit()
        flash('Acceptor updated successfully!', 'success')
        return redirect(url_for('main.acceptor_list'))
    return render_template('acceptor/form.html', form=form, title='Edit Acceptor')

@main.route('/acceptor/<int:id>/delete', methods=['POST'])
def acceptor_delete(id):
    acceptor = Acceptor.query.get_or_404(id)
    db.session.delete(acceptor)
    db.session.commit()
    flash('Acceptor deleted successfully!', 'success')
    return redirect(url_for('main.acceptor_list'))

# Blood Bank routes
@main.route('/blood_bank')
def blood_bank_list():
    blood_banks = BloodBank.query.all()
    return render_template('blood_bank/list.html', blood_banks=blood_banks)

@main.route('/blood_bank/new', methods=['GET', 'POST'])
def blood_bank_create():
    form = BloodBankForm()
    if form.validate_on_submit():
        blood_bank = BloodBank(
            Name=form.name.data,
            Location=form.location.data,
            Contact_Number=form.contact_number.data
        )
        db.session.add(blood_bank)
        db.session.commit()
        flash('Blood Bank added successfully!', 'success')
        return redirect(url_for('main.blood_bank_list'))
    return render_template('blood_bank/form.html', form=form, title='New Blood Bank')

@main.route('/blood_bank/<int:id>/edit', methods=['GET', 'POST'])
def blood_bank_edit(id):
    blood_bank = BloodBank.query.get_or_404(id)
    form = BloodBankForm(obj=blood_bank)
    if form.validate_on_submit():
        blood_bank.Name = form.name.data
        blood_bank.Location = form.location.data
        blood_bank.Contact_Number = form.contact_number.data
        db.session.commit()
        flash('Blood Bank updated successfully!', 'success')
        return redirect(url_for('main.blood_bank_list'))
    return render_template('blood_bank/form.html', form=form, title='Edit Blood Bank')

@main.route('/blood_bank/<int:id>/delete', methods=['POST'])
def blood_bank_delete(id):
    blood_bank = BloodBank.query.get_or_404(id)
    db.session.delete(blood_bank)
    db.session.commit()
    flash('Blood Bank deleted successfully!', 'success')
    return redirect(url_for('main.blood_bank_list'))

# Blood Stock routes
@main.route('/blood_stock')
def blood_stock_list():
    blood_stocks = BloodStock.query.all()
    return render_template('blood_stock/list.html', blood_stocks=blood_stocks)

@main.route('/blood_stock/new', methods=['GET', 'POST'])
def blood_stock_create():
    form = BloodStockForm()
    form.blood_bank_id.choices = [(b.Blood_Bank_ID, b.Name) for b in BloodBank.query.all()]
    if form.validate_on_submit():
        blood_stock = BloodStock(
            Blood_Bank_ID=form.blood_bank_id.data,
            Blood_Type=form.blood_type.data,
            Quantity=form.quantity.data,
            Last_Updated=form.last_updated.data
        )
        db.session.add(blood_stock)
        db.session.commit()
        flash('Blood Stock added successfully!', 'success')
        return redirect(url_for('main.blood_stock_list'))
    return render_template('blood_stock/form.html', form=form, title='New Blood Stock')

@main.route('/blood_stock/<int:id>/edit', methods=['GET', 'POST'])
def blood_stock_edit(id):
    blood_stock = BloodStock.query.get_or_404(id)
    form = BloodStockForm(obj=blood_stock)
    form.blood_bank_id.choices = [(b.Blood_Bank_ID, b.Name) for b in BloodBank.query.all()]
    if form.validate_on_submit():
        blood_stock.Blood_Bank_ID = form.blood_bank_id.data
        blood_stock.Blood_Type = form.blood_type.data
        blood_stock.Quantity = form.quantity.data
        blood_stock.Last_Updated = form.last_updated.data
        db.session.commit()
        flash('Blood Stock updated successfully!', 'success')
        return redirect(url_for('main.blood_stock_list'))
    return render_template('blood_stock/form.html', form=form, title='Edit Blood Stock')

@main.route('/blood_stock/<int:id>/delete', methods=['POST'])
def blood_stock_delete(id):
    blood_stock = BloodStock.query.get_or_404(id)
    db.session.delete(blood_stock)
    db.session.commit()
    flash('Blood Stock deleted successfully!', 'success')
    return redirect(url_for('main.blood_stock_list'))

# Transaction routes
@main.route('/transaction')
def transaction_list():
    transactions = Transaction.query.all()
    return render_template('transaction/list.html', transactions=transactions)

@main.route('/transaction/new', methods=['GET', 'POST'])
def transaction_create():
    form = TransactionForm()
    form.donation_id.choices = [(d.Donation_ID, d.Donation_ID) for d in Donation.query.all()]
    form.acceptor_id.choices = [(a.Acceptor_ID, a.Name) for a in Acceptor.query.all()]
    
    if form.validate_on_submit():
        transaction = Transaction(
            Donation_ID=form.donation_id.data,
            Acceptor_ID=form.acceptor_id.data,
            Date=form.date.data,
            Quantity=form.quantity.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction recorded successfully!', 'success')
        return redirect(url_for('main.transaction_list'))
    return render_template('transaction/form.html', form=form, title='New Transaction')

@main.route('/transaction/<int:id>/edit', methods=['GET', 'POST'])
def transaction_edit(id):
    transaction = Transaction.query.get_or_404(id)
    form = TransactionForm(obj=transaction)
    form.donation_id.choices = [(d.Donation_ID, d.Donation_ID) for d in Donation.query.all()]
    form.acceptor_id.choices = [(a.Acceptor_ID, a.Name) for a in Acceptor.query.all()]
    
    if form.validate_on_submit():
        transaction.Donation_ID = form.donation_id.data
        transaction.Acceptor_ID = form.acceptor_id.data
        transaction.Date = form.date.data
        transaction.Quantity = form.quantity.data
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('main.transaction_list'))
    return render_template('transaction/form.html', form=form, title='Edit Transaction')

@main.route('/transaction/<int:id>/delete', methods=['POST'])
def transaction_delete(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('main.transaction_list'))

# Healthcare Center routes
@main.route('/healthcare_center')
def healthcare_center_list():
    centers = HealthcareCenter.query.all()
    return render_template('healthcare_center/list.html', centers=centers)

@main.route('/healthcare_center/new', methods=['GET', 'POST'])
def healthcare_center_create():
    form = HealthcareCenterForm()
    if form.validate_on_submit():
        center = HealthcareCenter(
            Name=form.name.data,
            Location=form.location.data,
            Contact_Number=form.contact_number.data
        )
        db.session.add(center)
        db.session.commit()
        flash('Healthcare Center added successfully!', 'success')
        return redirect(url_for('main.healthcare_center_list'))
    return render_template('healthcare_center/form.html', form=form, title='New Healthcare Center')

@main.route('/healthcare_center/<int:id>/edit', methods=['GET', 'POST'])
def healthcare_center_edit(id):
    center = HealthcareCenter.query.get_or_404(id)
    form = HealthcareCenterForm(obj=center)
    if form.validate_on_submit():
        center.Name = form.name.data
        center.Location = form.location.data
        center.Contact_Number = form.contact_number.data
        db.session.commit()
        flash('Healthcare Center updated successfully!', 'success')
        return redirect(url_for('main.healthcare_center_list'))
    return render_template('healthcare_center/form.html', form=form, title='Edit Healthcare Center')

@main.route('/healthcare_center/<int:id>/delete', methods=['POST'])
def healthcare_center_delete(id):
    center = HealthcareCenter.query.get_or_404(id)
    db.session.delete(center)
    db.session.commit()
    flash('Healthcare Center deleted successfully!', 'success')
    return redirect(url_for('main.healthcare_center_list'))

# Center Affiliation routes
@main.route('/center_affiliation')
def center_affiliation_list():
    affiliations = CenterAffiliation.query.all()
    return render_template('center_affiliation/list.html', affiliations=affiliations)

@main.route('/center_affiliation/new', methods=['GET', 'POST'])
def center_affiliation_create():
    form = CenterAffiliationForm()
    form.healthcare_center_id.choices = [(h.Healthcare_Center_ID, h.Name) for h in HealthcareCenter.query.all()]
    if form.validate_on_submit():
        affiliation = CenterAffiliation(
            Healthcare_Center_ID=form.healthcare_center_id.data,
            Affiliation_Date=form.affiliation_date.data
        )
        db.session.add(affiliation)
        db.session.commit()
        flash('Center Affiliation recorded successfully!', 'success')
        return redirect(url_for('main.center_affiliation_list'))
    return render_template('center_affiliation/form.html', form=form, title='New Center Affiliation')

@main.route('/center_affiliation/<int:id>/edit', methods=['GET', 'POST'])
def center_affiliation_edit(id):
    affiliation = CenterAffiliation.query.get_or_404(id)
    form = CenterAffiliationForm(obj=affiliation)
    form.healthcare_center_id.choices = [(h.Healthcare_Center_ID, h.Name) for h in HealthcareCenter.query.all()]
    if form.validate_on_submit():
        affiliation.Healthcare_Center_ID = form.healthcare_center_id.data
        affiliation.Affiliation_Date = form.affiliation_date.data
        db.session.commit()
        flash('Center Affiliation updated successfully!', 'success')
        return redirect(url_for('main.center_affiliation_list'))
    return render_template('center_affiliation/form.html', form=form, title='Edit Center Affiliation')

@main.route('/center_affiliation/<int:id>/delete', methods=['POST'])
def center_affiliation_delete(id):
    affiliation = CenterAffiliation.query.get_or_404(id)
    db.session.delete(affiliation)
    db.session.commit()
    flash('Center Affiliation deleted successfully!', 'success')
    return redirect(url_for('main.center_affiliation_list'))
