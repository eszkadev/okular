from okular import db

class BuildFails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    build_id = db.Column(db.Integer, db.ForeignKey('builds.id'))
    test_name = db.Column(db.String(256), db.ForeignKey('tests.name'))

class Builds(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(7))
    name = db.Column(db.String(256))
    url = db.Column(db.String(1024))
    date = db.Column(db.DateTime)
    fails = db.relationship('Tests', secondary=BuildFails.__table__, back_populates='builds')

class Tests(db.Model):
    name = db.Column(db.String(256), primary_key = True)
    builds = db.relationship('Builds', secondary=BuildFails.__table__, back_populates='fails')
