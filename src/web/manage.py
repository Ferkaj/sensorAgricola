from flask_script import Manager
from aplicacion.app import app,db
from aplicacion.models import *
from werkzeug.security import generate_password_hash, check_password_hash

manager = Manager(app)
app.config['DEBUG'] = False # Ensure debugger will load.
app.config['ENV'] = "production"


@manager.command
def create_tables():
    "Create relational database tables."
    db.create_all()	

@manager.command
def drop_tables():
    "Drop all project relational database tables. THIS DELETES DATA."
    db.drop_all()

@manager.command
def add_data_tables():
    db.drop_all()
    db.create_all()

    registros = [
        {
			"temp": 20, "hum": 12, "soil":0
		},
		{
			"temp": 21, "hum": 22, "soil":2
		},
		{
			"temp": 22, "hum": 32, "soil":4
		}, ]

    administradores = [
        {
            "name": "admin", "email": "admin@XYX.com", "password": "1234","is_admin": True
        },
    ]
    usuarios = [
        {
            "name": "alice", "email": "alice@XYX.com", "password": "1234","is_admin": False
        },
        {
            "name": "bart", "email": "bart@XYX.com", "password": "1234","is_admin": False
        },
        {
            "name": "charlie", "email": "charlie@XYX.com", "password": "1234","is_admin": False
        },
    ]

    huertos = [
        {
            "nombre": "Villa conejos", 
            "direccion": "Av. El quinto pino, 22",
            "codigoPostal": "41013",
            "localidad": "Bermejales",
            "provincia": "Sevilla",
            "farmer_user_id": 0
        },
    ]

    zonas = [
        {
            "nombre": "Aromáticas",
            "descripcion": "Plantas aromáticas: (menta, romero, caléndula,...)",
            "huerto_id": 0
        },
        {
            "nombre": "Frutales",
            "descripcion": "Arboles frutales: (naranjos, limoneros, pomelo,...)",
            "huerto_id": 0
        },
    ]

    sensores = [
        {
            "mac": "84:0D:8E:A5:3A:FE",
            "zona_id": 0
        },
        {
            "mac": "84:0D:FF:FF:3A:FE",
            "zona_id": 1
        },
    ]

    electrovalvulas = [
        {
            "mac": "84:0D:8E:A5:38:88",
            "zona_id": 0
        },
        {
            "mac": "84:FF:FF:A5:38:88",
            "zona_id": 1
        },
    ]

    registros = [
        {
            "temp": 9,
            "hum": 30,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 19,
            "hum": 10,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 29,
            "hum": 20,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 39,
            "hum": 30,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 49,
            "hum": 90,
            "soil": 8,
            "sensor_id":0
        },
        {
            "temp": 9,
            "hum": 30,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 19,
            "hum": 10,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 29,
            "hum": 20,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 39,
            "hum": 30,
            "soil": 80,
            "sensor_id":0
        },
        {
            "temp": 49,
            "hum": 90,
            "soil": 8,
            "sensor_id":0
        },
    ]

    for user in administradores:
        newUser = User(user["name"],user["email"],user["is_admin"])
        newUser.set_password(user["password"])
        db.session.add(newUser)
        db.session.commit()

    for user in usuarios:
        newUser = User(user["name"],user["email"],user["is_admin"])
        newUser.set_password(user["password"])
        db.session.add(newUser)
        db.session.commit()

    for huerto in huertos:
        newHuerto = Huerto(**huerto)

        newHuerto.farmer_user_id = User.get_by_email(usuarios[huerto["farmer_user_id"]]["email"]).id
        db.session.add(newHuerto)
        db.session.commit()


    for zona in zonas:
        newZona = Zona(**zona)

        user_id = User.get_by_email(usuarios[huertos[zona["huerto_id"]]["farmer_user_id"]]["email"]).id
        huerto_id = Huerto.get_by_user_id(user_id).id
        newZona.huerto_id =huerto_id
        db.session.add(newZona)
        db.session.commit()
    
    for electro in electrovalvulas:
        idZona = electro["zona_id"]
        idHuerto = zonas[idZona]["huerto_id"]
        idUser = huertos[idHuerto]["farmer_user_id"]
        
        user_id = User.get_by_email(usuarios[idUser]["email"]).id
        huerto_id = Huerto.get_by_user_id(user_id).id
        zona_id = Zona.get_by_huerto_id(huerto_id)[idZona].id

        newElectroValvula = ElectroValvula(mac=electro["mac"],zona_id = zona_id)
        db.session.add(newElectroValvula)
        db.session.commit()

    for sensor in sensores:
        idZona = sensor["zona_id"]
        idHuerto = zonas[idZona]["huerto_id"]
        idUser = huertos[idHuerto]["farmer_user_id"]
        
        user_id = User.get_by_email(usuarios[idUser]["email"]).id
        huerto_id = Huerto.get_by_user_id(user_id).id
        zona_id = Zona.get_by_huerto_id(huerto_id)[idZona].id

        newSensor = Sensor(mac=sensor["mac"],zona_id = zona_id)
        db.session.add(newSensor)
        db.session.commit()

    for reg in registros:
        idSensor = reg["sensor_id"]
        idZona = sensores[idSensor]["zona_id"]
        idHuerto = zonas[idZona]["huerto_id"]
        idUser = huertos[idHuerto]["farmer_user_id"]
        
        user_id = User.get_by_email(usuarios[idUser]["email"]).id
        huerto_id = Huerto.get_by_user_id(user_id).id
        zona_id = Zona.get_by_huerto_id(huerto_id)[idZona].id
        sensor_id = Sensor.get_by_zona_id(zona_id).id

        newRegistro = Registro(reg["temp"],reg["hum"],reg["soil"],sensor_id)
        db.session.add(newRegistro)
        db.session.commit()




if __name__ == '__main__':
	manager.run()