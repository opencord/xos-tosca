from resources import RESOURCES

class GRPCModelsAccessor:
    """
    This class provide the glue between the models managed by TOSCA and the ones living in xos-core
    """

    @staticmethod
    def get_model_from_classname(class_name, data):
        """
        Give a Model Class Name and some data, check if that exits or instantiate a new one
        """

        if class_name not in RESOURCES:
            raise Exception('[XOS-TOSCA] The model your tring to create (%s) is not know by xos-core' % class_name)

        cls = RESOURCES[class_name]
        if data.get('name'):
            used_key = 'name'
        else:
            used_key = data.keys()[0]

        models = cls.objects.filter(**{used_key: data[used_key]})

        if len(models) == 1:
            print "[XOS-Tosca] Model %s already exist, updating..." % data[used_key]
            model = models[0]
        elif len(models) == 0:
            model = cls.objects.new()
            print "[XOS-Tosca] Model %s is new, creating..." % data[used_key]
        else:
            raise Exception("[XOS-Tosca] Model %s has multiple instances, I can't handle it" % data[used_key])
        return model