DROP TABLE IF EXISTS paper;
DROP TABLE IF EXISTS template;
DROP TABLE IF EXISTS deadline;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS samuser;
DROP TABLE IF EXISTS usertype CASCADE;

CREATE TABLE usertype (
    ut_id SERIAL NOT NULL PRIMARY KEY,
    ut_name varchar(30)
);

INSERT INTO usertype(ut_name) VALUES ('Admin');
INSERT INTO usertype(ut_name) VALUES ('PCC');
INSERT INTO usertype(ut_name) VALUES ('PCM');
INSERT INTO usertype(ut_name) VALUES ('Author');

CREATE TABLE samuser (
    u_id SERIAL NOT NULL PRIMARY KEY,
    u_type int REFERENCES usertype(ut_id),
    f_name varchar(50),
    l_name varchar(50),
    username varchar(35) UNIQUE,
    email varchar(50),
    pwd_hash varchar(256)
);

CREATE TABLE template (
    temp_id SERIAL NOT NULL PRIMARY KEY,
    uri VARCHAR(250),
    assigned_by int REFERENCES samuser(u_id)
);

CREATE TABLE review (
    review_id SERIAL NOT NULL PRIMARY KEY,
    pcm int REFERENCES samuser(u_id),
    review_text text,
    times_submitted int,
    submission_timestamp timestamp
);


CREATE TABLE rating (
    rating_id SERIAL NOT NULL PRIMARY KEY,
    review1_id int REFERENCES review(review_id),
    review2_id int REFERENCES review(review_id),
    review3_id int REFERENCES review(review_id),
    pcc int REFERENCES samuser(u_id),
    score float,
    submission_timestamp timestamp
);

CREATE TABLE paper (
    p_id SERIAL NOT NULL PRIMARY KEY,
    review1_id int REFERENCES review(review_id),
    review2_id int REFERENCES review(review_id),
    review3_id int REFERENCES review(review_id),
    author_id INT REFERENCES samuser(u_id),
    rating_id INT REFERENCES rating(rating_id),
    other_authors VARCHAR(250),
    times_submitted int,
    uri VARCHAR(250),
    title text,
    interested_pcm_ids varchar(200),
    assigned_pcm_ids varchar(200),
    last_updated_on VARCHAR(50)
);


CREATE TABLE deadline (
    d_id          SERIAL NOT NULL PRIMARY KEY,
    deadline_date timestamp,
    created_by_id int REFERENCES samuser(u_id),
    name varchar(100)
);
