Project Management System (Tkinter + PostgreSQL)
-------------------------------------------------
This is a Project Management System using a PostgreSQL database for storage.

How to Run:
1. Quick Setup (Recommended):
   - Run setup.bat to install dependencies and set up the database
   - Run start.bat to start the application

2. Manual Setup:
   - Install required packages:
     pip install -r requirments.txt
   - Setup PostgreSQL:
     a. Make sure PostgreSQL server is running
     b. Create a database named 'project_management'
     c. Run init-db.sql script to create necessary tables
   - Update your PostgreSQL credentials in the script if needed

Docker Setup:
- This project includes Docker configuration for the database
- Run setup.bat and select option 1 to set up the database using Docker
- PostgreSQL will be available at localhost:5432
- Database: project_management
- Username: postgres
- Password: Baseball1023

Features:
- Project management with detailed project information
- Team member tracking
- Requirements management
- Effort tracking
- Risk management
- Data export (CSV/PDF)
- User authentication system

Authors: Group 1
https://docs.google.com/document/d/1eB-rOR43J3jxL-RsJ3McKKb02yQAsRsL/edit?usp=sharing&ouid=110038738534494505738&rtpof=true&sd=true
