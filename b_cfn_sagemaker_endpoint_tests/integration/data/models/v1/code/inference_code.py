def model_fn(model_dir):
    pass


def input_fn(serialized_input_data, content_type):
    return 'Everything\'s Gucci! <3'


def predict_fn(input_object, model):
    return input_object


def output_fn(prediction, accept):
    return {
        'message': prediction,
        'model_name': 'v1'
    }
