class Error:
    def __init__(self, _type, desc, at, w, loc, l):
        self.type = _type
        self.desc = desc
        self.at   = at
        self.w    = w
        self.loc  = loc
        self.l    = l
    
    def __repr__(self):
        return f"{self.l}: {self.loc}\n    {self.type}\n    This error happened at character {self.w} of line {self.l}, which caused by {self.at}."

class UnknownCharacter(Error):
    def __init__(self, desc, at, w, l, loc):
        super().__init__("UnknownCharacter", desc, at, w, loc, l)

class BackslashError(Error):
    def __init__(self, desc, at, w, l, loc):
        super().__init__("BackslashError",  desc, at, w, loc, l)

class TokenizerError(Error):
    def __init__(self, desc, at, w, l, loc):
        super().__init__("TokenizerError",  desc, at, w, loc, l)