from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo
from sam2020.models import Samuser, Paper
from flask_login import current_user
from wtforms.fields.html5 import DateField

'''Login Forms'''


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user1 = Samuser.query.filter_by(username=username.data).first()
        if user1:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user2 = Samuser.query.filter_by(email=email.data).first()
        if user2:
            raise ValidationError('That email is taken. Please choose a different one')


class LoginForm(FlaskForm):
    email = StringField('Username/Email',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ForgotPass(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    def validate_email(self, email):
        user2 = Samuser.query.filter_by(email=email.data).first()
        if user2 is None:
            raise ValidationError('There is no account with that email')

    submit = SubmitField('Request Password Reset')


class ResetPassForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Reset Password')


'''End Login Forms'''
'''Account Update Form'''


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if current_user.username != username.data:
            user1 = Samuser.query.filter_by(username=username.data).first()
            if user1:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        if current_user.email != email.data:
            user2 = Samuser.query.filter_by(email=email.data).first()
            if user2:
                raise ValidationError('That email is taken. Please choose a different one')


'''Author Forms'''


class SubmitPaper(FlaskForm):
    title = StringField('Paper Title', validators=[DataRequired()])
    paperId = StringField('Paper ID')
    other_authors = StringField('Other Authors', description="Please use example format Ex: John,Smith; Wright,Fenix;")
    file = FileField('Upload File', validators=[DataRequired(),
                                                FileAllowed(['doc', 'docx', 'pdf'],
                                                            'Only doc, docx, pdf files types are allowed')])
    submit = SubmitField('Submit')

    def validate_title(self, title):
        ex_paper = Paper.query.filter_by(title=title.data, author_id=current_user.u_id).first()
        if ex_paper:
            raise ValidationError('You have already submitted a paper by this name. Are you trying to update?')


class UpdatePaper(FlaskForm):
    id = HiddenField("Id")
    title = StringField('Paper Title', validators=[DataRequired()])
    other_authors = StringField('Other Authors', description="Please use example format Ex: John,Smith; Wright,Fenix;")
    last_updated_on = StringField('Last updated on')
    file = FileField('Upload File', validators=[DataRequired(),
                                                FileAllowed(['doc', 'docx', 'pdf'],
                                                            'Only doc, docx, pdf files types are allowed')])
    submit = SubmitField('Update')

    def validate_title(self, title):
        ex_paper = Paper.query.filter_by(title=title.data, author_id=current_user.u_id).first()
        if ex_paper:
            if self.id.data != str(ex_paper.p_id):
                raise ValidationError('You have already submitted a paper by this name. Are you trying to update?')


'''-------Admin Forms------'''


class AdminRegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    type = SelectField('User Type(Role)', choices=[('1', 'Admin'), ('2', 'PCC'), ('3', 'PCM'), ('3', 'Author')],
                       validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user1 = Samuser.query.filter_by(username=username.data).first()
        if user1:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user2 = Samuser.query.filter_by(email=email.data).first()
        if user2:
            raise ValidationError('That email is taken. Please choose a different one')


class AdminUserUpdateForm(FlaskForm):
    id = HiddenField("id")
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    type = SelectField('User Type(Role)', choices=[('1', 'Admin'), ('2', 'PCC'), ('3', 'PCM'), ('3', 'Author')],
                       validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user1 = Samuser.query.filter_by(username=username.data).first()
        if user1:
            if user1.u_id != self.id:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user2 = Samuser.query.filter_by(email=email.data).first()
        if user2:
            if str(user2.u_id) != self.id.data:
                raise ValidationError('That email is taken. Please choose a different one')


class SubmitReview(FlaskForm):
    title = StringField('Paper Title', validators=[DataRequired()])
    paperId = StringField('Paper ID')
    submit = SubmitField('Submit')
    review = StringField('Review', validators=[DataRequired()])
    last_updated_on = StringField('Last updated on')
    submit = SubmitField('Submit Review')


class CreateDeadlineForm(FlaskForm):
    name = StringField('Deadline Name', validators=[DataRequired()])
    deadlinedate = DateField('Deadline Date', format='%Y-%m-%d')
    submit = SubmitField('Create Deadline')


class UpdateDeadlineForm(FlaskForm):
    id = HiddenField("id")
    name = StringField('Deadline Name', validators=[DataRequired()])
    deadlinedate = DateField('Deadline Date', format='%Y-%m-%d')
    submit = SubmitField('Update')


'''-----End Admin Forms-----'''
'''-----PCC Forms-----------'''


class setReviewerForm(FlaskForm):
    id = HiddenField("id")
    reviewer = SelectField('Reviewer', choices=[],
                           validators=[DataRequired()])
    submit = SubmitField('Set Reviewer')


class ratingForm(FlaskForm):
    id = HiddenField("id")
    score = SelectField('Score', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)],
                        validators=[DataRequired()])
    submit = SubmitField('Give Score')
    
class viewReviewForm(FlaskForm):
    review_text = StringField("Review text", validators=[DataRequired()])
    reviewed_by = StringField("Reviewed by", validators=[DataRequired()])
    
class viewRatingForm(FlaskForm):
    rating_score = IntegerField("Rating Score", validators=[DataRequired()])
    rated_by = StringField("Rated by", validators=[DataRequired()])

class updateRatingForm(FlaskForm):
    score = SelectField('Score',
                        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)],
                        validators=[DataRequired()])
    submit = SubmitField('Update Rating')

'''-------End PCC Forms-----'''

'''-------PCM Forms--------'''
class createReviewForm(FlaskForm):
    review_text = StringField("Review text", validators=[DataRequired()])
    submit = SubmitField("Create")

class updateReviewForm(FlaskForm):
    review_text = StringField("Review text", validators=[DataRequired()])
    submit = SubmitField("Update")

'''------End PCM Forms------'''