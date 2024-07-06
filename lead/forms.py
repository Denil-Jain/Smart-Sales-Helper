from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired

class LeadForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    enterprise_name = StringField('Enterprise Name', validators=[DataRequired()])
    lead_type = StringField('Type of Lead', validators=[DataRequired()])
    domain = StringField('Domain', validators=[DataRequired()])
    todo_actions = TextAreaField('To-do Actions', validators=[DataRequired()])
    next_follow_up = DateField('Next Follow-up', format='%Y-%m-%d', validators=[DataRequired()])
    action_needed = BooleanField('Action Needed')
    submit = SubmitField('Submit')
