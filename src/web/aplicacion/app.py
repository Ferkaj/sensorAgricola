from flask import Flask, render_template, abort, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mqtt import Mqtt
from aplicacion import config
import json
from json.decoder import JSONDecodeError
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from aplicacion.forms import *
import re
import datetime

app = Flask(__name__)
app.config.from_object(config)

app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
login_manager = LoginManager(app)

Bootstrap(app)	
db = SQLAlchemy(app)
from aplicacion.models import *


app.config['DEBUG'] = True # Ensure debugger will load.
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes

""" 
app.config['DEBUG'] = True # Ensure debugger will load.
app.config['MQTT_BROKER_URL'] = '192.168.1.210'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
"""

mqtt = Mqtt(app)
 



@app.route('/')
def index():
	return render_template("index.html")

@login_required
@app.route('/huerto/')
def show_huerto():
    
    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))

    huerto = Huerto.get_by_user_id(current_user.id)

    if huerto is None:
        return redirect(url_for('add_huerto'))


    return render_template('show_huerto.html', huerto=huerto)

@login_required
@app.route('/addHuerto/', methods=['GET', 'POST'])
def add_huerto():
    
    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))
    if Huerto.get_by_user_id(current_user.id) is not None:
        return redirect(url_for('show_huerto'))

    form = HuertoForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        direccion = form.direccion.data
        codigoPostal = form.codigoPostal.data
        localidad = form.localidad.data
        provincia = form.provincia.data

        huerto = Huerto(farmer_user_id=current_user.id,nombre=nombre, direccion=direccion,codigoPostal=codigoPostal,localidad=localidad, provincia=provincia)
        huerto.save()
        return redirect(url_for('show_huerto'))

    return render_template("huerto_form.html", form=form, titulo = "Create your farm")

@login_required
@app.route('/zonas/')
def list_zona():
    usuario = current_user

    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))
    
    huerto = Huerto.get_by_user_id(current_user.id)
    zonas = []
    if huerto is None:
        return redirect(url_for('index')) # TODO: cambiar por crear huerto
    else:
        zonas = Zona.get_by_huerto_id(huerto.id)

    return render_template("list_zona.html",usuario=usuario,zonas=zonas)	


@login_required
@app.route('/zona/<int:zona_id>/')
def show_zona(zona_id):
    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))

    #seleccionar zona mediante id
    zona = Zona.get_by_id(zona_id)
    if zona is None:
        abort(404)

    if Zona.get_by_user_id(current_user.id).count(zona) < 1:
        abort(401)
        
    sensor = Sensor.get_by_zona_id(zona.id)
    registros = []
    labels = []
    temperatures = []
    humidities = []
    soilHumidities = []
    legend = None
    legend2 = None
    legend3 = None

    electrovalvula = ElectroValvula.get_by_zona_id(zona.id)
    estadoRiego = None
    if electrovalvula is not None:
        estadoRiego = electrovalvula.estado

    registro = None
    if sensor is not None:
        registros = Registro.get_count_by_sensor_id(sensor.id,10)
        registros = registros[::-1]
        registro = Registro.get_last_registro_by_sensor_id(Sensor.get_by_zona_id(zona.id).id)
       
        
        legend = 'Temperature records'
        legend2 = 'humidity records'
        legend3 = 'Soil Humidity records'
        
        for reg in registros:
            labels.append(reg.created)
            temperatures.append(reg.temp)
            humidities.append(reg.hum)
            soilHumidities.append(reg.soil)

    
    return render_template("show_zona.html",zona=zona.nombre, zona_id= zona.id,registros= registros, registro = registro,labels = labels, temperatures = temperatures, humidities = humidities, soilHumidities=soilHumidities, legend = legend, legend2 = legend2, legend3 = legend3, estado = estadoRiego)	



@login_required
@app.route('/addZona/', methods=['GET', 'POST'])
def add_zona():
    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))
    
    # seleccionar huerto del farmer user, sino tiene se redirige para crear un huerto
    huerto = Huerto.get_by_user_id(current_user.id)
    if huerto is None:
        return redirect(url_for('add_huerto'))
    
    form = ZonaForm()
    error = None
    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        macSensor = form.macSensor.data
        macElectroValvula = form.macElectroValvula.data

        #comprobar que las macs no se estan usando
        error = []
        sensor = Sensor.get_by_mac(macSensor)
        electrovalvula = ElectroValvula.get_by_mac(macElectroValvula)
        if sensor is not None:
            error = f'The mac address of agriculture sensor {macSensor} is already being used.'
        elif electrovalvula is not None:
            error = f'The mac address of solenoid valve {macSensor} is already being used.'
        else:
            zona = Zona(nombre=nombre,descripcion=descripcion, huerto_id = huerto.id)
            
            zona.save()

            sensor = Sensor(mac=macSensor,zona_id=zona.id)
            sensor.save()

            electrovalvula = ElectroValvula(mac=macElectroValvula,zona_id=zona.id)
            electrovalvula.save()
            #crear sensor

            #crear electrovalvula

            
            return redirect(url_for('list_zona'))
    return render_template("zona_form.html", form=form, titulo = "Create a irrigation zone",error = error)

""" 
@login_required
@app.route('/editZona/<int:zona_id>/', methods=['GET', 'POST'])
def edit_zona(zona_id):
    if current_user.is_admin:
        return redirect(url_for('index'))

    #seleccionar zona mediante id
    zona = Zona.get_by_id(zona_id)
    if zona is None:
        abort(404)

    if Zona.get_by_user_id(current_user.id).count(zona) < 1:
        abort(401)
    
    # seleccionar huerto del farmer user, sino tiene se redirige para crear un huerto
    huerto = Huerto.get_by_user_id(current_user.id)
    if huerto is None:
        return redirect(url_for('add_huerto'))
    
    form = ZonaForm()
    error = None
    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        macSensor = form.macSensor.data
        macElectroValvula = form.macElectroValvula.data

        #comprobar que las macs no se estan usando
        error = []
        sensor = Sensor.get_by_mac(macSensor)
        electrovalvula = ElectroValvula.get_by_mac(macElectroValvula)

        if sensor is not None:
            if sensor.zona_id != zona.id:
                error = f'The mac address of agriculture sensor {macSensor} is already being used.'
        elif electrovalvula is not None:
            if electrovalvula.zona_id != zona.id:
                error = f'The mac address of solenoid valve {macSensor} is already being used.'
        else:
            zona.nombre = nombre
            zona.descripcion = descripcion
            zona.save()

            sensor = Sensor.get_by_zona_id(zona.id)
            electrovalvula = ElectroValvula.get_by_zona_id(zona.id)

            if sensor is None:
                sensor = Sensor(mac=macSensor,zona_id=zona.id)
                sensor.save()
            else:
                sensor.mac = macSensor
                sensor.save()

            if electrovalvula is None:
                electrovalvula = ElectroValvula(mac=macElectroValvula,zona_id=zona.id)
                electrovalvula.save()
            else:
                electrovalvula.mac = macElectroValvula
                electrovalvula.save()

            
            return redirect(url_for('list_zona'))
    return render_template("zona_form.html", form=form, titulo = "Edit a irrigation zone",error = error)

 """

@login_required
@app.route('/deleteZona/<int:zona_id>/')
def delete_zona(zona_id):
    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))

    #seleccionar zona mediante id
    zona = Zona.get_by_id(zona_id)
    if zona is None:
        abort(404)

    if Zona.get_by_user_id(current_user.id).count(zona) < 1:
        abort(401)
    
    sensor = Sensor.get_by_zona_id(zona.id)
    electrovalvula = ElectroValvula.get_by_zona_id(zona.id)

    sensor.delete()
    electrovalvula.delete()

    zona.delete()

    return redirect(url_for('list_zona'))



@login_required
@app.route('/activarRiego/<int:zona_id>/')
def activar_riego(zona_id):
    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))

    #seleccionar zona mediante id
    zona = Zona.get_by_id(zona_id)
    if zona is None:
        abort(404)

    if Zona.get_by_user_id(current_user.id).count(zona) < 1:
        abort(401)
    
    electrovalvula = ElectroValvula.get_by_zona_id(zona.id)
    if electrovalvula is not None:
        datosDic = {
            'id': f'{electrovalvula.mac}', 
            'estado':True
            }
        data = json.dumps(datosDic)
        mqtt.publish('leaf/server/data', data)

        electrovalvula.estado = True
        electrovalvula.save()
        #mandar mensaje mqtt

    return redirect(url_for('show_zona',zona_id=zona_id))

@login_required
@app.route('/desactivarRiego/<int:zona_id>/')
def desactivar_riego(zona_id):
    if not current_user.is_authenticated or current_user.is_admin:
        return redirect(url_for('index'))

    #seleccionar zona mediante id
    zona = Zona.get_by_id(zona_id)
    if zona is None:
        abort(404)

    if Zona.get_by_user_id(current_user.id).count(zona) < 1:
        abort(401)

    electrovalvula = ElectroValvula.get_by_zona_id(zona.id)
    if electrovalvula is not None:
        datosDic = {
            'id': f'{electrovalvula.mac}', 
            'estado':False
            }
        data = json.dumps(datosDic)
        mqtt.publish('leaf/server/data', data)

        electrovalvula.estado = False
        electrovalvula.save()
        #mandar mensaje mqtt

    return redirect(url_for('show_zona',zona_id=zona_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    errors=[]
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is None or not user.check_password(form.password.data):
            errors.append("User doesn't exist")
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('show_huerto')
            return redirect(next_page)
    
    return render_template('login_form.html', form=form,errors=errors)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#solo accesible para admins
@login_required
@app.route('/registerFarmer/', methods=['GET', 'POST'])
def register_farmer():
    
    if not current_user.is_admin:
        return redirect(url_for('index'))

    form = SignupFarmerForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        if user is not None:
            error = f'The email {email} is already being used by another user'
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=name, email=email,is_admin=False )
            user.set_password(password)
            user.save()
            
            
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template("signup_farmer_form.html", form=form, error=error)


@app.errorhandler(404)
def page_not_found(error):
	return render_template("error.html",error="Page not found...",titulo="Not found"), 404

@app.errorhandler(401)
def page_not_permisos(error):
	return render_template("error.html",error="You do not have permission to access this content",titulo="Not permission"), 401

@app.errorhandler(500)
def page_server__error(error):
	return render_template("error.html",error="unexpected error",titulo="unexpected error"), 500




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




def validarYguardarRegistro(payload):

	# Deserializar JSON
    temp, hum, soil = "A","A","A"
    try:
        dic = json.loads(payload)
        mac = dic.get("id")
        temp = dic.get("temp")
        hum = dic.get("hum")
        soil = dic.get("soil")

        exito = validarDatos(mac,temp,hum,soil)
        if exito:
            try:
                sensor = Sensor.get_by_mac(mac)
                if sensor is not None:
                    sensor_id = sensor.id
                    try:
                        newRegistro = Registro(temperatura = temp,humedad=hum,humedadTerrestre=soil,sensor_id=sensor_id)
                        Registro.save(newRegistro)
                        print("Datos registrados")
                    except:
                        pass
            except:
                pass
    except JSONDecodeError as e:
        print("JSONDecodeError")
        print(e)

    
def validarDatos(mac,temp,hum,soil):
    result = False
    
    try:
        temp = float(temp)
        hum = float(hum)
        soil = float(soil)
        if temp>0 and temp <100 and hum>0 and hum<100 and soil>0 and soil <100 :
            x = re.search("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",mac)
            if x:
                result = True
        else:
            print("Error: fuera de rango")
        
    except:
        print("Error: tipo de dato incorrecto")

    

    
    
    return result


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('leaf/server/records')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    payload = data["payload"]
    validarYguardarRegistro(payload)   