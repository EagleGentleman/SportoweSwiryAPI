import jwt

from flask import abort, current_app
from datetime import datetime, timedelta
from SportoweSwiryAPI_app import db
from marshmallow import Schema, fields, validate, validates, ValidationError
import hashlib
import binascii

class User(db.Model):
    __tableName__ = 'usersAPI'
    id = db.Column(db.String(50), unique=True, nullable=False , primary_key=True)
    name = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    mail = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean, default=True)
    isAddedByGoogle = db.Column(db.Boolean, default=False)
    isAddedByFb = db.Column(db.Boolean, default=False)

    # event_admin = db.relationship('Event', backref='admin', lazy='dynamic')
    # events = db.relationship('Participation', backref='user', lazy='dynamic')
    # activities = db.relationship('Activities', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.name} {self.lastName}'


    @staticmethod
    def generate_ID(name: str, lastName: str) -> str:

        sufix = 0

        id = name[0:3] + lastName[0:3] + str(sufix)
        user=User.query.filter(User.id == id).first()

        while user != None:
            sufix +=1
            print(sufix)
            id = name[0:3] + lastName[0:3] + str(sufix)
            user=User.query.filter(User.id == id).first()

        return id

    def hash_password(self):
        """Hash a password for storing."""
        # the value generated using os.urandom(60)
        os_urandom_static = b"ID_\x12p:\x8d\xe7&\xcb\xf0=H1\xc1\x16\xac\xe5BX\xd7\xd6j\xe3i\x11\xbe\xaa\x05\xccc\xc2\xe8K\xcf\xf1\xac\x9bFy(\xfbn.`\xe9\xcd\xdd'\xdf`~vm\xae\xf2\x93WD\x04"
        #os_urandom_static = b"ID_\x12p:\x8d\xe7&\xcb\xf0=H1"
        salt = hashlib.sha256(os_urandom_static).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', self.password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii') 

    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'),
        salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

    def removeAccents(self):
        strange='ŮôῡΒძěἊἦëĐᾇόἶἧзвŅῑἼźἓŉἐÿἈΌἢὶЁϋυŕŽŎŃğûλВὦėἜŤŨîᾪĝžἙâᾣÚκὔჯᾏᾢĠфĞὝŲŊŁČῐЙῤŌὭŏყἀхῦЧĎὍОуνἱῺèᾒῘᾘὨШūლἚύсÁóĒἍŷöὄЗὤἥბĔõὅῥŋБщἝξĢюᾫაπჟῸდΓÕűřἅгἰშΨńģὌΥÒᾬÏἴქὀῖὣᾙῶŠὟὁἵÖἕΕῨčᾈķЭτἻůᾕἫжΩᾶŇᾁἣჩαἄἹΖеУŹἃἠᾞåᾄГΠКíōĪὮϊὂᾱიżŦИὙἮὖÛĮἳφᾖἋΎΰῩŚἷРῈĲἁéὃσňİΙῠΚĸὛΪᾝᾯψÄᾭêὠÀღЫĩĈμΆᾌἨÑἑïოĵÃŒŸζჭᾼőΣŻçųøΤΑËņĭῙŘАдὗპŰἤცᾓήἯΐÎეὊὼΘЖᾜὢĚἩħĂыῳὧďТΗἺĬὰὡὬὫÇЩᾧñῢĻᾅÆßшδòÂчῌᾃΉᾑΦÍīМƒÜἒĴἿťᾴĶÊΊȘῃΟúχΔὋŴćŔῴῆЦЮΝΛῪŢὯнῬũãáἽĕᾗნᾳἆᾥйᾡὒსᾎĆрĀüСὕÅýფᾺῲšŵкἎἇὑЛვёἂΏθĘэᾋΧĉᾐĤὐὴιăąäὺÈФĺῇἘſგŜæῼῄĊἏØÉПяწДĿᾮἭĜХῂᾦωთĦлðὩზკίᾂᾆἪпἸиᾠώᾀŪāоÙἉἾρаđἌΞļÔβĖÝᾔĨНŀęᾤÓцЕĽŞὈÞუтΈέıàᾍἛśìŶŬȚĳῧῊᾟάεŖᾨᾉςΡმᾊᾸįᾚὥηᾛġÐὓłγľмþᾹἲἔбċῗჰხοἬŗŐἡὲῷῚΫŭᾩὸùᾷĹēრЯĄὉὪῒᾲΜᾰÌœĥტ'
        ascii_replacements='UoyBdeAieDaoiiZVNiIzeneyAOiiEyyrZONgulVoeETUiOgzEaoUkyjAoGFGYUNLCiIrOOoqaKyCDOOUniOeiIIOSulEySAoEAyooZoibEoornBSEkGYOapzOdGOuraGisPngOYOOIikoioIoSYoiOeEYcAkEtIuiIZOaNaicaaIZEUZaiIaaGPKioIOioaizTIYIyUIifiAYyYSiREIaeosnIIyKkYIIOpAOeoAgYiCmAAINeiojAOYzcAoSZcuoTAEniIRADypUitiiIiIeOoTZIoEIhAYoodTIIIaoOOCSonyKaAsSdoACIaIiFIiMfUeJItaKEISiOuxDOWcRoiTYNLYTONRuaaIeinaaoIoysACRAuSyAypAoswKAayLvEaOtEEAXciHyiiaaayEFliEsgSaOiCAOEPYtDKOIGKiootHLdOzkiaaIPIIooaUaOUAIrAdAKlObEYiINleoOTEKSOTuTEeiaAEsiYUTiyIIaeROAsRmAAiIoiIgDylglMtAieBcihkoIrOieoIYuOouaKerYAOOiaMaIoht'
        translator=str.maketrans(strange,ascii_replacements)
        return self.id.translate(translator)

    def generate_jwt(self) -> str:
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(minutes=current_app.config.get('JWT_EXPIRED_MINUTES', 30))
        }
        return jwt.encode(payload, current_app.config.get('SECRET_KEY'))


class UserSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=50))
    lastName = fields.String(required=True, validate=validate.Length(max=50))
    mail = fields.String(required=True, validate=validate.Length(max=50))
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=8, max=500))
    isAdmin = fields.Boolean(dump_default=False)
    confirmed = fields.Boolean(dump_defaultdefault=True)
    isAddedByGoogle = fields.Boolean(dump_defaultdefault=False)
    isAddedByFb = fields.Boolean(dump_defaultdefault=False)

class UpdatePasswordUserSchema(Schema):
    current_password = fields.String(load_only=True, required=True, validate=validate.Length(min=8, max=500))
    new_password = fields.String(load_only=True, required=True, validate=validate.Length(min=8, max=500))

user_schema = UserSchema()
update_password_user_schema = UpdatePasswordUserSchema()