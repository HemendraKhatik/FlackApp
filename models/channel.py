"""
@author:    kaloneh <kaloneh@gmail.com>
@comment:   The user channel abstract model and its communication via database
"""

from datetime import datetime
from .migration import schemas
from .exceptions import DBException
from .user import User


class Channel:
    """
    @author:    kaloneh <kaloneh@gmail.com>
    @comment:   Abstract user channel structure
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.channel = kwargs.get('channel', None)
        self.description = kwargs.get('description', None)
        self.u_id = kwargs.get('u_id', None)
        self.creation_time = kwargs.get('creation_time', datetime.now())
        self.last_update = kwargs.get('last_update', datetime.now())

    def __str__(self):
        return "{channel} <{description}>".format(channel=self.channel, description=self.description)


class ChannelDAO:
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
        schemas(self._db, table="user_channel").execute()

    def drop_schema(self):
        schemas(self._db, table="user_channel").execute(False)

    def findChannelByChannelName(self, channel_name: str):
        """
        find the specified channel by channel_name and returns either :Channel instance or None if parameter is valid
        and the database engine is connected unless it raise an :Exception
        :param channel_name: a string object with respect to definition of channel name
        :return: either of :Channel, None, or an :Exception
        """
        try:
            user_chnl = self._db.execute("SELECT * FROM user_channel where channel=:channel_name",
                                         {"channel_name": channel_name}).fetchall()
            return Channel(
                id=user_chnl['id'],
                channel=user_chnl['channel'],
                description=user_chnl['description'],
                u_id=user_chnl['u_id']
            )
        except DBException as e:
            raise "%s" % e

    def findChannelByUserID(self, userID):
        """
        find the specified user by email and returns either :User instance or None if parameter is valid
        and the database engine is connected unless it raise an :Exception
        :param userID: a string object with respect to definition of email address and set of allowed characters
        :return: either of :User, None, or an :Exception
        """
        try:
            if isinstance(userID, User):
                u_id = userID.id
            else:
                u_id = int(userID)  # if it's not an int instance an Exception will be thrown
            user_chnl = self._db.execute("SELECT * FROM user_channel where u_id=:u_id", {"u_id": u_id}).fetchall()
            return Channel(
                id=user_chnl['id'],
                channel=user_chnl['channel'],
                description=user_chnl['description'],
                u_id=user_chnl['u_id']
            )
        except DBException as e:
            raise "%s" % e

    def findChannelByChannelID(self, cid):
        """
        find the specified user by email and returns either :User instance or None if parameter is valid
        and the database engine is connected unless it raise an :Exception
        :param cid: :int
        :return: either of :Channel, None, or an :Exception
        """
        try:
            user_chnl = self._db.execute("SELECT * FROM user_channel where id=:_id", {"_id": cid}).fetchone()
            return Channel(
                id=user_chnl['id'],
                channel=user_chnl['channel'],
                description=user_chnl['description'],
                u_id=user_chnl['u_id']
            )
        except DBException as e:
            raise "%s" % e

    def findChannel(self, glue='OR', **kwargs):
        """
        find some specific channels if the conditions hold on the datatable
        unless returns either None on throws a :DBException
        :param kwargs: ``id``, ``channel``, or ``u_id``
        :return: :set of :Channel instances or either of :None and :DBException
        """
        where = {'id': kwargs.get("id", None), 'channel': kwargs.get("channel", None),
                 'u_id': kwargs.get("u_id", None)}
        cond = filter(lambda v: v[1] is not None, where.items())
        if len(cond) > 0:
            t, w = ([], {})
            for k, v in cond:
                t.append("%s=:%s" % (k, k))
                w[k] = v
            try:
                usr_channel = self._db.execute(
                    "SELECT * FROM user_channel {terms}".format(terms=" {0} ".format(glue).join(t)), w).fetchall()
                if usr_channel:
                    return Channel(
                        id=usr_channel['id'], channel=usr_channel['channel'],
                        description=usr_channel['description'], u_id=usr_channel['u_id']
                    )
                else:
                    return None
            except DBException as e:
                raise "%s" % e
        else:
            raise DBException("To find channel(s) in the table you have to specify id, channel, or u_id.")

    def findall(self):
        """
        fetch all user channels from database and returns either a set of :Channel instances or an empty set if
        parameter is valid and the database engine is connected unless it raise an :Exception
        :return: either of a set of :Channel instances, a None object, or an :Exception
        """
        try:
            channels = self._db.execute("SELECT * FROM user_channel").fetchall()
            chset = set()
            if len(channels) > 0:
                for c in channels:
                    chset.add(Channel(id=c['id'], channel=c['channel'], description=c['description'], u_id=c['u_id']))
            return chset
        except DBException as e:
            raise "%s" % e

    def saveChannel(self, usr_channel):
        """
        Storing a specific user channel into datatable
        :param usr_channel: an instance of :Channel
        :return: :True will be returned if transaction is completed unless the return value will be set to :False.
        """
        try:
            ret = self._db.execute(
                "INSERT INTO user_channel (channel, description, u_id) VALUES (:c,:d,:u_id)",
                {"c": usr_channel.channel, "d": usr_channel.description, "u_id": usr_channel.u_id}
            )
            self._db.commit()
            return ret is not None
        except DBException as e:
            raise "%s" % e

    def editChannel(self, usr_channel):
        """
        manipulate the channel fields except messages
        :param usr_channel: an instance of :Channel
        :return: :True will be returned if transaction is completed unless the return value will be set to :False.
        """
        try:
            ret = self._db.execute(
                "UPDATE user_channel SET channel=:c, description=:d, u_id=:u_id WHERE id=:id",
                {"id": usr_channel.id, "c": usr_channel.channel, "d": usr_channel.description, "u_id": usr_channel.u_id}
            )
            self._db.commit()
            return ret is not None
        except DBException as e:
            raise "%s" % e

    def deleteChannel(self, usr_channel):
        """
        deletes a specified channel
        :param usr_channel: an instance of :Channel
        :return: :True will be returned if transaction is completed unless the return value will be set to :False.
        """
        try:
            ret = self._db.execute("DELETE FROM user_channel where id=:id", {"id": usr_channel.id})
            self._db.commit()
            return ret is not None
        except DBException as e:
            raise "%s" % e
