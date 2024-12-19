**MAD I Project Report – Sep 2024** 

- Name: Praul Kumar Ayar 
- Roll number: 21F1003816 
- Student email id:[ 21f1003816@ds.study.iitm.ac.in ](mailto:21f1003816@ds.study.iitm.ac.in)

**Problem Statement (Household Services Application)** 

It is a multi-user app (requires one admin and other service professionals/ customers) which acts as platform for providing comprehensive home servicing and solutions. 

**My Approach (HouseHelpNow.com)** 

**HouseHelpNow** which address the core problem which is to connect service provider and customers through a platform based on location, better pricing and availability. Service provider offering various services and customer can book service of their choice with no hassle.  

Each feature addressing specific need. Role based access, dashboard, analytics, payment integration. 

**Frameworks and libraries used**: 

- **Flask**: A lightweight, micro web framework for building web applications in Python. 
- **Flask** **Extensions**: 
- **Flask**-**SQLAlchemy**: Integrates SQLAlchemy ORM with Flask to simplify database operations. 
- **Flask**-**Migrate**: Handles SQLAlchemy database migrations via Alembic  
- **Flask**-**Login**: Manages user session management and authentication in Flask applications. 
- **Flask**-**WTF**: Provides simple integration of WTForms for form validation and CSRF protection 
- **Flask**-**RESTful**: Simplifies the creation of RESTful APIs by adding abstractions on top of Flask. 
- **Flask**-**Bcrypt**: Adds bcrypt hashing for securely storing and managing user passwords in Flask apps. 
- **Jinja2** templates for HTML generation  
- **Tailwind CSS**:  for styling and aesthetics 
- **Javascript** for interactivity in templates 
- **SQLite** for data storage 
- **Git** for version control 

**Database schema**: 

Our app has three roles catering specific stakeholder according to its requirement. For storing specific data about each entity and stockholders using Flask SQLAlchemy as ORM to write python class and storing in file- based database SQLite. 

- **Entities** (Tables) 
- **User**:  stores user information such as username, password, role (admin, provider, customer) 
- **Profile**: stores additional personal details about a user 
- **Admin**: for storing admin related data which superuser of platform 
- **Category**: it has all detail about category offered on platform and manage by only admin  
- **Provider**: for storing provider related info and category which they are part of 
- **Service**: it has all detail about specific service offered by provider under category 
- **Customer**: for storing customer related info  
- **Booking**: stores details about bookings made by customers such status and tracking 
- **CustomerPayment**: tracks payment details for bookings, including amounts, fees, and status. 
- **Review**: allows customers to leave ratings and feedback for services they have used 
- **Relationships**
- **User** has **one-to-one** relationship with **Profile**, **Admin**, **Provider**, **Customer** 
- **Admin** has **one-to-many** relationship with **Category** 
- **Provider** has **one-to-one** relationship with **Category**, **one-to-many** relationship with **Service** 
- **Customer** has **one-to-many** relationship with **Booking** 
- **Service** has **one-to-many** relationship with **Booking** 
- **Booking** has **one-to-one** relationship with **CustomerPayment** and **Rating** 

**ER Diagram** 

![](Aspose.Words.36f36e80-c1f2-4af9-83b8-55f982c50866.001.jpeg)

**Project organizations, Architecture and feature:** 

Using **flask** **blueprint** to structure whole application by grouping related functionality into different components. Creating small apps in comparison with main app which later merge into our main app. 

Each small app has main two files models.py and views.py which is based on MVT architecture. 

At root level in project code folder: 

- **main.py**: main py file which creates actual flask app instance from factory function and runs 
- **config.py**: config file for managing various config of our app 
- **templates** **folder**: all templates of our app which in turn organize various templates into subfolders 
- **static** **folder**: for static files such css and javascript  
- **instance** **folder**: contains SQLite database file 
- **migrations** **folder**: migrations scripts for database migrations 
- **application** **folder**: which contains all application code, business logic, models, controllers, rest apis  
- \_\_**init**\_\_.py:  creates flask app factory function which in itself connect various initialized extensions and registers blueprints, apis 
- **extensions**.**py**: initialize various flask extensions into single file 
- **seed**.**py**: generate initial data for app  
- **decorators**.**py**: decorator which provides backbone for role-based access for various functionality 
- **admin** **folder**: admin app for user management, category management, super user dashboard 
- **auth** **folder**: auth app for register various users, authentications, user session management 
- **apis folder:** for various api resources for admin and providers 
- **core folder:** core app for serving authenticated customer to access platform 
- **provider folder:** provider app for service management and booking handling, dashboard 
- **customer folder:** customer app for booking management, payment handling and rating, dashboard 

**API Resource endpoints:** 

- For **Admin**: 
- CategoryListAPI  
  - GET: Retrieve List of all category with its providers 
  - POST: Create new category 
- Category API 
- GET: Retrieve single category 
- For **Provider**: 
- ProviderServiceListAPI 
  - GET: Retrieve list of all services 
  - POST: Create new service 
- ProviderServiceAPI 
- GET: Retrieve single service  
- For **Customer:** 
- CustomerBookingListAPI 
  - GET: Retrieve list of all bookings  
  - POST: Create new booking 
- CustomerBookingAPI 
- GET: Retrieve single booking 

Github Repository:  [ Go to Repo ](https://github.com/myGreatLoveM/Household-services-app--MAD1--Project.git)Project Presentation Video:[ have a look ](https://drive.google.com/file/d/1ohtWOYqLLwT2GQKPHg4XjMUfkckIXPDc/view?usp=drive_link)ER diagram:[ click](https://drive.google.com/file/d/1A8enovF1btTmJS5riT7Lq9dh4rq6D0JR/view?usp=drive_link)
