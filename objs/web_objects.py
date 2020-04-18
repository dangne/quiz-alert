import requests
import re
import concurrent.futures
import objs.colors as colors
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

STATUS_COLOR = {
    'Submitted':colors.GREEN,
    'Not submitted':colors.YELLOW,
    'Due soon!':colors.RED,
    'Overdue!':colors.RED_FG,
    'Not opened':colors.GREY
}



class Quiz:
    def __init__(self, html, title):
        self.html = html
        self.title = title 
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
                elif self.due != None and self.due <= self.due.today():
                    self.status = 'Overdue!'
                elif self.due != None and self.due <= self.due.today() + timedelta(days=3):
                    self.status = 'Due soon!'
                else:
                    self.status = 'Not submitted'

        else:
            self.status = 'Not opened'

    def show(self):
        color = STATUS_COLOR[self.status]
        output = ' '*4 + f'{color}Quiz | {str(self.status):13} | Due: {str(self.due):19} | {self.title}'
        output = (output[:110] + '..') if len(output) > 110 else output 
        print(output + colors.DEFAULT)
    


class Assignment:
    def __init__(self, html, title):
        self.html = html
        self.title = title 
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
                if self.due != None and self.due <= self.due.today():
                    self.status = 'Overdue!'
                elif self.due != None and self.due <= self.due.today() + timedelta(days=3):
                    self.status = 'Due soon!'
                else:
                    self.status = 'Not submitted'

        else:
            self.status = 'Not opened'

    def show(self):
        color = STATUS_COLOR[self.status]
        output = ' '*4 + f'{color}Assm | {str(self.status):13} | Due: {str(self.due):19} | {self.title}'
        output = (output[:110] + '..') if len(output) > 110 else output 
        print(output + colors.DEFAULT)
        


class Course:
    def __init__(self, ses, html, title):
        print(' '*2 + f'{title}')
        self.ses = ses
        self.html = html
        self.title = title 
        self.quizzes = []
        self.assignments = []
        self.parse_course()

    def parse_course(self):
        soup = BeautifulSoup(self.html, 'html5lib')

        # Extract quizzes
        quizzes = soup.find_all(class_='activity quiz modtype_quiz')

        # Get quizzes' titles
        quizzes_titles = [quiz.span.next_element for quiz in quizzes]

        # Get quizzes' htmls in multiple threads
        hrefs = self.get_quizzes_hrefs(quizzes)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            quizzes_htmls = executor.map(self.get_quizzes_html, hrefs)

        # Get quiz objects
        for html, title in zip(quizzes_htmls, quizzes_titles):
            try:
                self.quizzes.append(Quiz(html, title))
            except: 
                print(' '*4 + f'{colors.GREY}An error occurred while loading quiz {title}{colors.DEFAULT}')

        # Extract assignments
        assignments = soup.find_all(class_='activity assign modtype_assign')

        # Get assignments' titles
        assignments_titles = [assignment.span.next_element for assignment in assignments]

        # Get assignments' htmls in multiple threads
        hrefs = self.get_assignments_hrefs(assignments)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            assignment_htmls = executor.map(self.get_assignments_html, hrefs)

        # Get assignment objects
        for html, title in zip(assignment_htmls, assignments_titles):
            try:
                self.assignments.append(Assignment(html, title))
            except:
                print(' '*4 + f'{colors.GREY}An error occurred while loading assignment {title}{colors.DEFAULT}')

    def get_quizzes_html(self, href):
        try: html = self.ses.get(href).text
        except: html = None
        return html

    def get_assignments_html(self, href):
        try: html = self.ses.get(href).text
        except: html = None
        return html

    def get_quizzes_hrefs(self, quizzes):
        hrefs = []
        for quiz in quizzes:
            try: hrefs.append(quiz.a['href'])
            except: hrefs.append(None)

        return hrefs

    def get_assignments_hrefs(self, assignments):
        hrefs = []
        for assignment in assignments:
            try: hrefs.append(assignment.a['href'])
            except: hrefs.append(None)
        return hrefs

    def show(self):
        print(' '*2 + f'{self.title}')
        for quiz in self.quizzes: quiz.show()
        for assm in self.assignments: assm.show()

    def get_quizzes(self):
        return self.quizzes

    def get_assignments(self):
        return self.assignments
    


class MyELearning:
    def __init__(self, ses, html):
        print('Accessed MyELearning Page')
        self.ses = ses
        self.html = html
        self.courses = []
        self.parse_myel()

    def parse_myel(self):
        soup = BeautifulSoup(self.html, 'html5lib')

        # Get courses in the current semester
        courses = soup.find('div', class_='content')\
                      .select('span:nth-of-type(2)')[0]\
                      .find_previous_siblings('div', class_='course_list')

        courses = list(courses)[::-1]

        # Extract courses' hrefs and titles
        hrefs = [course.a['href'] for course in courses]
        titles = [course.a['title'] for course in courses]

        # Crawl courses' htmls in multiple threads
        with concurrent.futures.ThreadPoolExecutor() as executor:
            htmls = executor.map(lambda href: self.ses.get(href).text, hrefs)

        # Get course objects 
        for html, title in zip(htmls, titles):
            try:
                self.courses.append(Course(self.ses, html, title))
            except:
                print(' '*2 + f'{colors.GREY}An error occurred while loading the course {title}{colors.DEFAULT}')

    def show(self):
        for course in self.courses:
            course.show()

    def get_courses(self):
        return self.courses



class LoginPage:
    STUDENT_LOGIN_PAGE = 'https://sso.hcmut.edu.vn/cas/login?service=http%3A%2F%2Fe-learning.hcmut.edu.vn%2Flogin%2Findex.php%3FauthCAS%3DCAS'

    def __init__(self, ses, url=STUDENT_LOGIN_PAGE):
        print('Accessed Login Page')
        self.ses = ses
        self.url = url
        self.html = ses.get(url).text
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
        response = self.ses.post(self.url, login_data).text
    
        return response
