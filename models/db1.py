# -*- coding: utf-8 -*-
db.define_table('catagory',Field('name',
                requires=(IS_SLUG(),IS_NOT_IN_DB(db,'catagory.name'))))

db.define_table('post',
                Field('catagory','reference catagory',writable=False,readable=False),
                Field('title','string',requires=IS_NOT_EMPTY()),
                Field('Resolved','string',requires=IS_NOT_EMPTY()),
                Field('url',requires=IS_EMPTY_OR(IS_URL())),
                Field('body','string',requires=IS_NOT_EMPTY()),
                Field('votes','integer',default=0,writable=False,readable=False),
                auth.signature)

db.define_table('vote',
                Field('post','reference post'),
                Field('score','integer',default=+1),
                auth.signature)
                
db.define_table('comm',
                Field('post','reference post',writable=False,readable=False),
                Field('parent_comm','reference comm',writable=False,readable=False),
                Field('votes','integer',default=0,writable=False,readable=False),
                Field('body','text'),
                auth.signature)

db.define_table('comm_vote',
                Field('comm','reference comm'),
                Field('score','integer',default=+1),
                auth.signature)

def author(id):
    if id is None:
        return "Unknown"
    else:
        user=db.auth_user(id)
        return A('%(first_name)s %(last_name)s' %user,_href=URL('list_posts_by_author',args=user.id)) 
from gluon.contrib.populate import populate
if db(db.auth_user).count()<2:
    populate(db.auth_user,100)
    db.commit()
if db(db.post).count()<500:
    populate(db.post,500)
    db.commit()
