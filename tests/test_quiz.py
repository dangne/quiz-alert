import objs.colors as colors
from datetime import datetime, timedelta
from objs.web_objects import Quiz, Assignment
from bs4 import BeautifulSoup

def test_quiz_1():
    with open('tests/quiz_1.html', 'r') as page:
        title = 'Mock test quiz 1'
        quiz = Quiz(page, title)
        due = datetime.strptime('Monday, 30 March 2020, 3:15 PM', '%A, %d %B %Y, %I:%M %p')

        assert quiz.html != None
        assert quiz.title == title
        assert quiz.start == None
        assert quiz.due == due
        assert quiz.status == 'Submitted'

def test_quiz_2():
    with open('tests/quiz_2.html', 'r') as page:
        title = 'Mock test quiz 2'
        quiz = Quiz(page, title)
        start = datetime.strptime('Thursday, 16 April 2020, 12:00 PM', '%A, %d %B %Y, %I:%M %p')
        due = datetime.strptime('Wednesday, 22 April 2020, 8:15 AM', '%A, %d %B %Y, %I:%M %p')

        assert quiz.html != None
        assert quiz.title == title
        assert quiz.start == start
        assert quiz.due == due
        if start.today() < start:
            assert quiz.status == 'Not opened'
        elif due < due.today():
            assert quiz.status == 'Overdue!'
        elif due < due.today() + timedelta(days=3):
            assert quiz.status == 'Due soon!'
        else:
            assert quiz.status == 'Not submitted'

def test_quiz_3():
    with open('tests/quiz_3.html', 'r') as page:
        title = 'Mock test quiz 3'
        quiz = Quiz(page, title)

        assert quiz.html != None
        assert quiz.title == title
        assert quiz.start == None
        assert quiz.due == None
        assert quiz.status == 'Not submitted'

def test_quiz_4():
    with open('tests/quiz_4.html', 'r') as page:
        title = 'Mock test quiz 4'
        quiz = Quiz(page, title)

        assert quiz.html != None
        assert quiz.title == title
        assert quiz.start == None
        assert quiz.due == None
        assert quiz.status == 'Submitted'

def test_quiz_5():
    with open('tests/quiz_5.html', 'r') as page:
        title = 'Mock test quiz 5'
        quiz = Quiz(page, title)
        start = datetime.strptime('Friday, 10 April 2020, 12:00 PM', '%A, %d %B %Y, %I:%M %p')
        due = datetime.strptime('Sunday, 19 April 2020, 1:30 PM', '%A, %d %B %Y, %I:%M %p')

        assert quiz.html != None
        assert quiz.title == title
        assert quiz.start == start
        assert quiz.due == due
        assert quiz.status == 'Submitted'

if __name__ == '__main__':
    test_quiz()
