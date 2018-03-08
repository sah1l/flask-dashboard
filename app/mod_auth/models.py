# from flask_login import UserMixin
# from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from werkzeug.security import generate_password_hash, check_password_hash
#
# from app import base, login, session_maker
# from app.models import users_orgs_association_table
#
#
# class User(UserMixin, base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True)
#     username = Column(String(64))
#     email = Column(String(120), index=True, unique=True)
#     password_hash = Column(String(128))
#     is_admin = Column(Boolean, default=False)
#     organizations = relationship("Organization",
#                                  secondary=users_orgs_association_table,
#                                  back_populates="users")
#
#     def __repr__(self):
#         return '<User {}>'.format(self.username)
#
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
#
#
# @login.user_loader
# def load_user(id):
#     session = session_maker()
#     user_id = session.query(User).get(int(id))
#     session.close()
#
#     return user_id
