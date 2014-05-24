from django.utils.translation import ugettext as _
import jsonpickle
from django.http import HttpResponseRedirect, HttpResponse

#error message factory functions

def error_for_user_exists(user_id):
    error = ErrorMessage()
    error.message = "User %s already exists." % user_id
    error.error_code = "ErrorUserAlreadyExists"
    return error

def error_for_database_exists(database_name):
    error = ErrorMessage()
    error.message = _("Database with name '%(db_name)' already exists. Please enter another name.") % {'db_name' : database_name}
    error.error_code = "ErrorDatabaseAlreadyExists"



class BaseException(Exception):

    def http_response(self):
        json_string = jsonpickle.encode(self, unpicklable=False)
        return HttpResponse(content=json_string, mimetype="application/json")

class ErrorMessage(BaseException):
    def __init__(self, message = "", error_code = ""):
        self.message = message
        self.error_code = error_code

class KartenUserAlreadyExists(BaseException):
    def __init__(self, external_id):
        self.message = _("There is already a user with those credentials") 
        self.error_code = "ErrorKartenUserAlreadyExists"

class KartenUserDoesNotExist(BaseException):
    def __init__(self, user_id):
        self.user_id = user_id

class KartenCouchDBException(BaseException):
    def __init__(self, message="", error_code="", database=""):
        self.message = message
        self.error_code = error_code
        self.database = database

