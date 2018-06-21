class Assertion():

    def __init__(self, response):
        self.res = response
    
    def status_code_equal(self):
        if self.res.status_code == 200:
            return True
        else:
            return False

    def custom_assert(self, fname, *args, **kwargs):
        try:
            result = fname()
        except Exception, e:
            pass
