import os
import mongoengine as ming

os.environ["Database"] = "Mongo"
os.environ["Host"] = "mongodb+srv://OSP:osp_password@cluster0.17xqk.mongodb.net/Mongo?retryWrites=true&w=majority"

ming.connect(db=os.environ["Database"],host=os.environ["Host"])