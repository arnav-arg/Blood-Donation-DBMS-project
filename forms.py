from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
import phonenumbers

BLOOD_TYPES = [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
               ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')]

def validate_phone(form, field):
    try:
        input_number = phonenumbers.parse(field.data, "IN")  # Assuming Indian phone numbers
        if not phonenumbers.is_valid_number(input_number):
            raise ValidationError('Invalid phone number.')
    except:
        raise ValidationError('Invalid phone number format.')

class DonorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    blood_type = SelectField('Blood Type', choices=BLOOD_TYPES, validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), validate_phone])
    address = TextAreaField('Address', validators=[Length(max=255)])
    medical_complications = TextAreaField('Medical Complications')

class AcceptorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    blood_type = SelectField('Blood Type', choices=BLOOD_TYPES, validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired(), validate_phone])
    address = TextAreaField('Address', validators=[Length(max=255)])
    health_condition = TextAreaField('Health Condition')

class BloodBankForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=255)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), validate_phone])

class DonationForm(FlaskForm):
    donor_id = SelectField('Donor', coerce=int, validators=[DataRequired()])
    donation_date = DateField('Donation Date', validators=[DataRequired()])
    quantity = DecimalField('Quantity (in units)', validators=[DataRequired(), NumberRange(min=0)])
    blood_bank_id = SelectField('Blood Bank', coerce=int, validators=[DataRequired()])

class BloodStockForm(FlaskForm):
    blood_bank_id = SelectField('Blood Bank', coerce=int, validators=[DataRequired()])
    blood_type = SelectField('Blood Type', choices=BLOOD_TYPES, validators=[DataRequired()])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0)])

class TransactionForm(FlaskForm):
    donation_id = SelectField('Donation', coerce=int, validators=[DataRequired()])
    acceptor_id = SelectField('Acceptor', coerce=int, validators=[DataRequired()])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0)])

class HealthcareCenterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=255)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), validate_phone])

class CenterAffiliationForm(FlaskForm):
    blood_bank_id = SelectField('Blood Bank', coerce=int, validators=[DataRequired()])
    center_id = SelectField('Healthcare Center', coerce=int, validators=[DataRequired()])