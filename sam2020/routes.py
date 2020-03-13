from flask import render_template, url_for, flash, redirect, request, session, send_file
from werkzeug.utils import secure_filename

from sam2020.forms import *
from sam2020 import app, db, bcrypt, mail
from sqlalchemy.orm import sessionmaker
from sam2020.models import *
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from flask_mail import Message
from sqlalchemy import or_, not_, and_

import ast

# Start up the DB api
engine = db.get_engine()
DB_Session = sessionmaker(engine)
db_session = DB_Session()


# Possible params: title


def send_notification(email, msgText):
    msg = Message('Sam2020 Notification',
                  sender='sam2020replymail@gmail.com',
                  recipients=[email])
    msg.body = f'''{msgText}'''
    mail.send(msg)


'''---------Login Routes-------'''


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_byemail = Samuser.query.filter_by(email=form.email.data).first()
            user_byname = Samuser.query.filter_by(username=form.email.data).first()
            if user_byemail:
                user_login = user_byemail
            else:
                user_login = user_byname
            if user_login and bcrypt.check_password_hash(user_login.pwd_hash, form.password.data):
                login_user(user_login, remember=form.remember.data)
                next_page = request.args.get('next')
                # session['CurrentUser'] = user_acct.json_string()
                return redirect(next_page) if next_page else redirect(url_for('home'))
            flash('Login unsuccessful. Please check email/username and password', 'danger')
    return render_template('entryPoints/login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = Samuser(username=form.username.data, email=form.email.data,
                               f_name=form.firstname.data, l_name=form.lastname.data,
                               pwd_hash=pwd, u_type=4)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=form.remember.data)
            # session['CurrentUser'] = user_acct.json_string()
            return redirect(url_for('home'))
    
    return render_template('entryPoints/register.html', title='Register', form=form)


@app.route("/forgotPass", methods=['GET', 'POST'])
def forgotPass():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ForgotPass()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_to_reset = Samuser.query.filter_by(email=form.email.data).first()
            send_reset_email(user_to_reset)
            flash('An email has been sent with instructions to reset your password', 'info')
            return redirect(url_for('login'))
        flash(f'Email {form.email.data} is invalid, please try again')
    return render_template('entryPoints/forgotPass.html', title='Forgot Password', form=form)


def send_reset_email(user):
    token = Samuser.get_reset_token(user)
    msg = Message('Password Reset Request',
                  sender='sam2020replymail@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('resetPass', token=token, _external=True)}

If you did not make this request, simply ignore this email
'''
    mail.send(msg)


@app.route("/resetPass/<token>", methods=['GET', 'POST'])
def resetPass(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Samuser.verify_reset_token(token)
    if user is None:
        flash('Your token is invalid', 'warning')
        return redirect(url_for('forgotPass'))
    form = ResetPassForm()
    if form.validate_on_submit():
        pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.pwd_hash = pwd
        db.session.commit()
        login_user(user, remember=form.remember.data)
        flash('Your password has been updated, You are now logged in', 'success')
        return redirect(url_for('home'))
    return render_template('entryPoints/reset.html', title='Reset Password', form=form)


@app.route("/logout")
def logout():
    """"User session logout"""
    logout_user()
    return redirect(url_for('login'))


'''---------End Login Routes-------'''
'''---------General Routes---------'''


# TODO: TEST
def getPapersForPCMToSelect(pcm_id):
    # return Paper.query(Paper.title, Paper.author_id).join(Paper.review1_id == Review.review_id).filter(
    #     Review.pcm == 1).all();
    papersOfInterest = Paper.query.filter(
        or_(Paper.interested_pcm_ids == None, Paper.interested_pcm_ids.notlike(f'%{pcm_id}%'))).all()
    print(f'pcm({pcm_id}) is interested in {len(papersOfInterest)} papers')
    return papersOfInterest


def getUsernamePCM(paper):
    if paper.assigned_pcm_ids is not None:
        review_ids = str(paper.assigned_pcm_ids).split(",")
        review_usernames = ""
        for id in review_ids:
            if id.isdigit():
                review_usernames = review_usernames + "," + (Samuser.query.filter_by(u_id=id).first().username)
        if review_usernames == "":
            return None
        return review_usernames.strip()
    else:
        return None


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    """
    Returns the user info along the papers list according to the user level
    :return:
    """
    if current_user.u_type == 1:
        # Admin
        renderer = 'Admin/adminHome.html'
        get_list = Samuser.query.filter_by()
    if current_user.u_type == 2:
        # PCC
        renderer = 'PCC/PCCHome.html'
        get_need_rating = Paper.query.filter_by(rating_id=None)
        get_need_reviews = Paper.query.filter_by()
        for paper in get_need_reviews:
            paper.assigned_pcm_ids = getUsernamePCM(paper)
        
        return render_template(renderer, title="Home", list=get_need_reviews, list2=get_need_rating)
    if current_user.u_type == 3:
        # PCM
        renderer = 'PCM/PCMHome.html'
        get_list = getPapersForPCMToSelect(current_user.u_id)
    
    if current_user.u_type == 4:
        # Author
        renderer = 'Author/authorHome.html'
        get_list = getUserPapers(current_user.u_id)
    else:
        redirect(url_for('login'))
    
    return render_template(renderer, title="Home", list=get_list)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """User Account"""
    form = UpdateAccountForm()
    if current_user.u_type == 4:
        sideNavLink = 'Author/authorSideNav.html'
    if current_user.u_type == 3:
        sideNavLink = 'PCM/PCMSideNav.html'
    if current_user.u_type == 2:
        sideNavLink = 'PCC/PCCSideNav.html'
    if current_user.u_type == 1:
        sideNavLink = 'Admin/adminSideNav.html'
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.f_name = form.firstname.data
        current_user.l_name = form.lastname.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        send_notification(Samuser.query.filter_by(u_type=1).first().email, "Account update by:" + current_user.username)
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.firstname.data = current_user.f_name
        form.lastname.data = current_user.l_name
    return render_template('account.html', title='Account', form=form, sideNavLink=sideNavLink)


'''-----End General Routes------'''

'''--------Admin Routes-------'''


@app.route("/updateUser/<id>", methods=['GET', 'POST'])
def updateUser(id):
    edited_user = Samuser.query.filter_by(u_id=id)
    form = AdminUserUpdateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            edited_user.update(dict(username=form.username.data, email=form.email.data,
                                    f_name=form.firstname.data, l_name=form.lastname.data,
                                    u_type=int(form.type.data)))
            db.session.commit()
            flash('User creation successful.', 'Success')
            return redirect(url_for('home'))
        flash('User creation unsuccessful.', 'Danger')
    elif request.method == 'GET':
        form.username.data = edited_user.first().username
        form.email.data = edited_user.first().email
        form.firstname.data = edited_user.first().f_name
        form.lastname.data = edited_user.first().l_name
        form.type.data = edited_user.first().u_type
        form.id.data = edited_user.first().u_id
    return render_template('Admin/updateUser.html', title="Edit User", form=form)


@app.route("/newUser", methods=['GET', 'POST'])
def newUser():
    form = AdminRegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = Samuser(username=form.username.data, email=form.email.data,
                               f_name=form.firstname.data, l_name=form.lastname.data,
                               pwd_hash=pwd, u_type=int(form.type.data))
            db.session.add(new_user)
            db.session.commit()
            flash('User creation successful.', 'Success')
            return redirect(url_for('home'))
        flash('User creation unsuccessful.', 'Danger')
    return render_template('Admin/newUser.html', title="New User", form=form)


@app.route("/submissions", methods=['GET', 'POST'])
def submissions():
    get_list = Paper.query.filter_by()
    return render_template('Admin/adminSubmissions.html', title="Submissions", list=get_list)


@app.route("/templates", methods=['GET', 'POST'])
def templates():
    get_list = Template.query.filter_by()
    return render_template('Admin/adminTemplates.html', title="Templates", list=get_list)


@app.route("/createDeadline", methods=['GET', 'POST'])
def createDeadline():
    form = CreateDeadlineForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_deadine = Deadline(name=form.name.data, deadline_date=form.deadlinedate.data,
                                   created_by_id=int(current_user.u_id))
            db.session.add(new_deadine)
            db.session.commit()
            flash('Deadline creation successful.', 'Success')
            return redirect(url_for('deadlines'))
        flash('Deadline creation unsuccessful.', 'Danger')
    return render_template('Admin/createDeadline.html', title="Create Deadline", form=form)


@app.route("/updatedeadline/<id>", methods=['GET', 'POST'])
def updatedeadline(id):
    edited_deadline = Deadline.query.filter_by(d_id=id)
    form = UpdateDeadlineForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            edited_deadline.update(dict(name=form.name.data, deadline_date=form.deadlinedate.data))
            db.session.commit()
            flash('Deadline creation successful.', 'Success')
            return redirect(url_for('deadlines'))
        flash('Deadline creation unsuccessful.', 'Danger')
    elif request.method == 'GET':
        form.name.data = edited_deadline.first().name
        form.deadlinedate.data = edited_deadline.first().deadline_date
    return render_template('Admin/updatedeadline.html', title="Create Deadline", form=form)


# deadlines is also used by admin--see Author Routes


'''--------End Admin Routes-------'''

'''---------PCC Routes-------'''


@app.route("/ratings", methods=['GET', 'POST'])
def ratings():
    get_list = Rating.query.filter_by()
    return_list = []
    for listEl in get_list:
        return_list.append((Paper.query.filter_by(rating_id=listEl.rating_id).first().title, listEl))
    return render_template('PCC/PCCRatings.html', title="Ratings", list=return_list)


@app.route("/setReviewer/<id>", methods=['GET', 'POST'])
def setReviewer(id):
    paper_to_be_reviewed = Paper.query.filter_by(p_id=id)
    paper = paper_to_be_reviewed.first()
    form = setReviewerForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('Set successful.', 'Success')
        else:
            assignment = None
            if paper.assigned_pcm_ids is not None:
                if form.reviewer.data not in paper.assigned_pcm_ids.split(','):
                    assignment = str(paper.assigned_pcm_ids) + "," + str(form.reviewer.data)
            else:
                assignment = str(form.reviewer.data)
            
            if assignment is not None:
                paper_to_be_reviewed.update(dict(assigned_pcm_ids=assignment))
                review = Review(pcm=form.reviewer.data)
                db.session.add(review)
                db.session.flush()
                if paper.review1_id is None:
                    paper_to_be_reviewed.update(dict(review1_id=review.review_id))
                elif paper.review2_id is None:
                    paper_to_be_reviewed.update(dict(review2_id=review.review_id))
                elif paper.review3_id is None:
                    paper_to_be_reviewed.update(dict(review3_id=review.review_id))
            db.session.commit()
            send_notification(Samuser.query.filter_by(u_id=form.reviewer.data).first().email,
                              "You have been assigned a Paper")
            flash('Set successful.', 'Success')
            return redirect(url_for('home'))
        flash('Set unsuccessful.', 'Danger')
    elif request.method == 'GET':
        form.id.data = paper.p_id
        interestList = paper.interested_pcm_ids
        interestListAdj = set()
        interestedPCM = list()
        if interestList is not None and len(str(paper.interested_pcm_ids).split(",")) != 0:
            interestList = str(paper.interested_pcm_ids).split(",")
            for interest in interestList:
                usernaem = Samuser.query.filter_by(u_id=interest).first().username
                interest = (interest, usernaem)
                interestedPCM.append(usernaem)
                interestListAdj.add(interest)
        if len(interestListAdj) < 3:
            for pcm in Samuser.query.filter_by(u_type=3).all():
                if (pcm.username not in interestedPCM):
                    interestListAdj.add((pcm.u_id, pcm.username))
        form.reviewer.choices = interestListAdj
    
    return render_template('PCC/SetReviewer.html', title="Set Reviewer", form=form)


@app.route("/addScore/<id>", methods=['GET', 'POST'])
def addRating(id):
    rated_paper = Paper.query.filter_by(p_id=id)
    form = ratingForm()
    if request.method == 'POST':
        # if form.validate_on_submit():
        
        rating = Rating(pcc=current_user.u_id, score=form.score.data)
        db.session.add(rating)
        db.session.flush()
        rated_paper.update(dict(rating_id=rating.rating_id))
        db.session.commit()
        send_notification(Samuser.query.filter_by(u_id=rated_paper.first().author_id).first().email,
                          "Your paper has been rated")
        flash('Rating successful.', 'Success')
        return redirect(url_for('home'))
    reviews = []
    reviews.append(Review.query.filter_by(review_id=rated_paper.first().review1_id).first())
    reviews.append(Review.query.filter_by(review_id=rated_paper.first().review2_id).first())
    reviews.append(Review.query.filter_by(review_id=rated_paper.first().review3_id).first())
    
    return render_template('PCC/PCCaddRating.html', title="Add Rating", list=reviews, form=form)


@app.route("/updaterating/<id>", methods=['GET', 'POST'])
def updaterating(id):
    updated_review = Rating.query.filter_by(rating_id=id)
    paper = Paper.query.filter_by(rating_id=id).first()
    form = updateRatingForm()
    if request.method == 'POST':
        # if form.validate_on_submit():
        updated_review.update(dict(score=form.score.data))
        db.session.commit()
        
        send_notification(Samuser.query.filter_by(u_id=paper.author_id).first().email,
                          "Your paper rating has been changed")
        flash('Rating successful.', 'Success')
        return redirect(url_for('home'))
    form.score.data = updated_review.first().score
    reviews = []
    reviews.append(Review.query.filter_by(review_id=paper.review1_id).first())
    reviews.append(Review.query.filter_by(review_id=paper.review2_id).first())
    reviews.append(Review.query.filter_by(review_id=paper.review3_id).first())
    
    return render_template('PCC/PCCaddRating.html', title="Add Rating", list=reviews, form=form)


'''--------End PCC Routes-------'''


# get pcms assigned to a paper
@app.route("/papers/<paper_id>/pcms", methods=['GET'])
def getAssignedPCMS(paper_id):
    reviewers = []
    print(f'should find pcms for paper({paper_id})')
    targetPaper = Paper.query.filter_by(assigned_pcm_ids=paper_id).first()
    if targetPaper is not None:
        assignedPcms = ast.literal_eval(targetPaper.assigned_pcm_ids)
        for anAssignedPcmId in assignedPcms:
            reviewer = getPcm(anAssignedPcmId)
            if reviewer is not None:
                reviewers.append(reviewer)
    print(f'assigned reviewers for paper({paper_id}) is {reviewers}')
    return reviewers


def getPcm(pcm_id):
    return Samuser.query.filter_by(u_id=pcm_id).first()


# get reviews for a paper
@app.route("/papers/<paper_id>/reviews", methods=['GET'])
def getPaperReviews(paper_id):
    reviews = []
    print(f'should find reviews for paper({paper_id})')
    targetPaper = Paper.query.filter_by(p_id=paper_id).first()
    if targetPaper is not None:
        reviewIds = [targetPaper.review1_id, targetPaper.review2_id, targetPaper.review3_id]
        print(f'reviews for paper({paper_id}) => {reviewIds}')
        for aReviewId in reviewIds:
            currentReview = getReview(aReviewId)
            if currentReview is not None:
                reviews.append(currentReview)
    else:
        print(f'Couldn\'t retrieve paper with id ({paper_id})')
    
    print(f'reviews for paper({paper_id}) => {reviews}')
    # else:#i guess we'll return an empty list if the paper doesn't exist??
    return reviews


@app.route("/review/<reviewId>", methods=['GET'])
def getReview(reviewId):
    form = viewReviewForm()
    review = Review.query.filter_by(review_id=reviewId).first()
    if review is not None:
        form.review_text.data = review.review_text
        form.reviewed_by.data = Samuser.query.filter_by(u_id=review.pcm).first().username
    return render_template('PCC/PCCViewReviews.html', title="Review", form=form)


@app.route("/paperReview/<reviewId>", methods=['GET'])
def getPaperReview(reviewId):
    form = viewReviewForm()
    review = Review.query.filter_by(review_id=reviewId).first()
    if review is not None:
        form.review_text.data = review.review_text
        form.reviewed_by.data = Samuser.query.filter_by(u_id=review.pcm).first().username
    return render_template('Author/authorViewReview.html', title="Review", form=form)


@app.route("/rating/<ratingId>", methods=['GET'])
def getRating(ratingId):
    form = viewRatingForm()
    rating = Rating.query.filter_by(rating_id=ratingId).first()
    if rating is not None:
        form.rating_score.data = rating.score
        form.rated_by.data = Samuser.query.filter_by(u_id=rating.pcc).first().username
    return render_template('Author/authorViewRating.html', title="Review", form=form)


# get papers assigned to a PCM
@app.route("/pcm/<pcm_id>/assignedPapers", methods=['GET'])
def getAssignedPapers(pcm_id):
    print(f'finding papers pcm({pcm_id}) is assigned to')
    targetPapers = \
        Paper.query.filter(
            or_(
                Paper.review1_id == f'{pcm_id}'
                , Paper.review2_id == f'{pcm_id}'
                , Paper.review3_id == f'{pcm_id}'
            )).all()
    print(f'Pcm({pcm_id}) assigned {len(targetPapers)} papers')
    return targetPapers


'''---------PCM Routes-------'''


@app.route("/reviewPaper", methods=['GET', 'POST'])
def reviewPaper():
    form = createReviewForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            review = Review(review_text=form.review_text.data, pcm=current_user.u_id)
            # TODO: Connect to have timestamp be now
            db.session.add(review)
            db.session.commit()
            # send_notification(Samuser.query.filter_by(u_id=rated_paper.first().author_id).first().email, "Your paper has been rated")
            # TODO: Add notification
            flash('Review successful.', 'Success')
            return redirect(url_for('reviews'))
    return render_template('PCM/PCMreviewPaper.html', title="Review", form=form)


@app.route("/updateReview/<id>", methods=['GET', 'POST'])
def updateReview(id):
    up_review = Review.query.filter_by(review_id=id)
    form = updateReviewForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            up_review.update(dict(review_text=form.review_text.data, pcm=current_user.u_id))
            # TODO: Connect to pcm and have timestamp be now
            db.session.commit()
            # send_notification(Samuser.query.filter_by(u_id=rated_paper.first().author_id).first().email, "Your paper has been rated")
            # TODO: Add notification
            flash('Update successful.', 'Success')
            return redirect(url_for('reviews'))
    elif request.method == 'GET':
        form.review_text.data = up_review.first().review_text
    return render_template('PCM/PCMupdateReview.html', title="Update Review", form=form)


@app.route("/reviews", methods=['GET', 'POST'])
def reviews():
    get_list = Review.query.filter_by(pcm=current_user.u_id)
    # for listEl in get_list:
    # return render_template('PCM/PCMReviews.html', list=get_list)
    
    return_list = []
    for listEl in get_list:
        paper = Paper.query.filter_by(review1_id=listEl.review_id).first()
        if paper is None:
            paper = Paper.query.filter_by(review2_id=listEl.review_id).first()
            if paper is None:
                paper = Paper.query.filter_by(review3_id=listEl.review_id).first()
        return_list.append((paper, listEl))
    return render_template('PCM/PCMReviews.html', list=return_list)


@app.route("/addInterest/<id>", methods=['GET', 'POST'])
def addInterest(id):
    int_paper = Paper.query.filter_by(p_id=id)
    if int_paper.first().interested_pcm_ids is None:
        addedID = ""
    else:
        addedID = str(int_paper.first().interested_pcm_ids) + ","
    if int_paper.first().interested_pcm_ids is None or current_user.u_id not in int_paper.first().interested_pcm_ids.split(
            ","):
        addedID = str(addedID) + str(current_user.u_id)
        int_paper.update(dict(interested_pcm_ids=addedID))
        db.session.commit()
        flash('Interest expressed', 'Success')
    
    return redirect(url_for('home'))
    # get_list = Paper.query.filter_by()
    # return render_template('PCM/PCMHome.html', list=get_list, paperInterest=current_user.u_id)


@app.route("/showInterest/<paper_id>/<pcm_id>")
def setInterestInPaper(paper_id, pcm_id):
    print(f'paper id {paper_id}, pcm_id {pcm_id}')
    targetPaper = Paper.query.filter_by(p_id=paper_id).first()
    if targetPaper is None:
        # no paper with the given id
        print("no paper with givevn id found")
    else:
        currentInterestedPcms = []
        if targetPaper.interested_pcm_ids is None:
            # create fresh array of interested pcms
            currentInterestedPcms = [pcm_id]
        else:
            currentInterestedPcms = ast.literal_eval(targetPaper.interested_pcm_ids)
            currentInterestedPcms.append(pcm_id)
        targetPaper.interested_pcm_ids = currentInterestedPcms.__str__()
        db.session.commit()


# gets the papers a pcm is interested in
@app.route("/papersOfInterest/<pcm_id>", methods=['Get'])
def getPapersOfInterest(pcm_id):
    papersOfInterest = Paper.query.filter(Paper.interested_pcm_ids.like(f'%{pcm_id}%')).all()
    print(f'pcm({pcm_id}) is interested in {len(papersOfInterest)} papers')
    return papersOfInterest


'''--------End PCM Routes-------'''

'''---------Author Routes-------'''


@app.route("/deadlines", methods=['GET', 'POST'])
def deadlines():
    if current_user.u_type == 1:
        # Admin
        renderer = 'Admin/adminDeadlines.html'
    if current_user.u_type == 4:
        # Author
        renderer = 'Author/authorDeadlines.html'
    get_list = Deadline.query.filter_by()  # deadline_date='00:00:00'
    return render_template(renderer, title="Deadlines", list=get_list)


def save_file(file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file.filename)
    file_fn = random_hex + f_ext
    # file_path = os.path.join(app.root_path, 'static/papers', file_fn)
    file_path = 'static/papers/' + file_fn
    file.filename = file_fn
    file.save('sam2020/static/papers/' + file.filename)
    return file_path


@app.route('/return-files/')
def return_files_tut():
    try:
        filePath = request.args.get("filePath")
        return send_file(filePath)
    except Exception as e:
        return str(e)


@app.route("/submitPaper", methods=['GET', 'POST'])
def submitPaper():
    '''
    Submits/updates the paper.
    Update: /submitPaper?paperId=<p_id>
    POST data:
        {
           "author_id": "author user id",
           "other_authors" : "comma separated other author user ids",
           "title": "paper title",
           "file": the file object
        }
    :return: message : "Paper submitted successfully" or " Error message "
    '''
    form = SubmitPaper()
    if form.validate_on_submit():
        title = form.title.data
        other_authors = form.other_authors.data
        uri = save_file(request.files['file'])
        paper = Paper(title=title, other_authors=other_authors, author_id=current_user.u_id,
                      uri=uri, last_updated_on=str(datetime.now()))
        db_session.add(paper)
        msgText = "Paper: " + paper.title + " by " + Samuser.query.filter_by(
            u_id=paper.author_id).first().f_name + " submitted to Sam2020"
        db_session.commit()
        flash(f'Paper {form.title.data} submitted successfully!', 'success')
        if Samuser.query.filter_by(u_type=2).first() is not None:
            send_notification(Samuser.query.filter_by(u_type=2).first().email, msgText)
        return redirect(url_for('home'))
    return render_template('Author/paperSubmission.html', title='Submit Paper', form=form)


def getUserPapers(userId):
    """
    Gets the papers of the specified user form the DB

    :return: list[Paper]
    """
    return Paper.query.filter_by(author_id=userId).all()


@app.route("/updatePaper/<id>", methods=['GET', 'POST'])
def updatePaper(id):
    form = UpdatePaper()
    updated_paper = Paper.query.filter_by(p_id=id)
    if form.validate_on_submit():
        uri = save_file(request.files['file'])
        updated_paper.update(dict(title=form.title.data, other_authors=form.other_authors.data,
                                  uri=uri, last_updated_on=str(datetime.now())))
        db.session.commit()
        msgText = "Paper: " + updated_paper.first().title + " by " + Samuser.query.filter_by(
            u_id=updated_paper.first().author_id).first().f_name + " submitted to Sam2020"
        flash(f'Paper {form.title.data} submitted successfully!', 'success')
        if Samuser.query.filter_by(u_type=2).first() is not None:
            send_notification(Samuser.query.filter_by(u_type=2).first().email, msgText)
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.id.data = updated_paper.first().p_id
        form.title.data = updated_paper.first().title
        form.other_authors.data = updated_paper.first().other_authors
    return render_template('Author/updateSubmission.html', title='Update Paper', form=form)


@app.route("/getPapersAll", methods=['GET'])
def getPapersAll():
    """
    Gets 10 papers from the DB for every page (pagination)
    For ONLY PCC or Admin to view
    :return: list[Paper]
    """
    usertype = int(session["CurrentUser"]["u_type"])
    if usertype < 3:
        page = request.args.get('page', 1, type=int)
        print("ITEMS_PER_PAGE:", app.config['ITEMS_PER_PAGE'])
        papers = Paper.query.order_by(Paper.last_updated_on.desc()).paginate(page, app.config['ITEMS_PER_PAGE'], False)
        return render_template('home.html', title='Home', papers=papers.items)
    else:
        flash(f'Access denied!!!', 'error')


'''------End Author Routes-------'''
