def pass_filter(filter, model):
    #if not type(model) == dict:
    #    model = {k[1:]: v for k, v in model.__dict__.items() if k.startswith('_') and k != '_map'}
    #    print '***', model
    for key, value in filter.items():
        if type(value) == int or type(value) == str:
            if model[key] != value:
                return False
        else:
            for op, val in value.items():
                if op == '$gt':
                    if model[key] <= val:
                        return False
                elif op == '$lt':
                    if model[key] > val:
                        return False
    return True