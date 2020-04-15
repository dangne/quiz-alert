import requests
import re
import colors
from bs4 import BeautifulSoup
from datetime import datetime



class Quiz:
    def __init__(self, html, name):
        self.html = html
        self.name = name 
        self.start = None
        self.due = None
        self.status = None
        self.parse_quiz()

    def parse_quiz(self):
        if self.html != None:
            soup = BeautifulSoup(self.html, 'html5lib')
            main = soup.find('div', role='main')

            # Get start and due
            quizinfo = main.find('div', class_='box quizinfo').text
            dates = re.findall(r'([MTWFS]\w*day, \d\d? [A-Z]\w* \d{4}, \d\d?:\d\d [AP]M)', quizinfo)
            if len(dates) == 1:
                self.due = datetime.strptime(dates[0], '%A, %d %B %Y, %I:%M %p')
            elif len(dates) == 2:
                self.start = datetime.strptime(dates[0], '%A, %d %B %Y, %I:%M %p') 
                self.due = datetime.strptime(dates[1], '%A, %d %B %Y, %I:%M %p')

            # Check for submission
            attempts = main.find('table', class_='generaltable quizattemptsummary')
            if attempts == None:
                self.status = 'Not submitted'
            else:
                self.status = 'Submitted'
    


class Assignment:
    def __init__(self, html, name):
        self.html = html
        self.name = name 
        self.due = None
        self.status = None
        self.parse_assignment()

    def parse_assignment(self):
        if self.html != None:
            soup = BeautifulSoup(self.html, 'html5lib')
            table = soup.find('table', class_='generaltable')
            due = table.tbody('tr')[2]('td')[1].text

            self.status = 'Submitted' if table.tbody('tr')[0]('td')[1].text == 'Đã nộp' else 'Not submitted'
            self.due = datetime.strptime(due, '%A, %d %B %Y, %I:%M %p')
        


class Course:
    def __init__(self, ses, html, name):
        self.ses = ses
        self.html = html
        self.name = name
        self.quizzes = []
        self.assignments = []
        self.parse_course()

    def parse_course(self):
        def extract_quizzes(soup):
            quizzes = soup.find_all('li', class_='activity quiz modtype_quiz')

            for quiz in quizzes:
                try: quiz_html = self.ses.get(quiz.find('a')['href']).content
                except: quiz_html = None
                quiz_name = quiz.find('span', class_='instancename').contents[0]
                self.quizzes.append(Quiz(quiz_html, quiz_name))

        def extract_assignments(soup):
            assignments = soup.find_all('li', class_='activity assign modtype_assign')

            for assignment in assignments:
                try: assignment_html = self.ses.get(assignment.find('a')['href']).content
                except: assignment_html = None
                assignment_name = assignment.find('span', class_='instancename').contents[0]
                self.assignments.append(Assignment(assignment_html, assignment_name))

        soup = BeautifulSoup(self.html, 'html5lib')
        extract_quizzes(soup)
        extract_assignments(soup)

    def get_quizzes(self):
        return self.quizzes

    def get_assignments(self):
        return self.assignments
    


class MyELearning:
    def __init__(self, ses, html):
        self.ses = ses
        self.html = html
        self.courses = []
        self.parse_myel()

    def parse_myel(self):
        soup = BeautifulSoup(self.html, 'html5lib')
        content = soup.find('div', class_='content')

        start_flag = False
        for element in content.contents:
            if element.name == 'span' and not start_flag:
                start_flag = True
            elif element.name == 'span' and start_flag:
                return
            elif element.name == 'div':
                course_html = self.ses.get(element.find('a')['href']).content
                course_name = element.find('a')['title']
                self.courses.append(Course(self.ses, course_html, course_name))

    def get_courses(self):
        return self.courses

    def get_summary(self):
        for course in self.courses:
            if len(course.quizzes) == 0 and len(course.assignments) == 0: continue
            print(course.name)
            for quiz in course.quizzes:
                color = colors.GREEN if quiz.status == 'Submitted' else colors.YELLOW
                print(f'\t{color}Quiz | {str(quiz.status):13} | Due: {str(quiz.due):20} | {quiz.name}')
                print(colors.DEFAULT, end='')

            for assm in course.assignments:
                color = colors.GREEN if assm.status == 'Submitted' else colors.YELLOW
                print(f'\t{color}Assm | {str(assm.status):13} | Due: {str(assm.due):20} | {assm.name}')
                print(colors.DEFAULT, end='')



class LoginPage:
    STUDENT_LOGIN_PAGE = 'https://sso.hcmut.edu.vn/cas/login?service=http%3A%2F%2Fe-learning.hcmut.edu.vn%2Flogin%2Findex.php%3FauthCAS%3DCAS'

    def __init__(self, ses, url=STUDENT_LOGIN_PAGE):
        self.ses = ses
        self.url = url
        self.html = ses.get(url).content
        self.parse_login_page()

    def parse_login_page(self):
        soup = BeautifulSoup(self.html, 'html5lib')

        self.lt = soup.find('input', attrs={'name':'lt'})['value']
        self.execution = soup.find('input', attrs={'name':'execution'})['value']
        self._eventId = soup.find('input', attrs={'name':'_eventId'})['value']
        self.submit = soup.find('input', attrs={'name':'submit'})['value']

    def get_login_data(self, account):
        return {
            'username': account.username,
            'password': account.password,
            'lt': self.lt,
            'execution': self.execution,
            '_eventId': self._eventId,
            'submit': self.submit
        }

    def login(self, account):
        login_data = self.get_login_data(account)
        response = self.ses.post(self.url, login_data).content
    
        return response