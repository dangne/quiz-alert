import os



class Account:

    def __init__(self, filename='account.txt'):
        self.username = None
        self.password = None
        self.filename = filename

        if os.path.exists(self.filename):
            self.load_account()
        else:
            self.create_account()

    def create_account(self):
        print('-'*10, 'Create account', '-'*10)
        self.username = input('Your username: ')
        self.password = input('Your password: ')
        self.save_account()
        print('-'*34)

    def save_account(self):
        try:
            with open(self.filename, 'w') as f:
                f.write(self.username + '\n')
                f.write(self.password)

        except IOError:
            print(f'Error while saving account to {self.filename}')

    def load_account(self):
        try:
            with open(self.filename, 'r') as f:
                self.username, self.password = f.read().split()

        except IOError:
            print(f'Error while loading account from {self.filename}')
        
    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def set_username(self, username):
        self.username = username
        
    def set_password(self, password):
        self.password = password
