from datetime import datetime
from sam2020 import db, login_mngr, app
from flask_login import UserMixin

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_mngr.user_loader
def load_user(user_id):
    return Samuser.query.get(int(user_id))


class Usertype(db.Model):
    ut_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ut_name = db.Column(db.String(6), unique=True, nullable=False)

    # users           = db.relationship("User", backref='ass_user', lazy=True)

    def __repr__(self):
        return f"User_Type('{self.ut_name}')"


class Template(db.Model):
    temp_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uri = db.Column(db.String, unique=True, nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('samuser.u_id'), nullable=False)

    def __repr__(self):
        return f"Template('{self.uri}')"


class Samuser(db.Model, UserMixin):
    u_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    u_type = db.Column(db.Integer, db.ForeignKey('usertype.ut_id'), nullable=False)
    f_name = db.Column(db.String(120), nullable=False)
    l_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd_hash = db.Column(db.String, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        # lasts for 30 minutes
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.u_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Samuser.query.get(user_id)

    def get_id(self):
        try:
            return self.u_id
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    # template        = db.relationship("Template", backref='template_author', lazy=True)
    # reviews         = db.relationship("Review", backref='review_author', lazy=True)
    # ratings         = db.relationship("Rating", backref='rating_author', lazy=True)
    # reviewed_by_id1 = db.relationship("Paper", backref='r1', lazy=True)
    # reviewed_by_id2 = db.relationship("Paper", backref='r2', lazy=True)
    # reviewed_by_id3 = db.relationship("Paper", backref='r3', lazy=True)
    # author_id       = db.relationship("Paper", backref='r4', lazy=True)
    # rated_by_id     = db.relationship("Paper", backref='r5', lazy=True)

    def __repr__(self):
        return f"User('{self.u_type}','{self.f_name}','{self.l_name}', '{self.username})"


class Review(db.Model):
    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pcm = db.Column(db.Integer, db.ForeignKey('samuser.u_id'), nullable=False)
    review_text = db.Column(db.String, nullable=False)
    times_submitted = db.Column(db.Integer, default="1")
    submission_timestamp = db.Column(db.DateTime, nullable=True, default=datetime.utcnow())

    # rating1                 = db.relationship("Rating", backref='review1', lazy=True)
    # rating2                 = db.relationship("Rating", backref='review2', lazy=True)
    # rating3                 = db.relationship("Rating", backref='review3', lazy=True)

    def __repr__(self):
        return f"User('{self.pcm}','{self.review_text}','{self.times_submitted}')"


class Rating(db.Model):
    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    review1_id = db.Column(db.Integer, db.ForeignKey('review.review_id'), nullable=True)
    review2_id = db.Column(db.Integer, db.ForeignKey('review.review_id'), nullable=True)
    review3_id = db.Column(db.Integer, db.ForeignKey('review.review_id'), nullable=True)
    pcc = db.Column(db.Integer, db.ForeignKey('samuser.u_id'), nullable=False)
    score = db.Column(db.Float)
    submission_timestamp = db.Column(db.DateTime, nullable=True, default=datetime.utcnow())

    def __repr__(self):
        return f"User('{self.pcc}','{self.reviewer1}','{self.times_submitted}')"


class Deadline(db.Model):
    d_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    deadline_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('samuser.u_id'), nullable=True)
    name            = db.Column(db.String)


class Paper(db.Model):

    p_id            = db.Column(db.Integer, autoincrement=True, primary_key=True)
    review1_id         = db.Column(db.Integer, db.ForeignKey('review.review_id'), nullable=True)
    review2_id         = db.Column(db.Integer, db.ForeignKey('review.review_id'), nullable=True)
    review3_id         = db.Column(db.Integer, db.ForeignKey('review.review_id'), nullable=True)
    author_id       = db.Column(db.Integer, db.ForeignKey('samuser.u_id'))
    rating_id     = db.Column(db.Integer, db.ForeignKey('rating.rating_id'))
    other_authors   = db.Column(db.String)
    times_submitted = db.Column(db.Integer)
    uri             = db.Column(db.String)
    title           = db.Column(db.String)
    interested_pcm_ids = db.Column(db.String)
    assigned_pcm_ids   = db.Column(db.String)
    last_updated_on = db.Column(db.String)

    
    def __repr__(self):
        return f"Paper('{self.review1_id}','{self.review2_id}','{self.review3_id}," \
            f",'{self.author_id}','{self.rating_id}','{self.other_authors}','{self.times_submitted}'" \
            f",'{self.uri}','{self.title}')"