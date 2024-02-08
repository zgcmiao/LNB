class Error(Exception):
    def __init__(self, msg: str, detail=None):
        super().__init__("%s: %s" % (msg, detail) if detail else msg)
        self.msg = msg
        self.detail = detail
