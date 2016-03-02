# -*- coding: utf-8 -*-
db.define_table('catagory',Field('name'))

db.define_table('post',
                Field('catagory','reference catagory'),
                Field('title','string'),
                Field('body','text'),
                Field('votes','integer'),
                auth.signature)

db.define_table('vote',
                Field('post','reference post'),
                Field('score','integer',default=+1),
                auth.signature)

db.define_table('comm',
                Field('post','reference post'),
                Field('parent_comm','reference comm'),
                Field('votes','integer'),
                Field('body','text'),
                auth.signature)

db.define_table('comm_vote',
                Field('comm','reference comm'),
                Field('score','integer',default=+1),
                auth.signature)
