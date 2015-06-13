def spy():
    def spy_function(*args, **kwargs):
        spy_function.was_called = True

    spy_function.was_called = False
    return spy_function
