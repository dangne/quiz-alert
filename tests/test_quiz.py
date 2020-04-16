import objs.colors as colors
from datetime import datetime
from objs.web_objects import Quiz
from bs4 import BeautifulSoup

def test_quiz():
    with open('tests/quiz_1.html', 'r') as page:
        quiz = Quiz(page, 'Demo quiz')
        due = datetime.strptime('Monday, 30 March 2020, 3:15 PM', '%A, %d %B %Y, %I:%M %p')

        assert quiz.html != None
        assert quiz.name == 'Demo quiz'
        assert quiz.start == None
        assert quiz.due == due
        assert quiz.status == 'Submitted'

if __name__ == '__main__':
    test_quiz()
