# udec

## how to use:

```
@Ulogger(ltype='excexe', re_raise=True)
def test():
    pass
```
or in a class:
```
class Test: 
    def __init__(self):
        self.logger = logger # if the class/instance has an attribute named "logger", it will be used instead
    
    @Ulogger(ltype='excexe', re_raise=True)
    def test(self):
        pass
```
