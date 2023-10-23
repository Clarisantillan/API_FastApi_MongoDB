# uvicorn sistema_aut:app --reload
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app=FastAPI()

oauth2= OAuth2PasswordBearer(tokenUrl="login") #estandar de autenticacion

class User(BaseModel):#clase del usuario
   username:str 
   full_name: str
   email:str
   disabled:bool
   
class UserBD(User):#clase usuario_DB
    password: str
   
users_db ={
    "claridev":{
        "username":"claridev",
        "full_name": "Clara Santillan",
        "email":"clara.santillan.01@gmail.com",
        "disabled":False,
        "password":"123456"
    },
        "claridev2":{
        "username":"claridev2",
        "full_name": "Clara Santillan 2",
        "email":"clara.santillan2.01@gmail.com",
        "disabled":True,
        "password":"654321"
    }
}#usuarios de prueba

def search_user_db(username:str): #funcion buscador usuarios(incluyendo la contraseña)
    if username in users_db:
        return UserBD(**users_db[username])
    
def search_user(username:str):#funcion buscador datos de usuario
    if username in users_db:
        return User(**users_db[username])
    
async def current_user(token:str=Depends(oauth2)):#funcion para igualar el usuario a uno en la db y dar acceso en caso exitoso
    user= search_user(token)
    if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticacion invalidas", 
            headers={"WWW-Authenticate": "Bearer"}
        )
    if user.disabled:
           raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario Inactivo", 
        )
    return user
    
@app.post("/login")#funcion de login con retorno de access token 
async def login(form:OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es correcto"
        )
        
    user= search_user_db(form.username)
    
    if not form.password == user.password:
         raise HTTPException(
            status_code=400, detail="La contraseña no es correcta"
        )
    return {"access_token": user.username, "token_type": "bearer"}
        

@app.get("/users/me") #funcion para mostrar al usuario sus datos
async def me(user:User = Depends(current_user)):
    return user