from app.utils.encryption import encrypt,decrypt,generate_master_key,generate_key
from app.utils.queries import DataBind,DataInteger,Queriable,Query
class Foo(Queriable):
    test=DataInteger()
class Boo():
    pass
foo=Foo()
foo.setValues(test=2)
boo=Boo()
print(Query(obj=Foo).select(foo).build([("=","AND")]))
print(str(list("ciao"))[1:-1])