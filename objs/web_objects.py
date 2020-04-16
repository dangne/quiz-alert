import requests
import re
import objs.colors as colors
from bs4 import BeautifulSoup
from datetime import datetime

STATUS_COLOR = {
    'Submitted':colors.GREEN,
    'Not submitted':colors.YELLOW,
    'Due soon!':colors.RED,
    'Overdue!':colors.RED_FG,
    'Not opened':colors.GREY
}



class Quiz:
    def __init__(self, html, name):
        self.html = html
        self.name = name 
        self.start = None
        self.due = None
        self.status = None

        self.parse_quiz()
        self.show()

    def parse_quiz(self):
        if self.html != None:
            soup = BeautifulSoup(self.html, 'html5lib')
            main = soup.find('div', role='main')

            # Extract start and due date
            quizinfo = main.find('div', class_='box quizinfo').text
            dates = re.findall(r'([MTWFS]\w*day, \d\d? [A-Z]\w* \d{4}, \d\d?:\d\d [AP]M)', quizinfo)
            if len(dates) == 1:
                self.due = datetime.strptime(dates[0], '%A, %d %B %Y, %I:%M %p')
            elif len(dates) == 2:
                self.start = datetime.strptime(dates[0], '%A, %d %B %Y, %I:%M %p') 
                self.due = datetime.strptime(dates[1], '%A, %d %B %Y, %I:%M %p')

            # Extract submissions
            attempts = main.find('table', class_='generaltable quizattemptsummary')

            # Calculate status
            if attempts != None:
                self.status = 'Submitted'
            else:
                if self.start != None and self.start > self.start.today():
                    self.status = 'Not opened'
                elif self.due != None and (self.due - self.due.today()).days <= 0:
                    self.status = 'Overdue!'
                elif self.due != None and (self.due - self.due.today()).days <= 3:
                    self.status = 'Due soon!'
                else:
                    self.status = 'Not submitted'

        else:
            self.status = 'Not opened'

    def show(self):
        color = STATUS_COLOR[self.status]
        output = ' '*4 + f'{color}Quiz | {str(self.status):13} | Due: {str(self.due):19} | {self.name}'
        output = (output[:110] + '..') if len(output) > 110 else output 
        print(output + colors.DEFAULT)
    


class Assignment:
    def __init__(self, html, name):
        self.html = html
        self.name = name 
        self.due = None
        self.status = None

        self.parse_assignment()
        self.show()

    def parse_assignment(self):
        if self.html != None:
            soup = BeautifulSoup(self.html, 'html5lib')
            table = soup.find('table', class_='generaltable')

            # Extract due date
            due_text = table.tbody('tr')[2]('td')[1].text
            self.due = datetime.strptime(due_text, '%A, %d %B %Y, %I:%M %p')

            # Calculate status
            status_text = table.tbody('tr')[0]('td')[1].text
            if status_text == 'Đã nộp':
                self.status = 'Submitted'
            else:
                if self.due != None and (self.due - self.due.today()).days <= 0:
                    self.status = 'Overdue!'
                elif self.due != None and (self.due - self.due.today()).days <= 3:
                    self.status = 'Due soon!'
                else:
                    self.status = 'Not submitted'

        else:
            self.status = 'Not opened'

    def show(self):
        color = STATUS_COLOR[self.status]
        output = ' '*4 + f'{color}Assm | {str(self.status):13} | Due: {str(self.due):19} | {self.name}'
        output = (output[:110] + '..') if len(output) > 110 else output 
        print(output + colors.DEFAULT)
        


class Course:
    def __init__(self, ses, html, name):
        self.ses = ses
        self.html = html
        self.name = name
        self.quizzes = []
        self.assignments = []
        self.parse_course()

    def parse_course(self):
        soup = BeautifulSoup(self.html, 'html5lib')
        print_flag = False

        # Extract quizzes
        quizzes = soup.find_all('li', class_='activity quiz modtype_quiz')
        if len(quizzes) > 0 and not print_flag:
            print(' '*2 + f'{self.name}')
            print_flag = True

        for quiz in quizzes:
            try: quiz_html = self.ses.get(quiz.find('a')['href']).content
            except: quiz_html = None
            quiz_name = quiz.find('span', class_='instancename').contents[0]
            self.quizzes.append(Quiz(quiz_html, quiz_name))

        # Extract assignments
        assignments = soup.find_all('li', class_='activity assign modtype_assign')
        if len(assignments) > 0 and not print_flag:
            print(' '*2 + f'{self.name}')
            print_flag = True

        for assignment in assignments:
            try: assignment_html = self.ses.get(assignment.find('a')['href']).content
            except: assignment_html = None
            assignment_name = assignment.find('span', class_='instancename').contents[0]
            self.assignments.append(Assignment(assignment_html, assignment_name))

    def show(self):
        print(' '*2 + f'{self.name}')
        for quiz in self.quizzes: quiz.show()
        for assm in self.assignments: assm.show()

    def get_quizzes(self):
        return self.quizzes

    def get_assignments(self):
        return self.assignments
    


class MyELearning:
    def __init__(self, ses, html):
        self.ses = ses
        self.html = html
        self.courses = []

        print('Accessed MyELearning Page')
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

    def show(self):
        for course in self.courses:
            course.show()

    def get_courses(self):
        return self.courses



class LoginPage:
    STUDENT_LOGIN_PAGE = 'https://sso.hcmut.edu.vn/cas/login?service=http%3A%2F%2Fe-learning.hcmut.edu.vn%2Flogin%2Findex.php%3FauthCAS%3DCAS'

    def __init__(self, ses, url=STUDENT_LOGIN_PAGE):
        self.ses = ses
        self.url = url
        self.html = ses.get(url).content

        print('Accessed Login Page')
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
