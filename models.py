from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, Numeric, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

# Create database engine
engine = create_engine('sqlite:///blood_donation.db', echo=True)
Base = declarative_base()

# Helper class for blood types
class BloodType(enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"

# Models
class Donor(Base):
    __tablename__ = 'donors'
    
    donor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    blood_type = Column(String(3), nullable=False)
    contact_number = Column(String(15), nullable=False)
    address = Column(String(255))
    medical_complications = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    donations = relationship("Donation", back_populates="donor")
    
    __table_args__ = (
        CheckConstraint(
            blood_type.in_([bt.value for bt in BloodType]),
            name='valid_blood_type'
        ),
    )

class Acceptor(Base):
    __tablename__ = 'acceptors'
    
    acceptor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    blood_type = Column(String(3), nullable=False)
    contact_number = Column(String(15), nullable=False)
    address = Column(String(255))
    health_condition = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    transactions = relationship("Transaction", back_populates="acceptor")
    
    __table_args__ = (
        CheckConstraint(
            blood_type.in_([bt.value for bt in BloodType]),
            name='valid_blood_type'
        ),
    )

class BloodBank(Base):
    __tablename__ = 'blood_banks'
    
    blood_bank_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    contact_number = Column(String(15), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    stocks = relationship("BloodStock", back_populates="blood_bank")
    donations = relationship("Donation", back_populates="blood_bank")
    affiliations = relationship("CenterAffiliation", back_populates="blood_bank")

class Donation(Base):
    __tablename__ = 'donations'
    
    donation_id = Column(Integer, primary_key=True, autoincrement=True)
    donor_id = Column(Integer, ForeignKey('donors.donor_id'), nullable=False)
    donation_date = Column(Date, nullable=False)
    quantity = Column(Numeric(5, 2), nullable=False)
    blood_bank_id = Column(Integer, ForeignKey('blood_banks.blood_bank_id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    donor = relationship("Donor", back_populates="donations")
    blood_bank = relationship("BloodBank", back_populates="donations")
    transactions = relationship("Transaction", back_populates="donation")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='positive_quantity'),
        CheckConstraint('donation_date <= CURRENT_DATE', name='valid_donation_date'),
    )

class BloodStock(Base):
    __tablename__ = 'blood_stocks'
    
    stock_id = Column(Integer, primary_key=True, autoincrement=True)
    blood_bank_id = Column(Integer, ForeignKey('blood_banks.blood_bank_id'), nullable=False)
    blood_type = Column(String(3), nullable=False)
    quantity = Column(Numeric(5, 2), nullable=False)
    last_updated = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    blood_bank = relationship("BloodBank", back_populates="stocks")
    
    __table_args__ = (
        CheckConstraint(
            blood_type.in_([bt.value for bt in BloodType]),
            name='valid_blood_type'
        ),
        CheckConstraint('quantity >= 0', name='non_negative_quantity'),
    )

class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    donation_id = Column(Integer, ForeignKey('donations.donation_id', ondelete='CASCADE'), nullable=False)
    acceptor_id = Column(Integer, ForeignKey('acceptors.acceptor_id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    quantity = Column(Numeric(5, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # You can also modify the relationship to include cascade options
    donation = relationship("Donation", back_populates="transactions", cascade="all, delete")
    acceptor = relationship("Acceptor", back_populates="transactions", cascade="all, delete")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='positive_quantity'),
        CheckConstraint('date <= CURRENT_DATE', name='valid_transaction_date'),
    )

class HealthcareCenter(Base):
    __tablename__ = 'healthcare_centers'
    
    center_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    contact_number = Column(String(15), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    affiliations = relationship("CenterAffiliation", back_populates="healthcare_center")

class CenterAffiliation(Base):
    __tablename__ = 'center_affiliations'
    
    affiliation_id = Column(Integer, primary_key=True, autoincrement=True)
    blood_bank_id = Column(Integer, ForeignKey('blood_banks.blood_bank_id'), nullable=False)
    center_id = Column(Integer, ForeignKey('healthcare_centers.center_id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    blood_bank = relationship("BloodBank", back_populates="affiliations")
    healthcare_center = relationship("HealthcareCenter", back_populates="affiliations")

# Create database tables
Base.metadata.create_all(engine)

# Create session factory
Session = sessionmaker(bind=engine)

# Helper functions for common operations
class BloodDonationSystem:
    def __init__(self):
        self.session = Session()
    
    def add_donor(self, name, date_of_birth, blood_type, contact_number, address=None, medical_complications=None):
        donor = Donor(
            name=name,
            date_of_birth=date_of_birth,
            blood_type=blood_type,
            contact_number=contact_number,
            address=address,
            medical_complications=medical_complications
        )
        self.session.add(donor)
        self.session.commit()
        return donor
    
    def add_acceptor(self, name, blood_type, contact_number, address=None, health_condition=None):
        acceptor = Acceptor(
            name=name,
            blood_type=blood_type,
            contact_number=contact_number,
            address=address,
            health_condition=health_condition
        )
        self.session.add(acceptor)
        self.session.commit()
        return acceptor
    
    def record_donation(self, donor_id, blood_bank_id, quantity, donation_date=None):
        if donation_date is None:
            donation_date = datetime.now().date()
            
        donation = Donation(
            donor_id=donor_id,
            blood_bank_id=blood_bank_id,
            quantity=quantity,
            donation_date=donation_date
        )
        self.session.add(donation)
        
        # Update blood stock
        stock = self.session.query(BloodStock).filter(
            BloodStock.blood_bank_id == blood_bank_id,
            BloodStock.blood_type == self.session.query(Donor.blood_type).filter(Donor.donor_id == donor_id).scalar()
        ).first()
        
        if stock:
            stock.quantity += quantity
            stock.last_updated = datetime.now().date()
        else:
            stock = BloodStock(
                blood_bank_id=blood_bank_id,
                blood_type=self.session.query(Donor.blood_type).filter(Donor.donor_id == donor_id).scalar(),
                quantity=quantity,
                last_updated=datetime.now().date()
            )
            self.session.add(stock)
            
        self.session.commit()
        return donation
    
    def process_transaction(self, donation_id, acceptor_id, quantity, date=None):
        if date is None:
            date = datetime.now().date()
            
        transaction = Transaction(
            donation_id=donation_id,
            acceptor_id=acceptor_id,
            quantity=quantity,
            date=date
        )
        self.session.add(transaction)
        
        # Update blood stock
        donation = self.session.query(Donation).get(donation_id)
        stock = self.session.query(BloodStock).filter(
            BloodStock.blood_bank_id == donation.blood_bank_id,
            BloodStock.blood_type == donation.donor.blood_type
        ).first()
        
        if stock:
            if stock.quantity >= quantity:
                stock.quantity -= quantity
                stock.last_updated = datetime.now().date()
                self.session.commit()
                return transaction
            else:
                self.session.rollback()
                raise ValueError("Insufficient blood stock")
        else:
            self.session.rollback()
            raise ValueError("Blood stock not found")
    
    def get_blood_stock_levels(self, blood_bank_id=None):
        query = self.session.query(BloodStock)
        if blood_bank_id:
            query = query.filter(BloodStock.blood_bank_id == blood_bank_id)
        return query.all()
    
    def close(self):
        self.session.close()

# Example usage
if __name__ == "__main__":
    system = BloodDonationSystem()
    
    # Add a donor
    donor = system.add_donor(
        name="John Doe",
        date_of_birth=datetime(1990, 1, 1).date(),
        blood_type="A+",
        contact_number="1234567890",
        address="123 Main St"
    )
    
    # Add a blood bank
    blood_bank = BloodBank(
        name="Central Blood Bank",
        location="Downtown",
        contact_number="9876543210"
    )
    system.session.add(blood_bank)
    system.session.commit()
    
    # Record a donation
    donation = system.record_donation(
        donor_id=donor.donor_id,
        blood_bank_id=blood_bank.blood_bank_id,
        quantity=0.5
    )
    
    # Check blood stock levels
    stock_levels = system.get_blood_stock_levels()
    for stock in stock_levels:
        print(f"Blood Type: {stock.blood_type}, Quantity: {stock.quantity}L")
    
    system.close()