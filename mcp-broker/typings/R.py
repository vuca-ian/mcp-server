from typing import Optional, TypeVar, Generic, Union
from pydantic import BaseModel
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
import json
T = TypeVar('T')

class R() :
   code: int
   message:str
   data :Optional[T]= None 
   def __init__(self, code: int, message:str, data: Optional[T] = None):
      self.code = code
      self.message = message
      self.data = data
   class Config:
      arbitrary_types_allowed = True


def ok(*, data: Union[T]) -> Response:
   return JSONResponse(status_code= 200, content= jsonable_encoder(R(code=200, message="OK", data=data)))