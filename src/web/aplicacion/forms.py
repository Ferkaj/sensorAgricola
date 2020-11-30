from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email(),Length(min=6, max=35)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')

class SignupFarmerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register farmer')

class HuertoForm(FlaskForm):

    nombre = StringField('Name', validators=[DataRequired(),Length(min=6, max=25)])
    direccion = StringField('Address', validators=[DataRequired(),Length(min=6, max=25)])
    codigoPostal = StringField('Zip code', validators=[DataRequired(),Length(min=5, max=6)])
    localidad = StringField('Locality', validators=[DataRequired(),Length(min=6, max=25)])
    provincia = StringField('Province', validators=[DataRequired(),Length(min=6, max=25)])

    submit = SubmitField('Create')

class ZonaForm(FlaskForm):
    macRegEx = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

    nombre = StringField('Name', validators=[DataRequired(),Length(min=6, max=25)])
    descripcion = StringField('Description', validators=[DataRequired(),Length(min=6, max=25)])
    macSensor = StringField('MAC agricultural sensor', validators=[DataRequired(),Regexp(macRegEx,message="mac address not valid")])
    macElectroValvula = StringField('MAC solenoid valve', validators=[Regexp(macRegEx,message="mac address not valid")])
    
    submit = SubmitField('Submit')

class ProgramaRiegoForm(FlaskForm):
    titulo = StringField('Name', validators=[DataRequired(),Length(min=3,max=25)])
    fecha_inicio = DateTimeField(display_format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    fecha_fin = DateTimeField(display_format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    
    submit = SubmitField('Create')
