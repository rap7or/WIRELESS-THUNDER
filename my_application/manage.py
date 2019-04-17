from my_application.web_project import app, db
from my_application.models.users import User


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User)
