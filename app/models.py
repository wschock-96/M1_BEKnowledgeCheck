from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Relationship
from sqlalchemy import Date, String, Float, ForeignKey, Column
import datetime
from app.extensions import db, Base

# class Base(DeclarativeBase):
#     pass


ticket_mechanic = db.Table(
    'ticket_mechanic',
    Base.metadata,
    Column('ticket_id', ForeignKey('service_tickets.id')),
    Column('mechanic_id', ForeignKey('mechanics.id'))
)

class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(17))

    tickets: Mapped[list['ServiceTicket']] = Relationship(back_populates='customer')

class ServiceTicket(Base):
    __tablename__ = 'service_tickets'
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
    service_desc: Mapped[str] = mapped_column(String(500), nullable=False)

    customer: Mapped['Customer'] = Relationship(back_populates='tickets')
    mechanics: Mapped[list['Mechanic']] = Relationship(secondary=ticket_mechanic, back_populates='tickets')

class Mechanic(Base):
    __tablename__ = 'mechanics'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    passwords: Mapped[str] = mapped_column(String(200), nullable=False)

    tickets: Mapped[list['ServiceTicket']] = Relationship(secondary=ticket_mechanic, back_populates='mechanics')
