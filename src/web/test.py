#!flask/bin/python
import os
import unittest

from aplicacion.app import app, db, mqtt, handle_connect, handle_mqtt_message, validarDatos, validarYguardarRegistro
from aplicacion.models import *
from sqlalchemy.exc import IntegrityError
import json
PWD = os.path.abspath(os.curdir)	


class TestCase(unittest.TestCase):
    @staticmethod
    def create_user(name, email, password, is_admin):
        user = User(name=name,email= email, is_admin= is_admin)
        user.set_password(password)
        user.save()
        return user
    @staticmethod
    def create_huerto(nombre, direccion, codigoPostal, localidad, provincia, farmer_id):
        huerto = Huerto(nombre = nombre, direccion = direccion, codigoPostal = codigoPostal, localidad= localidad, provincia=provincia)
        huerto.farmer_user_id = farmer_id
        huerto.save()
        return huerto

    @staticmethod
    def create_zona(nombre, descripcion, huerto_id):
        zona = Zona(nombre=nombre, descripcion = descripcion)
        zona.huerto_id = huerto_id
        zona.save()
        return zona
    
    

    @staticmethod
    def create_sensor(mac, zona_id):
        sensor = Sensor(mac = mac)
        sensor.zona_id = zona_id
        sensor.save()
        return sensor
    
    @staticmethod
    def create_registro(temperatura,humedad,humedadTerrestre,sensor_id):
        registro = Registro(temperatura=temperatura,humedad=humedad,humedadTerrestre=humedadTerrestre,sensor_id=sensor_id)
        registro.save()
        return registro



    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/test.db'.format(PWD)
        app.config['DEBUG'] = True # Ensure debugger will load.
        app.config['MQTT_BROKER_URL'] = '192.168.1.210'  # use the free broker from HIVEMQ
        app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
        app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
        app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
        app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
        app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes

        self.app = app.test_client()
        db.create_all()
        
        handle_connect
        handle_mqtt_message
        user_id = TestCase.create_user('alice', 'alice@xyz.com','1234',False).id
        
        huerto_id = TestCase.create_huerto("huerto de prueba","Av. Andalucia 21","41400", "Los algarves","Sevilla", user_id).id
        zona_id = TestCase.create_zona("zona 0","zona 0 ", huerto_id).id
        try:
            TestCase.create_sensor("84:0D:FF:FF:3A:FE",zona_id).id

        except IntegrityError:
            pass
        
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_make_unique_email(self):
        user1 = User(name='john',email= 'john@example.com', is_admin= False)
        user1.set_password("password")
        db.session.add(user1)
        db.session.commit()

        user2 = User(name='alice',email= 'john@example.com', is_admin= False)
        user2.set_password("1234")
        db.session.add(user2)
        self.assertRaises(IntegrityError, db.session.commit)
         
    def test_anonimous_access(self):
        res = self.app.get('/huerto/')
        self.assertEqual(302, res.status_code)
        res = self.app.get('/zonas/')
        self.assertEqual(302, res.status_code)
        res = self.app.get('/addZona/')
        self.assertEqual(302, res.status_code)
        
    def test_unauthorized_access(self):
        res = self.app.get('/deleteZona/')
        self.assertEqual(404, res.status_code)

    def test_show_zone_not_exits(self):
        self.login('alice@xyz.com', '1234')
        res = self.app.get('/zona/1')
        self.assertEqual(308, res.status_code)

    def test_unauthorized_access_to_admin(self):
        self.login('alice@xyz.com', '1234')

        res = self.app.get('/registerFarmer/')
        self.assertEqual(302, res.status_code)
    
    def test_mqtt_received(self):
        
        user_id = User.get_by_email('alice@xyz.com').id
        
        zona_id = Zona.get_by_user_id(user_id)[0].id
        
        sensor = Sensor.get_by_zona_id(zona_id)
        print(sensor)
        
        datosDic = {
            'id': f'{sensor.mac}', 
            'temp': 10.0,
            'hum': 10.0,
            'soil': 19.0
            }

        payload = json.dumps(datosDic)
        mqtt.subscribe('leaf/server/records')

        handle_connect
        handle_mqtt_message
        mqtt.publish("leaf/server/records",payload)
        mqtt.publish("leaf/server/records",payload)
        mqtt.publish("leaf/server/records",payload)

        registro = Registro.get_last_registro_by_sensor_id(sensor.id)

        self.assertEqual(10.0, registro.temp)

    def login(self, email, password):
        return self.app.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    

if __name__ == '__main__':
    unittest.main()