from okular import dbcontext

class Settings(dbcontext.Model):
    name = dbcontext.Column(dbcontext.String(256), primary_key = True)
    value = dbcontext.Column(dbcontext.String(1024))

class BuildFails(dbcontext.Model):
    id = dbcontext.Column(dbcontext.Integer, primary_key=True)
    build_id = dbcontext.Column(dbcontext.Integer, dbcontext.ForeignKey('builds.id'))
    test_name = dbcontext.Column(dbcontext.String(256), dbcontext.ForeignKey('tests.name'))

class Builds(dbcontext.Model):
    id = dbcontext.Column(dbcontext.Integer, primary_key = True)
    status = dbcontext.Column(dbcontext.String(7))
    name = dbcontext.Column(dbcontext.String(256))
    url = dbcontext.Column(dbcontext.String(1024))
    date = dbcontext.Column(dbcontext.DateTime)
    fails = dbcontext.relationship('Tests', secondary=BuildFails.__table__, back_populates='builds')

class Tests(dbcontext.Model):
    name = dbcontext.Column(dbcontext.String(256), primary_key = True)
    builds = dbcontext.relationship('Builds', secondary=BuildFails.__table__, back_populates='fails')
