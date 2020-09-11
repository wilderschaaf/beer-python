from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    name = StringField('Name', [
        DataRequired()])
    password = StringField('Password', [
        DataRequired()])
    submit = SubmitField('Submit')

    # def validate_name(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')
    #
    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')
