# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
POSTS_PER_PAGE=10
def get_catagory():
    catagory_name=request.args(0)
    catagory=db.catagory(name=catagory_name)
    if not catagory:
        session.flash='page not found'
        redirect(URL('index'))
    return catagory

def index():
    #http://127.0.0.1:8000/reddit_clone/default/index
    rows =db(db.catagory).select()
    return locals()
@auth.requires_login()
def create_post():
    #http://127.0.0.1:8000/reddit_clone/default/create_post/<catagory>
    catagory=get_catagory()
    db.post.catagory.default=catagory.id
    form=SQLFORM(db.post).process(next='view_post/[id]')
    return locals()
@auth.requires_login()
def edit_post():
    #http://127.0.0.1:8000/reddit_clone/default/edit_post/<id>
    id=request.args(0,cast=int)
    form=SQLFORM(db.post,id,showid=False).process(next='view_post/[id]')
    return locals()


def list_posts_new():
    catagory=get_catagory()
    return locals()

def list_posts_by_datetime():
    #http://127.0.0.1:8000/reddit_clone/default/list_posts_by_datetime/<catagory>/<page>
    response.view='default/list_posts_by_votes.html'
    catagory=get_catagory()
    page=request.args(1,cast=int,default=0)
    start=page*POSTS_PER_PAGE
    stop=start+POSTS_PER_PAGE
    rows=db(db.post.catagory==catagory.id).select(orderby=~db.post.created_on,limitby=(start,stop))
    return locals()

def list_posts_by_author():
    #http://127.0.0.1:8000/reddit_clone/default/list_posts_by_author/<user_id>/<page>
    response.view='default/list_posts_by_votes.html'
    user_id=request.args(0,cast=int)
    page=request.args(1,cast=int,default=0)
    start=page*POSTS_PER_PAGE
    stop=start+POSTS_PER_PAGE
    rows=db(db.post.created_by==user_id).select(orderby=~db.post.created_on,limitby=(start,stop))
    return locals()

def list_posts_by_votes():
    #http://127.0.0.1:8000/reddit_clone/default/list_posts_by_votes/<catagory>/<page>
    
    catagory=get_catagory()
    page=request.args(1,cast=int,default=0)
    start=page*POSTS_PER_PAGE
    stop=start+POSTS_PER_PAGE
    rows=db(db.post.catagory==catagory.id).select(orderby=~db.post.votes,limitby=(start,stop))
    return locals()

def view_post():
    #http://127.0.0.1:8000/reddit_clone/default/view_post/<id>
    id=request.args(0,cast=int)
    post=db.post(id) or redirect(URL('index'))
    comment=db(db.comm.post==post.id).select(orderby=~db.comm.created_on,limitby=(0,1)).first()
    if auth.user:
        db.comm.post.default=id
        db.comm.parent_comm.default=comment.id if comment else None
        form=SQLFORM(db.comm).process()
    else:
        form=A("Login to comment",_href=URL('user/login',vars=dict(_next=URL(args=request.args))))
    comments=db(db.comm.post==post.id).select(orderby=db.comm.created_on)
    return locals()


def vote_callback():
    #http://127.0.0.1:8000/reddit_clone/default/vote_callback/?id=2&&direction=up
    vars=request.post_vars
    if vars and auth.user:
        id=vars.id
        direction= 1 if vars.direction=='up' else -1
        post=db.post(id)
        if post:
            vote=db.vote(post=id,created_by=auth.user.id)
            if not vote:
                post.update_record(votes=post.votes+direction)
                db.vote.insert(post=id,score=direction)
            elif vote.score!=direction:
                post.update_record(votes=post.votes+direction)
                vote.update_record(score=direction)
            else:
                pass #voter voted twice in same direction
    return str(post.votes)

def comm_vote_callback():
    #http://127.0.0.1:8000/reddit_clone/default/comm_vote_callback/<comm_id>/<up or down>
    id=request.args(0,cast=int)
    direction=request.args(1)
    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
