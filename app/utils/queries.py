
from time import time,strftime,localtime
from copy import deepcopy
from typing import Literal
class DataBind():
    def __init__(self,unique:bool=False,key:bool=False,external_key:bool=False,required:bool=False):
        self.value=None
        self.key=key
        self.unique=unique
        self.external_key=external_key
        self.required=required
    def getValue(self)->any:
        return self.value
    def setValue(self,value:any):
        self.value=value
    def SQLType(self)->str:
        return f"VARCHAR {'NOT NULL' if self.required else ''} {'UNIQUE' if self.unique else ''} {'PRIMARY KEY' if self.key else ''}"
    def copy(self):
        return deepcopy(self)
    def __eq__(self, value: object) -> bool:
        value.__eq__(self.value)
    def __gt__(self, value: object) -> bool:
        value.__gt__(self.value)
    def __lt__(self, value: object) -> bool:
        value.__lt__(self.value)
        
class DataInteger(DataBind):
    Test_Variable:DataBind=0
    def __init__(self,unique:bool=False,key:bool=False,external_key:bool=False,required:bool=False):
        self.value=None
        self.key=key
        self.unique=unique
        self.external_key=external_key
        self.required=required
    def getValue(self)->int:
        return self.value
    def setValue(self,value:int):
        self.value=value
    def SQLType(self)->str:
        return f"INTEGER {'NOT NULL' if self.required else ''} {'UNIQUE' if self.unique else ''} {'PRIMARY KEY' if self.key else ''}"
        
class DataString(DataBind):
    def __init__(self,maxchar:int=255,unique:bool=False,key:bool=False,external_key:bool=False,required:bool=False):
        self.value=None
        self.maxchar=maxchar
        self.key=key
        self.unique=unique
        self.external_key=external_key
        self.required=required
    def getValue(self)->str:
        return self.value
    def setValue(self,value:str):
        self.value=value
    def SQLType(self)->str:
        return f"VARCHAR({self.maxchar}) {'NOT NULL' if self.required else ''} {'UNIQUE' if self.unique else ''} {'PRIMARY KEY' if self.key else ''}"
class DataBool(DataBind):
    def __init__(self, unique: bool = False, key: bool = False, external_key: bool = False,required:bool=False):
        super().__init__(False, False, False,required)
    def getValue(self) -> bool:
        return super().getValue()
    def setValue(self, value: bool):
        return super().setValue(value)
    def SQLType(self)->str:
        return "BOOLEAN"
    
class DataFloat(DataBind):
    def __init__(self, unique: bool = False, key: bool = False, external_key: bool = False,required:bool=False):
        super().__init__( unique, key, external_key,required)
    def getValue(self) -> float:
        return super().getValue()
    def setValue(self, value: float):
        return super().setValue(value)
    def SQLType(self)->str:
        return f"DECIMAL(2) {'NOT NULL' if self.required else ''} {'UNIQUE' if self.unique else ''} {'PRIMARY KEY' if self.key else ''}"
    
class DataList(DataBind):
    def __init__(self, unique: bool = False, key: bool = False, external_key: bool = False,max_length:int=999,min_length:int=0,required:bool=False):
        super().__init__(unique, key, external_key,required)
        self.max_length=max_length
        self.min_length=min_length
    def getValue(self) -> list[str]:
        return super().getValue()
    def setValue(self, value: list[str]):
        return super().setValue(value)
    def SQLType(self)->str:
        return "VARCHAR[]"
    
class DataDateTime(DataBind):
    def __init__(self, unique: bool = False, key: bool = False, external_key: bool = False,required:bool=False,autogenerated:bool=False):
        super().__init__(unique, key, external_key,required)
        self.autogenerated=autogenerated
        if autogenerated:
            self.value=time()
    def SQLType(self)->str:
        return "VARCHAR"
    def toHumanReadable(self)->str:
        return strftime(r"%Y-%m-%d %H:%M:%S",localtime(self.value))
    def getValue(self) -> float:
        return super().getValue()
    def setValue(self, value: float):
        return super().setValue(value)
    def SQLType(self)->str:
        return "INTERVAL"
    

def _managed_property(name:str):
    prop_name = "_"+name.lower()
    
    @property
    def prop(self):
        return getattr(self,prop_name).getValue()
    @prop.setter
    def prop(self,value):
        try:
            getattr(self,prop_name).setValue(value)
            print(getattr(self,prop_name).getValue())
        except AttributeError:
            setattr(self,prop_name,value.copy())

    return prop

class Queriable():
    def __init__(self) -> None:
        annotations = self.__class__.__dict__
        self.schema:dict[str,type] = dict()
        for k,v in annotations.items():
            if issubclass(v.__class__,DataBind):
                self.schema[k]=v 
        for  k,v in self.schema.items():
            setattr(self,k,v.copy())
            
    def getValues(self)->dict[str,any]:
        ret_values=dict()
        for key in self.schema.keys():
            val=getattr(self,key).getValue()
            if val:
                ret_values[key]=val
        return ret_values
    
    def setValues(self,**args):
        done=True
        val_generator = ((k,args[k]) for k in self.schema.keys())
        while done:
            try:
                for k,v in val_generator:
                    getattr(self,k).setValue(v)
                done=False
            except KeyError:
                continue
class Query():
    COMMANDS=Literal["SELECT * FROM","DELETE FROM","INSERT INTO","UPDATE"]
    OPERATORS=Literal["LIKE","BETWEEN","IN","=","<",">","<=",">="]
    LOGIC_OPERATORS=Literal["AND","OR","NOT"]
    def __init__(self,obj:type):
        if not issubclass(obj,Queriable):
            raise TypeError
        self.command:Query.COMMANDS=""
        self.where_clause:dict[str,any]=dict()
        self.obj_type=obj
        self.schema =  self.obj_type().schema.copy()
        self.query=f"SHOW TABLE {self.obj_type.__name__}"

    def select(self,obj:Queriable)->'Query':
        if not isinstance(obj,self.obj_type):
            raise TypeError
        self.command="SELECT * FROM"
        self.where_clause=obj.getValues()
        return self
    def delete(self,obj:Queriable)->'Query':
        if not isinstance(obj,self.obj_type):
            raise TypeError
        self.command="DELETE FROM"
        self.where_clause=obj.getValues()
        return self
    def update(self,obj:Queriable)->'Query':
        if not isinstance(obj,self.obj_type):
            raise TypeError
        self.command="UPDATE"
        self.where_clause=obj.getValues()
        return self
    def insert(self,obj:Queriable)->'Query':
        if not isinstance(obj,self.obj_type):
            raise TypeError
        self.command="INSERT INTO"
        self.where_clause=obj.getValues()
        return self
    def build(self,operators:list[tuple[OPERATORS,LOGIC_OPERATORS]]|None=None)->'Query':
        query=f"{self.command} {self.obj_type.__name__}"
        if self.command == "INSERT INTO":
            query=query + " ("
            val_string="("
            for k,v in self.where_clause.items():
                val_string=val_string+str(v)+", "
                query=query + k +", "
            val_string=val_string[:-2]+")"
            query=query[:-2]+") VALUES "+val_string
            self.query=query
        else:
            if not operators or not self.where_clause:
                return self
            query=query+" WHERE"
            last_l_op=""
            try:
                i=0
                for k,v in self.where_clause.items():
                    op,l_op=operators[i]
                    last_l_op=l_op
                    query=query+f" {k} {op} {v} {l_op}"
                    i+=1
            except IndexError:
                if i<1:
                    return self
            finally:
                query=query[:-len(last_l_op)] +";"
                self.query=query
        return self
    def __repr__(self) -> str:
        return self.query
        