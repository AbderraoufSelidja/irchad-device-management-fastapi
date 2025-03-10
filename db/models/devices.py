from sqlalchemy import Column, ForeignKey, Integer, Boolean, String, Float, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from ..db_setup import Base
from datetime import datetime, date
from enum import Enum as PyEnum  

# Définition des énumérations

class SoftwareVersionEnum(str, PyEnum):
    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"
    V2_0 = "2.0"


class DeviceTypeEnum(str, PyEnum):
    CEINTURE = "ceinture"
    CANNE_AUGMENTEE = "canne augmentée"
    LUNETTES_CONNECTEES = "lunettes connectées"

class InitialStateEnum(str, PyEnum):
    NEUF = "neuf"
    RECONDITIONNE = "reconditionné"
    DEFECTUEUX = "défectueux"

class OperationalStatusEnum(str, PyEnum):
    EN_SERVICE = "en service"
    EN_VEILLE = "en veille"
    EN_MAINTENANCE = "en maintenance"

class ConnectionStatusEnum(str, PyEnum):
    EN_LIGNE = "en ligne"
    HORS_LIGNE = "hors ligne"

# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    devices = relationship("Occupation", back_populates="user")

# Device Model
class Device(Base):
    __tablename__ = "device"
    serial_number = Column(Integer, primary_key=True)
    type = Column(Enum(DeviceTypeEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    software_version = Column(Enum(SoftwareVersionEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    image = Column(String, nullable=False) 
    initial_state = Column(Enum(InitialStateEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    mac_address = Column(String, unique=True, nullable=False)
    operational_status = Column(Enum(OperationalStatusEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    connection_status = Column(Enum(ConnectionStatusEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    battery_level = Column(Integer, nullable=False)
    creation_date = Column(Date, nullable=False)
    # Relationships
    user = relationship("Occupation", back_populates="device")
    positions = relationship("Position", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    components = relationship("Component", back_populates="device", cascade="all, delete-orphan")


# Calendar Model
class Calendar(Base):
    __tablename__ = "calendar"

    date = Column(DateTime, primary_key=True, nullable=False, default=datetime.utcnow)
    occupations = relationship("Occupation", back_populates="calendar", cascade="all, delete")

# Occupation Model
class Occupation(Base):
    __tablename__ = "occupation"
    device_serial_number = Column(String, ForeignKey("device.serial_number"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    calendar_date = Column(DateTime, ForeignKey("calendar.date"), primary_key=True, nullable=False)
    occupied = Column(Boolean, default=True, nullable=False) 
    user = relationship("User", back_populates="devices")
    device = relationship("Device", back_populates="user")
    calendar = relationship("Calendar", back_populates="occupations")

# Position Model
class Position(Base):
    __tablename__ = "position"
    id = Column(Integer, primary_key=True, index=True)
    device_serial_number = Column(Integer, ForeignKey("device.serial_number"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    occupation_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    position_name = Column(String, nullable=True)
    device = relationship("Device", back_populates="positions")
    


# Alert Model
class Alert(Base):
    __tablename__ = "alert"
    id = Column(Integer, primary_key=True, index=True)
    device_serial_number = Column(Integer, ForeignKey("device.serial_number"), nullable=False)
    message = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    device = relationship("Device", back_populates="alerts")



# Component Model
class Component(Base):
    __tablename__ = "component"
    
    id = Column(Integer, primary_key=True, index=True)
    device_serial_number = Column(Integer, ForeignKey("device.serial_number"), nullable=False)
    type = Column(String, nullable=False)  # Correspond au type du composant
    
    device = relationship("Device", back_populates="components")