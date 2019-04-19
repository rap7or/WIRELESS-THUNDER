from flask_login import UserMixin
from datetime import datetime
from my_application.models import db


class Video(UserMixin, db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_title = db.Column(db.String(255), index=True, unique=False, nullable=False)
    video_loc = db.Column(db.String(255), index=True, unique=True, nullable=False)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, user, video_title, video_loc):
        self.user_id = user.id
        self.video_title = video_title
        self.video_loc = video_loc
        self.upload_time = datetime.now()

    def __repr__(self):
        return "<User '{}' : Video '{}'>".format(self.user_id, self.video_title)
