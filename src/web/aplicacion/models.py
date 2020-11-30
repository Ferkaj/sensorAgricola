from sqlalchemy import Boolean, Column , ForeignKey
from sqlalchemy import DateTime, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from aplicacion.app import db
import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import random as rd

class User(db.Model, UserMixin):

    __tablename__ = 'farmer_user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, name, email,is_admin):
        self.name = name
        self.email = email
        self.is_admin = is_admin

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def get_by_id(id):
        return User.query.get(id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()


class Huerto(db.Model):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    #descripcion = Column(String(100), nullable=False)
    direccion = Column(String(100), nullable=False)
    codigoPostal = Column(String(100), nullable=False)
    localidad = Column(String(100), nullable=False)
    provincia = Column(String(100), nullable=False)

    #FK: farmer_user
    farmer_user_id = db.Column(db.Integer, db.ForeignKey('farmer_user.id'), nullable=True)

    
    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_user_id(user_id):
        return Huerto.query.filter_by(farmer_user_id=user_id).first()


class Zona(db.Model):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(100), nullable=False)

    # FK : huerto
    huerto_id = db.Column(db.Integer, db.ForeignKey('huerto.id'), nullable=True)

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Zona.query.get(id)

    @staticmethod
    def get_by_huerto_id(huerto):
        return Zona.query.filter_by(huerto_id=huerto).all()
    
    @staticmethod
    def get_by_user_id(user_id):
        huerto_id = Huerto.get_by_user_id(user_id).id
        return Zona.query.filter_by(huerto_id=huerto_id).all()

    
class Programa_riego(db.Model):
    id = Column(Integer, primary_key=True)
    fecha_inicio = Column(DateTime,default=datetime.datetime.utcnow)
    fecha_fin = Column(DateTime,default=datetime.datetime.utcnow)
    titulo = Column(String(100), nullable=True, default = "Programa de riego")
    
    ## FK : zona de riego
    zona_id = db.Column(db.Integer, db.ForeignKey('zona.id', ondelete="CASCADE"), nullable=False)
    
    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_zona_id(zona):
        return Programa_riego.query.filter_by(zona_id=zona).all()
	



class ElectroValvula(db.Model):
    id = Column(Integer, primary_key=True)
    mac = Column(String(100), nullable=False)
    estado = Column(Boolean, default = False)
    
    # FK : zona
    zona_id = db.Column(db.Integer, db.ForeignKey('zona.id', ondelete="CASCADE"), nullable=True)

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_mac(mac):
        return ElectroValvula.query.filter_by(mac=mac).first()

    @staticmethod
    def get_by_zona_id(zona):
        return ElectroValvula.query.filter_by(zona_id=zona).first()

class Sensor(db.Model):
    id = Column(Integer, primary_key=True)
    mac = Column(String(100), unique=True, nullable=False, )
    # FK : zona
    zona_id = db.Column(db.Integer, db.ForeignKey('zona.id', ondelete="CASCADE"), nullable=True)

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_mac(mac):
        return Sensor.query.filter_by(mac=mac).first()
    
    @staticmethod
    def get_by_zona_id(zona):
        return Sensor.query.filter_by(zona_id=zona).first()
    
class Registro(db.Model):
    id = Column(Integer, primary_key=True)
    created = Column(DateTime,default=datetime.datetime.utcnow)
    temp = Column(Float,nullable=False)
    hum = Column(Float,nullable=False)
    soil = Column(Float,nullable=False)
    
    ## FK : sensor_agricola
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id', ondelete="CASCADE"), nullable=False)
    

    def __init__(self,temperatura,humedad,humedadTerrestre,sensor_id):
        #self.created = datetime.datetime.utcnow
        self.temp = temperatura
        self.hum = humedad
        self.soil = humedadTerrestre
        self.sensor_id = sensor_id

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_sensor_id(sensor):
        return Registro.query.filter_by(sensor_id=sensor).all()
    
    @staticmethod
    def get_count_by_sensor_id(sensor,count):
        return Registro.query.filter_by(sensor_id=sensor).order_by(Registro.id.desc()).limit(count).all()
	
    @staticmethod
    def get_last_registro_by_sensor_id(sensor):
        return Registro.query.filter_by(sensor_id=sensor).order_by(Registro.id.desc()).first()