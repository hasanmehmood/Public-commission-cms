from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, validators, DateField
from wtforms.validators import Required


class LoginForm(Form):
	username = TextField('username', validators = [Required()])
	password = PasswordField('password', validators = [Required()])
	

class AddContactForm(Form):
	name = TextField('name', validators = [Required()])
	number = TextField('number', validators = [Required()])
	description = TextField('description', validators = [Required()])

	
class AddUserForm(Form):
	username = TextField('username', validators = [Required()])
	password = PasswordField('password', validators = [Required()])
	contact = TextField('contact', validators = [Required()])
	email = TextField('email', validators = [Required()])
	sec = TextField('sec', validators = [Required()])

	
class AddDoc(Form):
	title = TextField('title', validators = [Required()])
	content = TextField('contact', validators = [Required()])
	

class AddComment(Form):
	name = TextField('name', validators = [Required()])
	comment = TextField('comment', validators = [Required()])



