class Router(object):
    def get_db(self, model):
        if model._meta.app_label == "geodata":
            return "arcgis"
        # if model._meta.app_label == "login"
        #    return "concrete5"
        return None
    
    def db_for_write(self, model, **hints):
        return self.get_db(model)
    
    def db_for_read(self, model, **hints):
        return self.get_db(model)
