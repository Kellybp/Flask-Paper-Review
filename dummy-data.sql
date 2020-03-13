-- Insert Users into table first
-- 1 Admin
-- 1 PCC
-- 3 PCMs
-- 2 Authors

-- Admin
INSERT INTO Samuser(u_type, f_name, l_name, username, email, pwd_hash)
VALUES(1, 'admin', 'person', 'admin', 'admin@gmail.com', '$2b$12$d0sm22hSfl29Zb2TSRqbEejn2.ZsGbMHdCIona9X018zKJgDhs3Te');

-- PCC
INSERT INTO Samuser(u_type, f_name, l_name, username, email, pwd_hash)
VALUES(2, 'pcc', 'person', 'pcc', 'pcc@verizon.net', '$2b$12$d0sm22hSfl29Zb2TSRqbEejn2.ZsGbMHdCIona9X018zKJgDhs3Te');

-- PCM
INSERT INTO Samuser(u_type, f_name, l_name, username, email, pwd_hash)
VALUES(3, 'pcm', 'one', 'pcm1', 'pcm@hotmail.com', '$2b$12$d0sm22hSfl29Zb2TSRqbEejn2.ZsGbMHdCIona9X018zKJgDhs3Te');

INSERT INTO Samuser(u_type, f_name, l_name, username, email, pwd_hash)
VALUES(3, 'pcm', 'two', 'pcm2', 'pcm@yahoo.com', '$2b$12$d0sm22hSfl29Zb2TSRqbEejn2.ZsGbMHdCIona9X018zKJgDhs3Te');

INSERT INTO Samuser(u_type, f_name, l_name, username, email, pwd_hash)
VALUES(3, 'pcm', 'three', 'pcm3', 'pcm@aol.com', '$2b$12$d0sm22hSfl29Zb2TSRqbEejn2.ZsGbMHdCIona9X018zKJgDhs3Te');

-- Author
INSERT INTO Samuser(u_type, f_name, l_name, username, email, pwd_hash)
VALUES(4, 'author', 'one', 'author1', 'author1@gmail.com', '$2b$12$d0sm22hSfl29Zb2TSRqbEejn2.ZsGbMHdCIona9X018zKJgDhs3Te');

INSERT INTO Samuser(u_type, f_name, l_name, username, email, pwd_hash)
VALUES(4, 'author', 'two', 'author2', 'author2@gmail.com', '$2b$12$d0sm22hSfl29Zb2TSRqbEejn2.ZsGbMHdCIona9X018zKJgDhs3Te');

-- Next insert papers
-- They won't have review ids or rating ids yet so those will be null
-- This is authored by the first user
INSERT INTO Paper(author_id, other_authors, times_submitted, uri, title)
VALUES ((SELECT Samuser.u_id FROM Samuser WHERE username = 'author1'), 'Ashish Galagali, Brian Kelly', 2, 'static/papers/dummy_one.pdf', 'The Winds of Winter');

INSERT INTO Paper(author_id, other_authors, times_submitted, uri, title)
VALUES((SELECT Samuser.u_id FROM Samuser WHERE username = 'author2'), '', 1, 'static/papers/dummy_two.pdf', 'The Best Paper');

INSERT INTO Deadline(deadline_date, created_by_id, name)
VALUES('2020-1-1', (SELECT Samuser.u_id FROM Samuser WHERE u_type = 1), 'New Years Deadline');

-- DECLARE pcm1_id = (SELECT u_id FROM Samuser WHERE username='pcm1');
-- DECLARE pcm2_id = (SELECT u_id FROM Samuser WHERE username='pcm2');
-- DECLARE pcm3_id = (SELECT u_id FROM Samuser WHERE username='pcm3');
--
-- -- Paper 1 Reviews
-- INSERT INTO Review(pcm, review_text, times_submitted, submission_timestamp)
-- VALUES (pcm1_id, 'This paper was great!', 1, current_timestamp);
--
-- INSERT INTO Review(pcm, review_text, times_submitted, submission_timestamp)
-- VALUES (pcm2_id, 'This paper was bad!', 40, current_timestamp);
--
-- INSERT INTO Review(pcm, review_text, times_submitted, submission_timestamp)
-- VALUES (pcm3_id, 'This paper was okay at best.', 3, current_timestamp);
--
-- DECLARE 1review_id = (SELECT review_id, FROM Review WHERE review_text = 'This paper was great!');
-- DECLARE 2review_id = (SELECT review_id, FROM Review WHERE review_text = 'This paper was bad!');
-- DECLARE 3review_id = (SELECT review_id, FROM Review WHERE review_text = 'This paper was okay at best.');
--
-- DECLARE pcc_id = (SELECT u_id FROM Samuser WHERE username='pcc');
--
-- -- Paper 1 Rating
-- INSERT INTO Rating(review1_id, review2_id, review3_id, pcc, score, submission_timestamp)
-- VALUES (1review_id, 2review_id, 3review_id, pcc_id, 7, current_timestamp);
--
-- -- Paper 2 Rating
-- INSERT INTO Rating()
-- VALUES();
