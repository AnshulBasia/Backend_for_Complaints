@request.restful()
def get_post():
    def GET(id):
        post=db.post(id)
        return post.as_dict() if post else None
    return locals()
