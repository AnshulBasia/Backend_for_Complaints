@request.restful()
def get_post():  #api to get post with the id using GET
    def GET(id):
        post=db.post(id)
        return post.as_dict() if post else None
    return locals()

def notifications():  #api to get notifications for the logged in user
    if auth.is_logged_in():
        noti = db(db.notifications.user_id==auth.user.id).select(orderby=~db.notifications.created_at)
        db(db.notifications.user_id==auth.user.id).update(is_seen=1)
        return dict(notifications=noti)
        
def add_comment():      #api to comment on any post
    if auth.is_logged_in():
        body=str(request.vars["body"])
        post_id=int(request.vars["id"])
        db.comm.insert(post=post_id,body=body,posted_by=auth.user.id)
        post=db.post(post_id)
        return dict(success=True)

def get_comments():     #api to get comments any user has posted on a particular post
    id=int(request.vars["id"])
    comments=db(db.comm.post==id).select()
    my_data = {}
    dict={}
    i=0
    for comm in comments:
        if comm.post==id:
            my_data[i]=comm.body
            flag=comm.posted_by.id
            user=db.users(flag)
            my_data[i+1]=user.first_name
            #dict[i]=my_data
            l=[]
            l.append(comm.body)
            l.append(user.first_name)
            dict[i]=l
            i=i+1
    return dict

def get_user():  #api to get user form the primary key
    id=int(request.vars["id"])
    user=db.users(id)
    return dict(name=user.first_name,last_name=user.last_name,Entry_no=user.entry_no,Hostel=user.Hostel)
def add_complaint():  #api to add the complaint
    if auth.is_logged_in():
        #idm=int(request.vars["id"])
        user=db.users(auth.user.id)
        resolved=str(request.vars["resolved"]).strip()
        catagory=int(request.vars["catagoryy"])
        complaint_level=int(request.vars["complaint_level"])
        title=str(request.vars["title"]).strip()
        body=str(request.vars["body"]).strip()
        db.post.insert(
            Resolved=resolved,complaint_level=complaint_level,title=title,catagoryy=catagory,posted_by=auth.user.id,body=body)
        hostel=user.Hostel
        if complaint_level==1:
            users=db(db.users).select()
            for user in users:
                if(user.typee==10+catagory):
                    db.notifications.insert(user_id=user.id,typee=1,body=body,title=title,
                                       posted_by=auth.user.id)
                else:
                    db.notifications.insert(user_id=user.id,typee=0,body=body,title=title,
                                        posted_by=auth.user.id)
        if complaint_level==2:
            use=db(db.users).select()
            for user in use:
                if(user.typee==20+catagory and user.Hostel==hostel):
                    db.notifications.insert(user_id=user.id,typee=1,body=body,title=title,
                                        posted_by=auth.user.id)
                if(user.typee!=20+catagory and user.Hostel==hostel):
                    db.notifications.insert(user_id=user.id,typee=0,body=body,title=title,
                                        posted_by=auth.user.id)
        if complaint_level==3:
            users=db(db.users).select()
            for user in users:
                if user.typee==catagory:
                    db.notifications.insert(user_id=user.id,typee=1,body=body,title=title,
                                        posted_by=auth.user.id)
        return dict(success=True)

def comment_vote():  #api to comment on the vote
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

def up_downvote():  #api to vote the post
    if auth.is_logged_in():
        id = int(request.vars["id"])
        vote = int(request.vars["vote"])
        post=db.post(id)
        if post:
            post.update_record(votes=post.votes+vote)
            return dict(success=True,post=post)
    return dict(success=True)
@request.restful()
def post():  #api to get generic patterns using parsed json response
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
