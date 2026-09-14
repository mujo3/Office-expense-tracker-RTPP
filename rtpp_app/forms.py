# rtpp_app/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    DateField,
    FileField,
    SubmitField
)
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo

class LoginForm(FlaskForm):
    email    = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit   = SubmitField('Sign In')

class ForcePasswordChangeForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),          # make sure field is not empty
            Length(min=8)            # require at least 8 characters
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")      # must match password field
        ]
    )
    submit = SubmitField("Change Password")

class InvoiceForm(FlaskForm):
    # Step 2 fields: Vendor & Category
    vendor         = SelectField('Vendor', coerce=int, validators=[DataRequired()])
    category       = SelectField('Category', coerce=int, validators=[DataRequired()])

    #  Step 1 fields: Invoice details
    invoice_number   = StringField('Invoice Number', validators=[DataRequired()])
    fiscal_number    = StringField('Fiscal Receipt Number', validators=[Optional()])
    order_number     = StringField('Order Number', validators=[Optional()])
    date_of_issue    = DateField('Date of Issue', format='%Y-%m-%d', validators=[DataRequired()])
    date_of_delivery = DateField('Date of Delivery', format='%Y-%m-%d', validators=[Optional()])
    due_date         = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    place_of_issue   = StringField('Place of Issue', validators=[Optional()])
    payment_method   = SelectField(
        'Payment Method',
        choices=[('virman','Virman'), ('cash','Cash'), ('card','Card')],
        validators=[DataRequired()]
    )
    reference        = StringField('Reference / Notes', validators=[Optional()])

    #  File upload for invoice photo
    photo  = FileField('Invoice Photo', validators=[Optional()])

    #  Submission button
    submit = SubmitField('Submit Invoice')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')
