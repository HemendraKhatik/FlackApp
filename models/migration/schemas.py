"""
                      List of relations
 Schema |            Name            | Type  |     Owner
--------+----------------------------+-------+----------------
 public | active_storage_attachments | table | vfobhheluegnpw
 public | active_storage_blobs       | table | vfobhheluegnpw
 public | ahoy_events                | table | vfobhheluegnpw
 public | ahoy_visits                | table | vfobhheluegnpw
 public | ar_internal_metadata       | table | vfobhheluegnpw
 public | assessments                | table | vfobhheluegnpw
 public | behaviors                  | table | vfobhheluegnpw
 public | friendly_id_slugs          | table | vfobhheluegnpw
 public | image                      | table | vfobhheluegnpw
 public | img                        | table | vfobhheluegnpw
 public | schema_migrations          | table | vfobhheluegnpw
 public | sections                   | table | vfobhheluegnpw
 public | settings                   | table | vfobhheluegnpw
 public | user_channel               | table | vfobhheluegnpw
 public | user_signup_data           | table | vfobhheluegnpw
 public | users                      | table | vfobhheluegnpw
 public | versions                   | table | vfobhheluegnpw

 @author:   kaloneh <kaloneh@gmail.com>
 @comment:  This script is gonna create all schemas' required by application, however, at this time there is
            only an overview and to do list in which will be developed.
"""
from . import AbstractSchema


class schemas(AbstractSchema):
    def __init__(self, db, **kwargs):
        self.super = super(AbstractSchema, self)
        super().__init__(db=db, associated_sql=kwargs.get('associated_sql', 'user_channel_table.sql'),
                            sql_delimiter=kwargs.get('sql_delimiter', ';'))

    def get_schema(self, table_name):
        pass

