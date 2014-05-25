from jsonpickle.pickler import Pickler
import django

def to_json(dj_object):
    
    if type(dj_object) == django.db.models.query.QuerySet:
        json_array = []
        for obj in dj_object:
            json_array.append(to_json(obj))
        return json_array

    foreign_key_fields = [field for field in dj_object._meta.fields if type(field) is django.db.models.ForeignKey]
    fk_array = []
    pickler = Pickler(unpicklable=False)
    json_dict = pickler.flatten(dj_object)
    for field in foreign_key_fields:
        obj = dj_object.__getattribute__(field.name)
        try:
            json_dict[field.name] = to_json(obj)
        except:
            pass

    return json_dict 


