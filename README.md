# Scheduling System API

This project is a scheduling system built with Flask, designed to manage doctors, specialties, availability, and patient information, including previous consultations and appointments.

## Project Structure

```
scheduling_system
├── app
│   ├── __init__.py
│   ├── api_doctors
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   ├── api_patients
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   └── extensions.py
├── requirements.txt
├── config.py
└── README.md
```

## Features

- **Doctors API**: Manage doctors, specialties, and their availability.
  - List doctors
  - Add new doctors
  - Update doctor availability

- **Patients API**: Manage patient information and appointments.
  - Add new patients
  - Retrieve patient records
  - Schedule appointments

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd scheduling_system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `config.py`.

4. Run the application:
   ```
   flask run
   ```