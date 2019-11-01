"""
@author:    kaloneh <kaloneh@gmail.com>
@comment:   The user signup data abstract model and its communication via database
"""
from util.encryption import HashTable
from datetime import datetime
from .migration import schemas
from .exceptions import DBException


class User:
    """
    @author:    kaloneh <kaloneh@gmail.com>
    @comment:   Abstract user signup data structure
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.username = kwargs.get('username', None)
        self.email = kwargs.get('email', None)
        self.password = kwargs.get('password', None)
        self.creation_time = kwargs.get('creation_time', datetime.now())
        self.last_update = kwargs.get('last_update', datetime.now())

    def __str__(self):
        return "{username} <{email}>".format(username=self.username, email=self.email)


class UserDAO:
    """
    @author:    kaloneh <kaloneh@gmail.com>
    @comment:   This class's implemented in low level so that it prunes to maintain carefully
                and has to be applied with respect to high level API in the <link>sqlalchemy</link> package
    """

    def __init__(self, db, **kwargs):
        """
        :param db: global database connection which is passed by caller from top level, i.e., application.
        :param kwargs:
        """
        for key in kwargs:
            self.__setattr__(key, kwargs.get(key))
        self._db = db

    def build_schema(self):
        schemas(self._db, table="user_signup_data").execute()

    def drop_schema(self):
        schemas(self._db, table="user_signup_data").execute(False)

    def findUser(self, glue='OR', **kwargs):
        """
        find a specific user who is identified via :kwargs including ``id``, ``username``, or ``email``
        :param kwargs: ``id``, ``username``, or ``email``
        :return: :User instance
        """
        where = {'id': kwargs.get("id", None), 'username': kwargs.get("username", None),
                 'email': kwargs.get("email", None)}
        cond = filter(lambda v: v[1] is not None, where.items())
        if len(cond) > 0:
            t, w = ([], {})
            for k, v in cond:
                t.append("%s=:%s" % (k, k))
                w[k] = v
            try:
                user = self._db.execute(
                    "SELECT * FROM user_signup_data {terms}".format(terms=" {0} ".format(glue).join(t)), w).fetchone()
                if user:
                    return User(id=user.id, username=user.username, email=user.email, password=user.password)
                else:
                    return None
            except DBException as e:
                raise "%s" % e
        else:
            raise DBException("To find a user in the table you have to specify id, username, or email.")

    def findUserByUsername(self, username):
        """
        find the specified user by username and returns either :User instance or None if parameter is valid
        and the database engine is connected unless it raise an :Exception
        :param username: a string object with respect to definition of username
        :return: either of :User, None, or an :Exception
        """
        try:
            user = self._db.execute("SELECT * FROM user_signup_data where username=:username",
                                    {"username": username}).fetchone()
            if user:
                return User(id=user.id, username=user.username, email=user.email, password=user.password)
            else:
                return None
        except DBException as e:
            raise "%s" % e

    def findUserByEmail(self, email):
        """
        find the specified user by email and returns either :User instance or None if parameter is valid
        and the database engine is connected unless it raise an :Exception
        :param email: a string object with respect to definition of email address and set of allowed characters
        :return: either of :User, None, or an :Exception
        """
        try:
            user = self._db.execute("SELECT * FROM user_signup_data where email=:email", {"email": email}).fetchone()
            if user:
                return User(id=user.id, username=user.username, email=user.email, password=user.password)
            else:
                return None
        except DBException as e:
            raise "%s" % e

    def findall(self):
        """
        fetch all users from database and returns either a set of :User instances or an empty set if parameter
        is valid and the database engine is connected unless it raise an :Exception
        :return: either of a set of :User instances, a None object, or an :Exception
        """
        try:
            users = self._db.execute("SELECT * FROM user_signup_data").fetchall()
            usrset = set()
            if len(users) > 0:
                for u in users:
                    usrset.add(User(id=u.id, username=u.username, email=u.email, password=u.password))
            return usrset
        except DBException as e:
            raise "%s" % e

    def saveUser(self, user, encryptPassword=True):
        """
        Storing user in database. It's noticeable that it doesn't check uniqueness over username or password so that
        it has to be done with respect to ``findUser`` due to validating user data.
        :param user: an instance of :User
        :param encryptPassword: a boolean value whether indicates the password should be encrypted or not.
        :return: :True will be returned if transaction is completed unless the return value will be set to :False.
        """
        try:
            ret = self._db.execute(
                "INSERT INTO user_signup_data (username, email, password) VALUES (:username,:email,:password)",
                {"username": user.username, "email": user.email,
                 "password": HashTable().hexdigest(user.password) if encryptPassword else user.password}
            )
            self._db.commit()
            return ret
        except DBException as e:
            raise "%s" % e

    def editUser(self, user, encryptPassword=False):
        """
        typically, it's useful to handle changing password because username and email as unique keys often remain
        unchanged so that manipulating passwords with respect to this fact passing in plain text should be encrypted
        for security reasons.
        :param user: an instance of :User
        :param encryptPassword: a boolean value whether indicates the password should be encrypted or not.
        :return: :True will be returned if transaction is completed unless the return value will be set to :False.
        """
        try:
            ret = self._db.execute(
                "UPDATE user_signup_data SET username=:username, email=:email, password=:password where id=:id",
                {"id": user.id, "username": user.username, "email": user.email,
                 "password": HashTable().hexdigest(user.password) if encryptPassword else user.password}
            )
            self._db.commit()
            return ret
        except DBException as e:
            raise "%s" % e

    def deleteUser(self, user):
        """
        deletes a specified user
        :param user: an instance of :User
        :return: :True will be returned if transaction is completed unless the return value will be set to :False.
        """
        try:
            ret = self._db.execute("DELETE FROM user_signup_data where id=:id", {"id": user.id})
            self._db.commit()
            return ret
        except DBException as e:
            raise "%s" % e
