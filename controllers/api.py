@request.restful()
def get_post():
    def GET(id):
        post=db.post(id)
        return post.as_dict() if post else None
    return locals()

def add_comment():
    if auth.is_logged_in():
        body=str(request.vars["body"])
        post_id=int(request.vars["id"])
        db.comm.insert(post=post_id,body=body,posted_by=auth.user.id)
        post=db.post(post_id)
        return dict(success=True)

def get_comments():
    id=int(request.vars["id"])
    comments=db(db.comm.post==id).select()
    list=[]
    for comm in comments:
        if comm.post==id:
            list.append(comm.body)
    return list
def add_complaint():
    if auth.is_logged_in():
        #idm=int(request.vars["id"])
        #user=db.users(idm)
        resolved=str(request.vars["resolved"]).strip()
        catagory=str(request.vars["catagoryy"]).strip()
        complaint_level=int(request.vars["complaint_level"])
        title=str(request.vars["title"]).strip()
        db.post.insert(
            Resolved=resolved,complaint_level=complaint_level,title=title,catagoryy=catagory,posted_by=auth.user.id)
        return auth.user.id

def comment_vote():
    if auth.is_logged_in():
        id = int(request.vars["id"])
        vote = int(request.vars["vote"])
        comm=db.comm(id)
        if comm:
            comm.update_record(votes=comm.votes+vote)
            return dict(success=True,comm=comm)
def set_resolved():
    if auth.is_logged_in():
        id = int(request.vars["id"])
        sta = str(request.vars["status"])
        post=db.post(id)
        if post:
            post.update_record(Resolved=sta)
            return dict(success=True,post=post)
    return locals()

def up_downvote():
    if auth.is_logged_in():
        id = int(request.vars["id"])
        vote = int(request.vars["vote"])
        post=db.post(id)
        if post:
            post.update_record(votes=post.votes+vote)
            return dict(success=True,post=post)
    return dict(success=True)
@request.restful()
def post():
    def GET(*args,**vars):
        patterns=['/{post.complaint_level}',
                 '/catagory/id/{catagory.id}',
                 '/by-user/{post.created_by}']
        parsed=db.parse_as_rest(patterns,args,vars)
        if parsed.status==200:return dict(content=parsed.response)
        raise HTTP(parsed.status,parsed.error)
    #def POST(catagory,title,resolved,url,body,votes):
        #return db.post.validate_and_insert(catagory=catagory,title=title,resolved=resolved,url=url if url else None,body=body,votes=votes)
    return locals()
@request.restful()
def auto():
    def GET(*args,**vars):
        parsed=db.parse_as_rest('auto',args,vars)
        if parsed.status==200:return dict(content=parsed.response)
        raise HTTP(parsed.status,parsed.error)
    return locals()
