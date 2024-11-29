from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Person, Donation, Receive, Stock
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_donation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # for flash messages

db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# Person CRUD
# Route for listing persons
# Route for listing persons with optional search
@app.route('/person', methods=['GET', 'POST'])
def person_list():
    search_query = request.args.get('search')  # Get the search term from the query string

    if search_query:
        # If there's a search query, filter persons by name or phone
        persons = Person.query.filter(
            (Person.name.ilike(f'%{search_query}%')) | 
            (Person.phone.ilike(f'%{search_query}%'))
        ).all()
    else:
        # If no search query, just return all persons
        persons = Person.query.all()

    return render_template('person.html', persons=persons, search_query=search_query)

# Route for adding a new person
@app.route('/person/add', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        new_person = Person(
            name=request.form['name'],
            phone=request.form['phone'],
            gender=request.form['gender'],
            blood_group=request.form['blood_group'],
            address=request.form['address'],
            med_issues=request.form['med_issues'],
            dob=datetime.strptime(request.form['dob'], '%Y-%m-%d')
        )
        db.session.add(new_person)
        db.session.commit()
        return redirect(url_for('person_list'))
    
    return render_template('add_person.html')

@app.route('/person/edit/<int:id>', methods=['GET', 'POST'])
def edit_person(id):
    person = Person.query.get_or_404(id)
    if request.method == 'POST':
        person.name = request.form['name']
        person.phone = request.form['phone']
        person.gender = request.form['gender']
        person.blood_group = request.form['blood_group']
        person.address = request.form['address']
        person.med_issues = request.form['med_issues']
        person.dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        db.session.commit()
        return redirect(url_for('person_list'))
    
    return render_template('person_edit.html', person=person)

@app.route('/person/delete/<int:id>')
def delete_person(id):
    person = Person.query.get_or_404(id)
    db.session.delete(person)
    db.session.commit()
    return redirect(url_for('person_list'))

# Donations CRUD
@app.route('/donation', methods=['GET', 'POST'])
def donation_list():
    search_query = request.args.get('search')  # Get the search query from the URL

    if request.method == 'POST':
        person = Person.query.get(request.form['person_id'])
        if not person:
            flash('Invalid person selected')
            return redirect(url_for('donation_list'))
        
        new_donation = Donation(
            person_id=request.form['person_id'],
            quantity=float(request.form['quantity'])
        )
        db.session.add(new_donation)
        
        # Update stock
        stock = Stock.query.filter_by(blood_group=person.blood_group).first()
        if not stock:
            stock = Stock(blood_group=person.blood_group, quantity=0)
            db.session.add(stock)
        stock.quantity += new_donation.quantity
        
        db.session.commit()
        return redirect(url_for('donation_list'))
    
    # Apply search filtering if search query exists
    if search_query:
        donations = Donation.query.join(Person).filter(
            (Person.name.ilike(f'%{search_query}%')) | 
            (Person.phone.ilike(f'%{search_query}%'))
        ).all()
    else:
        donations = Donation.query.all()

    persons = Person.query.all()
    return render_template('donation.html', donations=donations, persons=persons, search_query=search_query)

@app.route('/donation/edit/<int:id>', methods=['GET', 'POST'])
def edit_donation(id):
    donation = Donation.query.get_or_404(id)
    if request.method == 'POST':
        old_quantity = donation.quantity
        new_quantity = float(request.form['quantity'])
        donation.quantity = new_quantity
        
        # Update stock
        person = donation.person
        stock = Stock.query.filter_by(blood_group=person.blood_group).first()
        stock.quantity += (new_quantity - old_quantity)
        
        db.session.commit()
        return redirect(url_for('donation_list'))
    
    persons = Person.query.all()
    return render_template('donation_edit.html', donation=donation, persons=persons)

@app.route('/donation/delete/<int:id>')
def delete_donation(id):
    donation = Donation.query.get_or_404(id)
    
    # Reduce stock
    stock = Stock.query.filter_by(blood_group=donation.person.blood_group).first()
    stock.quantity = max(0, stock.quantity - donation.quantity)
    
    db.session.delete(donation)
    db.session.commit()
    return redirect(url_for('donation_list'))

# Receive CRUD (similar pattern to Donation)
@app.route('/receive', methods=['GET', 'POST'])
def receive_list():
    search_query = request.args.get('search')  # Get the search query from the URL

    if request.method == 'POST':
        person = Person.query.get(request.form['person_id'])
        if not person:
            flash('Invalid person selected')
            return redirect(url_for('receive_list'))
        
        quantity = float(request.form['quantity'])
        
        # Check stock availability
        stock = Stock.query.filter_by(blood_group=person.blood_group).first()
        if not stock or stock.quantity < quantity:
            flash('Insufficient blood stock')
            return redirect(url_for('receive_list'))
        
        new_receive = Receive(
            person_id=request.form['person_id'],
            quantity=quantity
        )
        db.session.add(new_receive)
        
        # Reduce stock
        stock.quantity -= quantity
        
        db.session.commit()
        return redirect(url_for('receive_list'))
    
    # Apply search filtering if search query exists
    if search_query:
        receives = Receive.query.join(Person).filter(
            (Person.name.ilike(f'%{search_query}%')) | 
            (Person.phone.ilike(f'%{search_query}%'))
        ).all()
    else:
        receives = Receive.query.all()

    persons = Person.query.all()
    return render_template('receive.html', receives=receives, persons=persons, search_query=search_query)

@app.route('/receive/edit/<int:id>', methods=['GET', 'POST'])
def edit_receive(id):
    receive = Receive.query.get_or_404(id)
    if request.method == 'POST':
        old_quantity = receive.quantity
        new_quantity = float(request.form['quantity'])
        receive.quantity = new_quantity
        
        # Update stock
        person = receive.person
        stock = Stock.query.filter_by(blood_group=person.blood_group).first()
        stock.quantity += (old_quantity - new_quantity)  # Increase stock by the reduced quantity
        
        db.session.commit()
        return redirect(url_for('receive_list'))
    
    persons = Person.query.all()
    return render_template('receive_edit.html', receive=receive, persons=persons)

@app.route('/receive/delete/<int:id>')
def delete_receive(id):
    receive = Receive.query.get_or_404(id)
    
    # Increase stock
    stock = Stock.query.filter_by(blood_group=receive.person.blood_group).first()
    stock.quantity += receive.quantity  # Add the received quantity back to stock
    
    db.session.delete(receive)
    db.session.commit()
    return redirect(url_for('receive_list'))

# Stock View (Read-only)
@app.route('/stock')
def stock_view():
    stocks = Stock.query.all()
    return render_template('stock.html', stocks=stocks)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)