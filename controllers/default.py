# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
POSTS_PER_PAGE=10
def get_catagory():                                                         #for the website or the back_end
    catagory_name=request.args(0)
    catagory=db.catagory(name=catagory_name)
    if not catagory:
        session.flash='page not found'
        redirect(URL('index'))
    return catagory

def populate_db():                  #for the testing
    db.users.insert(
		first_name="John",
		last_name="Doe",
		email="cs1110200@cse.iitd.ac.in",
		username="cs1110200",
		entry_no="2011CS10200",
		type_=0,
		password="john",
	)

def logged_in():    #session handling
    return dict(success=auth.is_logged_in(), user=auth.user)

def logout():           #session handling
    return dict(success=True, loggedout=auth.logout())

@request.restful()
def api():          #api to get generic patterns and getting parsed json response
    response.view = 'generic.'+request.extension
    def GET(*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    def POST(table_name,**vars):
        return db[table_name].validate_and_insert(**vars)
    def PUT(table_name,record_id,**vars):
        return db(db[table_name]._id==record_id).update(**vars)
    def DELETE(table_name,record_id):
        return db(db[table_name]._id==record_id).delete()
    return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE)

def login():        # for api to login usin app usin gGET method
    userid = request.vars.userid
    password = request.vars.password
    user = auth.login_bare(userid,password)
    return dict(success=False if not user else True, user=user)


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
def edit_post():            #to edit the post
    #http://127.0.0.1:8000/reddit_clone/default/edit_post/<id>
    id=request.args(0,cast=int)
    form=SQLFORM(db.post,id,showid=False).process(next='view_post/[id]')
    return locals()


def list_posts_new():
    catagory=get_catagory()
    return locals()

def list_posts_by_datetime():       #sort posts to show the latest first
    #http://127.0.0.1:8000/reddit_clone/default/list_posts_by_datetime/<catagory>/<page>
    response.view='default/list_posts_by_votes.html'
    catagory=get_catagory()
    page=request.args(1,cast=int,default=0)
    start=page*POSTS_PER_PAGE
    stop=start+POSTS_PER_PAGE
    rows=db(db.post.catagoryy==catagory.id).select(orderby=~db.post.created_on,limitby=(start,stop))
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
    rows=db(db.post.catagoryy==catagory.id).select(orderby=~db.post.votes,limitby=(start,stop))
    return locals()

def view_post():        #to view the post
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


def vote_callback():            #voting at backend
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
                post.update_record(votes=post.votes+direction*2)
                vote.update_record(score=direction)
            else:
                pass #voter voted twice in same direction
    return str(post.votes)

def comm_vote_callback():       #voting for comments
    #http://127.0.0.1:8000/reddit_clone/default/comm_vote_callback/<comm_id>/<up or down>
    vars=request.post_vars
    if vars and auth.user:
        id=vars.id
        direction= 1 if vars.direction=='up' else -1
        comm=db.comm(id)
        if comm:
            vote=db.comm_vote(comm=id,created_by=auth.user.id)
            if not vote:
                comm.update_record(votes=comm.votes+direction)
                db.comm_vote.insert(comm=id,score=direction)
            elif vote.score!=direction:
                comm.update_record(votes=comm.votes+direction*2)
                vote.update_record(score=direction)
            else:
                pass #voter voted twice in same direction
    return str(comm.votes)


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
