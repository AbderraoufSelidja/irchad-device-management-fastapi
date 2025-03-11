# IRCHAD Project - Device Management Module  

## Overview  
IRCHAD is an indoor navigation and assistance system designed to help visually impaired individuals navigate indoor environments efficiently. This project was developed as part of a fourth-year computer science project at our school(ESI Algiers). I am one of the team members contributing to the system's development. IRCHAD includes multiple components, such as mapping management, real-time user localization, and interactive guidance, ensuring an accessible and user-friendly experience.  

## Device Management Module  
As part of this project, this module is responsible for managing the assignment of devices to users. Administrators can allocate, track, and update devices linked to each user, ensuring seamless integration with the overall navigation system. This module is built with a FastAPI backend and a web-based frontend, facilitating efficient device administration.  

## Features  
- **User-Device Assignment**: Administrators can assign specific devices to registered users.  
- **Device Tracking**: The system maintains a record of all assigned devices.  
- **Device Management**: Administrators can update, reassign, or remove device assignments.  
- **API Integration**: The backend provides RESTful APIs for easy communication with other components of the system.  
- **Device History Tracking**: Keep a history of past device assignments and usage logs for analysis.

## Technologies Used  
- **Backend**: FastAPI (Python)  
- **Database**: PostgreSQL  

## Installation  

### Prerequisites  
- Python 3.8+  
- PostgreSQL  
### Backend Setup  
## 1. Clone the repository:  
   - git clone git@github.com:AbderraoufSelidja/irchad-device-management-fastapi.git
   - cd irchad-device-management
# 2. Create a virtual environment and install dependencies:
   - python -m venv venv.␣␣
   - pip install -r requirements.txt
# 3. Configure the database by updating the DATABASE_URL in db/db_setup.py:
  - Go to db/db_setup.py
  # Modify the following variables with your database credentials:
    - DATABASE_URL=postgresql://user:password@localhost/irchad_db
   - SECRET_KEY=your_secret_key.␣␣
   - alembic upgrade head.␣␣
# 4. Run the backend server
  - python -m uvicorn main:app --reload
# 5. Test the API
  - Open your browser and go to: http://127.0.0.1:8000/docs
