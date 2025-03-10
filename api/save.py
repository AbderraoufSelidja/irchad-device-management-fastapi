import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.db_setup import get_db
from db.models.devices import User, Device, Occupation, Calendar, Position, Alert
from schemas import DeviceCreateBase, DeviceUpdateBase
from datetime import datetime

router = fastapi.APIRouter()


# Récupérer tous les dispositifs
@router.get("/devices")
def display_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    result = []

    for device in devices:
        assigned_user = (
            db.query(User.first_name, User.last_name)
            .join(Occupation, Occupation.user_id == User.id)
            .filter(Occupation.device_serial_number == device.serial_number)
            .order_by(Occupation.calendar_date.desc())
            .first()
        )

        last_position = (
            db.query(Position.position_name)
            .filter(Position.device_serial_number == device.serial_number) 
            .order_by(Position.occupation_timestamp.desc()) 
            .first()
        )

        alert_count = db.query(Alert).filter(Alert.device_serial_number == device.serial_number).count()

        result.append({
            "serial_number": device.serial_number,
            "type": device.type.value, 
            "software_version": device.software_version,
            "initial_state": device.initial_state.value,
            "image": device.image,
            "mac_address": device.mac_address,
            "operational_status": device.operational_status.value,
            "connection_status": device.connection_status.value,  
            "battery_level": device.battery_level,
            "creation_date": device.creation_date,  
            "first_name": assigned_user.first_name if assigned_user else None,
            "last_name": assigned_user.last_name if assigned_user else None,
            "last_position_name": last_position.position_name if last_position else None, 
            "alert_count": alert_count  
        })

    return result



# Récupérer les détails d'un dispositif spécifique
@router.get("/devices/{serial_number}")
def get_device_details(serial_number: int, db: Session = Depends(get_db)): 
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    assigned_user = (
        db.query(User.first_name, User.last_name)
        .join(Occupation, Occupation.user_id == User.id)
        .filter(Occupation.device_serial_number == serial_number)  
        .order_by(Occupation.calendar_date.desc())
        .first()
    )

    last_position = (
        db.query(Position.position_name)
        .filter(Position.device_serial_number == serial_number) 
        .order_by(Position.occupation_timestamp.desc()) 
        .first()
    )
    
    alert_count = db.query(Alert).filter(Alert.device_serial_number == serial_number).count()  

    return {
        "serial_number": device.serial_number,
        "type": device.type.value, 
        "software_version": device.software_version,
        "initial_state": device.initial_state.value,
        "image": device.image,
        "mac_address": device.mac_address,
        "operational_status": device.operational_status.value,
        "connection_status": device.connection_status.value,  
        "battery_level": device.battery_level,
        "creation_date": device.creation_date, 
        "first_name": assigned_user.first_name if assigned_user else None,
        "last_name": assigned_user.last_name if assigned_user else None,
        "last_position_name": last_position.position_name if last_position else None, 
        "alert_count": alert_count  
    }

# Récupérer toutes les occupations d'un dispositif spécifique
@router.get("/devices/{serial_number}/occupations")
def get_device_occupations(serial_number: int, db: Session = Depends(get_db)):
    # Vérifier si le device existe
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Récupérer les occupations du device
    occupations = (
        db.query(Occupation, User.first_name, User.last_name, User.email)
        .join(User, Occupation.user_id == User.id)
        .filter(Occupation.device_serial_number == serial_number)  # Correction ici
        .order_by(Occupation.calendar_date.desc())
        .all()
    )

    # Construire la liste des occupations
    occupation_list = [
        {
            "user_id": occupation.Occupation.user_id,
            "first_name": occupation.first_name,
            "last_name": occupation.last_name,
            "email": occupation.email,
            "calendar_date": occupation.Occupation.calendar_date
        }
        for occupation in occupations
    ]

    return occupation_list


# Récupérer toutes les alertes d'un dispositif spécifique
@router.get("/devices/{serial_number}/alerts")
def get_device_alerts(serial_number: int, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.device_serial_number == serial_number).all()
    
    return [{"id": alert.id, "message": alert.message, "date": alert.date} for alert in alerts]


# Supprimer un dispositif spécifique
@router.delete("/devices/delete/{serial_number}")
def delete_device(serial_number: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    
    return {"message": f"Device with serial number {serial_number} has been deleted successfully"}


# Modifier les informations d'un dispositif spécifique
@router.put("/devices/update/{serial_number}")
def update_device(serial_number: str, device_data: DeviceUpdateBase, db: Session = Depends(get_db)):
        # Vérifier si le device existe
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    # Vérifier si le nouvel utilisateur existe
    new_user = db.query(User).filter(User.id == device_data.user_id).first()
    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Mettre à jour les informations du device
    device.type = device_data.type
    device.software_version = device_data.software_version
    device.image = device_data.image
    device.initial_state = device_data.initial_state
    device.mac_address = device_data.mac_address
    device.operational_status = device_data.operational_status
    device.connection_status = device_data.connection_status
    device.battery_level = device_data.battery_level
    # Vérifier la dernière occupation du device
    last_occupation = (
        db.query(Occupation)
        .filter(Occupation.device_serial_number == serial_number)
        .order_by(Occupation.calendar_date.desc())
        .first()
    )
        # Si l'utilisateur a changé, ajouter une nouvelle occupation
    if not last_occupation or last_occupation.user_id != device_data.user_id:
                # Créer une nouvelle entrée dans le calendrier
        new_calendar_entry = Calendar(date=datetime.now())
        db.add(new_calendar_entry)
        db.commit()
        db.refresh(new_calendar_entry)
        # Ajouter une nouvelle occupation sans supprimer l'ancienne
        new_occupation = Occupation(
            user_id=device_data.user_id,
            device_serial_number=serial_number,
            calendar_date=new_calendar_entry.date
        )
        db.add(new_occupation)

    db.commit()
    db.refresh(device)

    return {
        "message": "Device updated successfully",
        "device": {
            "serial_number": device.serial_number,
            "type": device.type,
            "software_version": device.software_version,
            "initial_state": device.initial_state,
            "image": device.image,
            "mac_address": device.mac_address,
            "operational_status": device.operational_status,
            "connection_status": device.connection_status,
            "battery_level": device.battery_level,
            "user_id": device_data.user_id
        }
    }


# Créer un dispositif
@router.post("/devices/create")
def create_device(device_data: DeviceCreateBase, db: Session = Depends(get_db)):
        # Création du dispositif
    new_device = Device(
        serial_number=device_data.serial_number,
        type=device_data.type,
        software_version=device_data.software_version,
        initial_state=device_data.initial_state,
        image=device_data.image,
        mac_address=device_data.mac_address,
        operational_status=device_data.operational_status,
        connection_status=device_data.connection_status,
        battery_level=device_data.battery_level,
        creation_date=device_data.creation_date  
    )
    
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    # Vérifier si un utilisateur est assigné
    if device_data.user_id is not None:
        calendar_entry = Calendar(date=datetime.now())
        db.add(calendar_entry)
        db.commit()
        db.refresh(calendar_entry)

        new_occupation = Occupation(
            user_id=device_data.user_id,
            device_serial_number=device_data.serial_number,  
            calendar_date=calendar_entry.date
        )
        db.add(new_occupation)
        db.commit()

    return {
        "message": "Device created successfully",
        "device": {
            "serial_number": new_device.serial_number,
            "type": new_device.type,
            "software_version": new_device.software_version,
            "initial_state": new_device.initial_state,  
            "image": new_device.image,
            "mac_address": new_device.mac_address,
            "operational_status": new_device.operational_status,
            "connection_status": new_device.connection_status,
            "battery_level": new_device.battery_level,
            "creation_date": new_device.creation_date, 
            "user_id": device_data.user_id  
        }
    }


# Récupérer tous les utilisateurs
@router.get("/devices/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()




































import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.db_setup import get_db
from db.models.devices import User, Device, Occupation, Calendar, Position, Alert
from schemas import DeviceCreateBase, DeviceUpdateBase
from sqlalchemy import  Date
from datetime import datetime
from db.models.devices import DeviceTypeEnum, InitialStateEnum, OperationalStatusEnum, ConnectionStatusEnum
router = fastapi.APIRouter()



# Récupérer tous les dispositifs avec l'utilisateur associé et la derniere position detecté et le nombre d'alerts associés
@router.get("/devices")
def display_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    result = []

    for device in devices:
        assigned_user = (
            db.query(User.first_name, User.last_name)
            .join(Occupation, Occupation.user_id == User.id)
            .filter(Occupation.device_id == device.id)
            .order_by(Occupation.calendar_date.desc())
            .first()
                    )

        last_position = (
            db.query(Position.position_name)
            .filter(Position.device_id == device.id)
            .order_by(Position.occupation_timestamp.desc()) 
            .first()
        )
        
        alert_count = db.query(Alert).filter(Alert.device_id == device.id).count()


        result.append({
            "id": device.id,
            "type": device.type.value, 
            "software_version": device.software_version,
            "initial_state": device.initial_state.value,
            "image": device.image,
            "mac_address": device.mac_address,
            "operational_status": device.operational_status.value,
            "connection_status": device.connection_status.value,  
            "battery_level": device.battery_level,
            "first_name": assigned_user.first_name if assigned_user else None,
            "last_name": assigned_user.last_name if assigned_user else None,
            "last_position_name": last_position.position_name if last_position else None , 
            "alert_count": alert_count  
        })

    return result


# Récupérer les détails d'un dispositif spécifique
@router.get("/devices/{device_id}")
def get_device_details(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    assigned_user = (
        db.query(User.first_name, User.last_name)
        .join(Occupation, Occupation.user_id == User.id)
        .filter(Occupation.device_id == device.id)
        .order_by(Occupation.calendar_date.desc())
        .first()
    )

    last_position = (
        db.query(Position.position_name)
        .filter(Position.device_id == device.id)
        .order_by(Position.occupation_timestamp.desc()) 
        .first()
    )
    
    alert_count = db.query(Alert).filter(Alert.device_id == device.id).count()

    return {
        "id": device.id,
        "type": device.type.value, 
        "software_version": device.software_version,
        "initial_state": device.initial_state.value,
        "image": device.image,
        "mac_address": device.mac_address,
        "operational_status": device.operational_status.value,
        "connection_status": device.connection_status.value,  
        "battery_level": device.battery_level,
        "first_name": assigned_user.first_name if assigned_user else None,
        "last_name": assigned_user.last_name if assigned_user else None,
        "last_position_name": last_position.position_name if last_position else None, 
        "alert_count": alert_count  
    }

# Récupérer toutes les occupations d'un dispositif spécifique

@router.get("/devices/{device_id}/occupations")
def get_device_occupations(device_id: int, db: Session = Depends(get_db)):
    # Vérifier si le device existe
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Récupérer les occupations du device
    occupations = (
        db.query(Occupation, User.first_name, User.last_name, User.email)
        .join(User, Occupation.user_id == User.id)
        .filter(Occupation.device_id == device_id)
        .order_by(Occupation.calendar_date.desc())
        .all()
    )

    # Construire la liste des occupations
    occupation_list = [
        {
            "user_id": occupation.Occupation.user_id,
            "first_name": occupation.first_name,
            "last_name": occupation.last_name,
            "email": occupation.email,
            "calendar_date": occupation.Occupation.calendar_date
        }
        for occupation in occupations
    ]

    return occupation_list




# Récupérer toutes les alertes d'un dispositif spécifique
@router.get("/devices/{device_id}/alerts")
def get_device_alerts(device_id: int, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.device_id == device_id).all()
    
    return [{"id": alert.id, "message": alert.message, "date": alert.date} for alert in alerts]


# Supprimer un device specifique

@router.delete("/devices/delete/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(device)
    db.commit()
    
    return {"message": f"Device with ID {device_id} has been deleted successfully"}


# Modifier les informations d'un device specifique
@router.put("/devices/update/{device_id}")
def update_device(device_id: int, device_data: DeviceUpdateBase, db: Session = Depends(get_db)):
    # Vérifier si le device existe
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Vérifier si le nouvel utilisateur existe
    new_user = db.query(User).filter(User.id == device_data.user_id).first()
    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mettre à jour les informations du device
    device.type = device_data.type
    device.software_version = device_data.software_version
    device.image = device_data.image
    device.initial_state = device_data.initial_state
    device.mac_address = device_data.mac_address
    device.operational_status = device_data.operational_status
    device.connection_status = device_data.connection_status
    device.battery_level = device_data.battery_level

    # Vérifier la dernière occupation du device
    last_occupation = (
        db.query(Occupation)
        .filter(Occupation.device_id == device_id)
        .order_by(Occupation.calendar_date.desc())
        .first()
    )
    
    # Si l'utilisateur a changé, ajouter une nouvelle occupation
    if not last_occupation or last_occupation.user_id != device_data.user_id:
        # Créer une nouvelle entrée dans le calendrier
        new_calendar_entry = Calendar(date=datetime.now())
        db.add(new_calendar_entry)
        db.commit()
        db.refresh(new_calendar_entry)

        # Ajouter une nouvelle occupation sans supprimer l'ancienne
        new_occupation = Occupation(
            user_id=device_data.user_id,
            device_id=device_id,
            calendar_date=new_calendar_entry.date
        )
        db.add(new_occupation)

    db.commit()
    db.refresh(device)

    return {
        "message": "Device updated successfully",
        "device": {
            "id": device.id,
            "type": device.type,
            "software_version": device.software_version,
            "initial_state": device.initial_state,
            "image": device.image,
            "mac_address": device.mac_address,
            "operational_status": device.operational_status,
            "connection_status": device.connection_status,
            "battery_level": device.battery_level,
            "user_id": device_data.user_id
        }
    }



# Créer un dispositif et l'affecter à un utilisateur (si spécifié)
@router.post("/devices/create")
def create_device(device_data: DeviceCreateBase, db: Session = Depends(get_db)):
    # Création du dispositif
    new_device = Device(
            type=DeviceTypeEnum(device_data.type),  
            software_version=device_data.software_version,
            initial_state=InitialStateEnum(device_data.initial_state), 
            image=device_data.image,
            mac_address=device_data.mac_address,
            operational_status=OperationalStatusEnum(device_data.operational_status), 
            connection_status=ConnectionStatusEnum(device_data.connection_status),
            battery_level=int(device_data.battery_level) 
        )
    
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    # Vérifier si un utilisateur est assigné
    if device_data.user_id is not None:
        calendar_entry = Calendar(date=datetime.now())
        db.add(calendar_entry)
        db.commit()
        db.refresh(calendar_entry)

        new_occupation = Occupation(
            user_id=device_data.user_id,
            device_id=new_device.id,
            calendar_date=calendar_entry.date
        )
        db.add(new_occupation)
        db.commit()

    return {
        "message": "Device created successfully",
        "device": {
            "id": new_device.id,
            "type": new_device.type,
            "software_version": new_device.software_version,
            "initial_state": new_device.initial_state,  
            "image": new_device.image,
            "mac_address": new_device.mac_address,
            "operational_status": new_device.operational_status,
            "connection_status": new_device.connection_status,
            "battery_level": new_device.battery_level,
            "user_id": device_data.user_id  
        }
    }
    
    


# Récupérer tous les utilisateurs
@router.get("/devices/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
