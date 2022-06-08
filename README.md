## MediBuddy – wearable system for healt monitoring
-------------------------------------------------------------

The python django-restframework app represents the backend of the MediBuddy App as the web server accepting HTTP requests from the client. 
The MediBuddy project is a fictive application for learning purpuses. This consists of a wearable device for alderly patientients to monitor their fiziological parameters (EKG, humidity, temperature, puls). If this parameters are not within the normal ranges, the patient/user will receive a notification via Smartphone. This application also includes a web interface, where doctors can create an account, register patients, edit and monitor patients files. 

## Project URL:
    api documentation:
    [MediBuddy_API](http://ec2-34-234-75-154.compute-1.amazonaws.com/api/docs/)
    
    http://ec2-34-234-75-154.compute-1.amazonaws.com/api/docs/

## API Endpoints

-> Api documentation:

    GET : http://127.0.0.1:8000/api/docs/
    

-> Register new doctor-user:

    POST : http://127.0.0.1:8000/api/signup/doctor/ 

    Input:
        {
            "user": {
                "username":"doctor1",
                "email":"doc1@doctor.com",
                "password":"password123",
                "first_name":"Cristian",
                "last_name":"Doc"
            },
            "speciality":"cardio"
        }

    Output: 

        If successful, will return an object with the following properties:
        user_id, username, is_doctor:true, token, message: "account created successully".

        Will return an array of reasons why registration failed (e.g. username is already taken, invalid email address, required fields: username, email, password, first_name, last_name). 
        

    
-> Register new pacient-user:
    A new patient can be added only by an existing and authenticated doctor using the web interface.
    The patient will automaticaly be assingned to the authenticated doctor.

    POST : http://127.0.0.1:8000/api/signup/patient/

    Input: (doctor token required, only doctor-user can register a patient)
        {
            "user": {
                "username":"pacient3",
                "email":"test3@pacient.com",
                "password":"password123",
                "first_name":"Dan",
                "last_name":"Popescu"
            },
            "cnp":"128756789",
            "birthday":"1997-06-23",
            "street":"blastr",
            "city":"tm",
            "state":"romania",
            "phone":"+40712800429",
            "profession":"professor",
            "workplace":"tircomp",
            "records":"...",
            "alergies":"nuts",
            "cardio_check":"..."
        }

    Output: 

        If successful, will return an object with the following properties:
        user_id, username, is_doctor:false, token, message: "account created successully".

        Will return an array of reasons why registration failed ( username, cnp or phone is already taken, invalid email address, required fields: username, email, password, first_name, last_name, cnp, birthday, phone). 
        


-> Login user (doctor and patient can use this endpoint):

    POST : http://127.0.0.1:8000/api/login/

    Input: 
        {
            "username":"doctor1",
            "password":"password123"
        }

    Output:

        If successful, will return an object with the following properties:
        token, user_id, username, is_doctor:true

        Will return an array of reasons why registration failed (ex. username or password incorect).


-> Logout user(doctor and patient can use this endpoint):

    POST : http://127.0.0.1:8000/api/logout/

    Input : (token required, registered user)
        None
    Output:
        If successful: Response HTTP_204_NO_CONTENT
        Will return an array of reasons why registration failed (ex. no token provided)

-> Change password user (doctor and patient can use this endpoint):
    All registered users(doctor or patient), can change their password. 
    For the first time, when a patient is registered, he receives the username and password
    from his doctor, and he can change his password.

    PUT : http://127.0.0.1:8000/api/change-password/

    Input: (token required, registered user)
        {
            "old_password":"password12",
            "new_password":"newpass456"
        }
    Output:
        If successful: Response HTTP_204_NO_CONTENT
        Will return an array of reasons why the change failed (ex. old_password is incorect).

-> DOCTOR PROFILE:
    Endpoints representing a doctor profiles and the actions that can be done to the profile: 
    show(GET) profile, update(PATCH) profile, delete(DELETE) profile

    - show profile:
        GET: http://127.0.0.1:8000/api/doctor/profile/

        Input: (token required, registered doctor)
            None
        Output:
        If successful:
            {
                "user": {
                    "id": <user.id>,
                    "username": "<username>",
                    "email": "<email>",
                    "first_name": "<first_name>",
                    "last_name": "<last_name>",
                    "is_doctor": true
                },
                "speciality": "<speciality>",
                "patients": [<id list of registered patients>]
            }
        Will return an array of reasons why the change failed (ex. no (valid) token provided).

    - update profile
        PATCH : http://127.0.0.1:8000/api/doctor/profile/

        Input: (token required, registered doctor)
            (all fields are optional)
            {
                "user": {
                    "email": "<new_email>",
                    "first_name": "<new_first_name>",
                    "last_name": "<new_last_name>"
                },
                "speciality": "<new_speciality>"
            }
        Output:
        If successful:
            {
                "user": {
                    "id": <user.id>,
                    "username": "<username>",
                    "email": "<email>",
                    "first_name": "<first_name>",
                    "last_name": "<last_name>",
                    "is_doctor": true
                },
                "speciality": "<speciality>",
                "patients": [<id list of registered patients>]
            }
        Will return an array of reasons why the change failed (ex. no (valid) token provided).

    - delete profile
        DELETE : http://127.0.0.1:8000/api/doctor/profile/

        Input: (token required, registered doctor)
            None
        Output:
            If successful: Response HTTP_204_NO_CONTENT
            Will return an array of reasons why the change failed (ex. no (valid) token provided).

-> Doctor's patients list
    Show a list of all the patients belonging to the registered doctor, and the actions that can be done each profile. Doctor has all rights to edit/delete a patients profile. 
    
    - show all patints profiles:
        GET: http://127.0.0.1:8000/api/doctor/patients/

            Input: (token required, registered doctor)
                None
            Output:
                If successful: List with all the patients of the registered doctor

    - show patient's with id (patient_id) profile
        GET: http://127.0.0.1:8000/api/doctor/patients/<int:patient_id>/

            Input: (token required, registered doctor)
                None
            Output:
                If successful: List the patient profil: 
                user :{id, username, email, first_name, last_name, is_doctor},
                limits :{patient, ecg_low, ecg_high, humidity_low, humidity_high}
                doctor, cnp, birthday, street, city, state, phone, profession, workplace,
                records, alergies, cardio_check


    - update patient's with id (patient_id) profile 
        - PATCH: http://127.0.0.1:8000/api/doctor/patients/<int:patient_id>/

            Input: (token required, registered doctor)
                    (all fields are optional)
                {
                    "user": {
                        "email": "<new_email>",
                        "first_name": "<new_first_name>",
                        "last_name": "<new_last_name>"
                    },
                    "limits": {
                        "ecg_low": <new_limit>,
                        "ecg_high": <new_limit>,
                        "humidity_low": <new_limit>,
                        "humidity_high": <new_limit>,
                        "temperature_low": <new_limit>,
                        "temperature_high": <new_limit>,
                        "pulse_low": <new_limit>,
                        "pulse_high": <new_limit>
                    },
                    "cnp": "<new_cnp>",
                    "birthday": "<new_birthday: YYYY-MM-DD>",
                    "street": "<new_street>",
                    "city": "<new_city>",
                    "state": "<new_state>",
                    "phone": "<new_phone_nr>",
                    "profession": "<new_profession>",
                    "workplace": "<new_workplace>",
                    "records": "<new_record>",
                    "alergies": "<new_alergie>",
                    "cardio_check": "<new_cardio_check_data>"
                }

            Output: If successful:
                {
                    "user": {
                        "id": <user_id?,
                        "username": "<username>",
                        "email": "<email>",
                        "first_name": "<first_name>",
                        "last_name": "<last_name>",
                        "is_doctor": false
                    },
                    "limits": {
                        "ecg_low": <limit>,
                        "ecg_high": <limit>,
                        "humidity_low": <limit>,
                        "humidity_high": <limit>,
                        "temperature_low": <limit>,
                        "temperature_high": <limit>,
                        "pulse_low": <limit>,
                        "pulse_high": <limit>
                    },
                    "doctor": <doctor_id>,
                    "cnp": "<cnp>",
                    "birthday": "<birthday>",
                    "street": "<street>",
                    "city": "<city>",
                    "state": "<state>",
                    "phone": "<phone_nr>",
                    "profession": "<profession>",
                    "workplace": "<workplace>",
                    "records": "<records>",
                    "alergies": "<alergies>",
                    "cardio_check": "<cardio_ckeck>"
                }

    - delete patient's with id (patient_id) profile          
        - DELETE: http://127.0.0.1:8000/api/doctor/patients/<int:patient_id>/

            Input: (token required, registered doctor)
                None
            Output:
                If successful: Response HTTP_204_NO_CONTENT 
    
- PATIENT PROFILE:
    Endpoints representing a patient profile. A patinent can only see his informations:

    - show patient profile
        GET: http://127.0.0.1:8000/api/patient/profile/
        
            Input: (token required, registered patient)
                    None
            Output:
                If successful: List the patient profil: 
                user :{id, username, email, first_name, last_name, is_doctor},
                limits :{patient, ecg_low, ecg_high, humidity_low, humidity_high}
                doctor, cnp, birthday, street, city, state, phone, profession, workplace,
                records, alergies, cardio_check

- MEASUREMENTS:
    Endpoints representing the patients measurements.

    - add new measurement:
        POST: http://127.0.0.1:8000/api/patient/measurements/
        
        Input: (token required, registered patient
                all fields are optional)
            {
                "ecg":65,
                "humidity":50,
                "temperature":36.7,
                "pulse":65
            }
        Output:
            {
                "created_on": "2022-05-13T17:33:47.768185Z",
                "patient": 6,
                "ecg": 65,
                "humidity": 50,
                "temperature": 36.7,
                "pulse": 65
            }

    - get measurement as a patient: 
        GET: http://127.0.0.1:8000/api/patient/measurements/?date=2022-05-13

        Input: (token required, registered patient
                date parameter required)
        Output:
            If successful: a list with all measurements {created_on, ecg, humidity, temperature, pulse} object from that date
            Will return an array of reasons why request failed (ex. no (valid) token provided).
            will return an empty list if no date is provided

    -get measurement as a doctor:
        GET: http://127.0.0.1:8000/api/doctor/<int:patient_id>/measurements/?date=2022-05-13

        Input: (token required, registered doctor
                date parameter required)
        Output:
            If successful: a list with all measurements {created_on, ecg, humidity, temperature, pulse} object from that date
            Will return an array of reasons why request failed (ex. no (valid) token provided).
            will return an empty list if no date is provided or if the patient_id does not belong to a patient of the registered doctor

- NOTIFICATIONS:
    Endpoints representing the notifications send from doctor to his patients.

    - add a new notification (for doctor)
        POST: http://127.0.0.1:8000/api/doctor/notifications/

        Input: (token required, registered doctor)
            {
                "patient_id":6,
                "message":"eat no more sugar",
                "start_date":"2022-05-15",
                "end_date":"2022-10-01"
            }
        Output:
            {
                "id": 15,
                "patient": 6,
                "message": "eat no more sugar",
                "created_on": "2022-05-13T17:57:53.168140Z",
                "active": false,
                "start_date": "2022-05-15",
                "end_date": "2022-10-01",
                "doctor": 2
            }
            Will return an array of reasons why request failed (ex. no (valid) token provided, 
            no "patient_id" provided, the patient id does not corespond to a patient of the registered user).

    - update notification (for doctor)
        POST: http://127.0.0.1:8000/api/doctor/notifications/<int:notification_id>/

        Input: (token required, registered doctor, 
                all fields are optional)
            {
                "message":"walk daily",
                "start_date":"2022-05-15",
                "end_date":"2022-10-01"
            }
        Output:
            {
                "id": 15,
                "patient": 6,
                "message": "walk daily",
                "created_on": "2022-05-13T17:57:53.168140Z",
                "active": false,
                "start_date": "2022-05-15",
                "end_date": "2022-10-01",
                "doctor": 2
            }
            Will return an array of reasons why request failed (ex. no (valid) token provided, 
            no "patient_id" provided, the patient id does not corespond to a patient of the registered user).

    - show notifications (for doctor)
        GET: http://127.0.0.1:8000/api/doctor/notifications/

        Input: (token required, registered doctor)
            None
        Output:
            List will al the notifications created by the registered doctor
             Will return an array of reasons why request failed (ex. no (valid) token provided)

    - show notifications (for patient)
        GET: http://127.0.0.1:8000/api/patient/notifications/

        Input: (token required, registered patient)
            None
        Output:
            List will al the notifications of the authenticated patient
            Will return an array of reasons why request failed (ex. no (valid) token provided)

    - activate notification (for patient)
        PATCH: http://127.0.0.1:8000/api/patient/notifications/<int:notification_id>/

        Input: (token required, registered patient)
            {
                "active":true
            }
        Output:
            {
                "id": <notification_id>,
                "patient": <patient_id>,
                "message": "<message>",
                "created_on": "<created time>",
                "active": true,
                "start_date": "<start_date>",
                "end_date": "<end_date>",
                "doctor": <doctor_id>
            }
            Will return an array of reasons why request failed (ex. no (valid) token provided)
    
        
