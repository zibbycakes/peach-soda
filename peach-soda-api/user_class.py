class User:
    instances = []
    def __init__(self, user_id, username, first_name):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.is_authenticated = False
        self.is_active = False
        self.is_anonymous = False
        User.instances.append(self)

    def get_id(self):
        return self.user_id
    
    def set_authenticated(self, authenticated):
        self.is_authenticated = authenticated
    
    def set_activated(self, activated):
        self.is_active = activated

    def get(user_id):
        for i in range(len(User.instances)):
            if User.instances[i].user_id == user_id:
                return User.instances[i]
        return None
    