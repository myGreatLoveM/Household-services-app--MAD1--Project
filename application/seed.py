import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from application.admin.models import Admin, Category
from application.core.models import User
from application.extensions import db
from application.core.enums import UserRoleEnum
from application.admin.constants import categories as categories_raw_data


def create_initial_data():
    inspector = sa.inspect(db.engine)

    user_table_created = inspector.has_table("users")
    admin_table_created = inspector.has_table("admin")
    categories_table_created = inspector.has_table("categories")
    database_created = user_table_created and admin_table_created and categories_table_created
    
    if database_created:
        user_admin = db.session.query(User, Admin).join(Admin, User.admin).filter(User.role.is_(UserRoleEnum.ADMIN.value)).first()

        if user_admin is None:
            super_user = User(username='admin', role=UserRoleEnum.ADMIN.value)
            super_user.password = '123456'
            admin = Admin()
            super_user.admin = admin
            super_user.save_to_db()


        if user_admin and user_admin[1].categories.count() <= len(categories_raw_data):
            try:
                for category in categories_raw_data:
                    category_exist = Category.query.filter(Category.name == category.get('name')).first()

                    if category_exist:
                        continue

                    new_cat = Category(
                        name=category.get('name'), 
                        admin_id=user_admin[1].id,
                        base_price=int(category.get('base_price')),
                        service_rate=int(category.get('service_rate')),
                        booking_rate=int(category.get('booking_rate')),
                        transaction_rate=int(category.get('transaction_rate')),
                        short_description=category.get('short_description'),
                        long_description=category.get('long_description'),
                    )
                    db.session.add(new_cat)
                db.session.commit()
                print('Everything created successfully')
            except:
                db.session.rollback()
                raise SQLAlchemyError('Something went wrong')
    else:
        db.create_all()

