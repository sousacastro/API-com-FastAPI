from fastapi import FastAPI, HTTPException, Depends
from fastapi_pagination import Page, paginate, add_pagination
from fastapi_pagination.params import Params
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from database import get_db
from models import Atleta  # Supondo que o modelo Atleta já esteja definido

app = FastAPI()

class AtletaCreate(BaseModel):
    nome: str
    cpf: str
    centro_treinamento: str
    categoria: str

class AtletaResponse(BaseModel):
    nome: str
    centro_treinamento: str
    categoria: str

@app.get("/atletas", response_model=Page[AtletaResponse])
def get_atletas(nome: str = None, cpf: str = None, params: Params = Depends(), db: Session = Depends(get_db)):
    query = db.query(Atleta)
    
    if nome:
        query = query.filter(Atleta.nome.contains(nome))
    if cpf:
        query = query.filter(Atleta.cpf == cpf)
    
    atletas = query.all()
    return paginate(atletas, params)

@app.post("/atletas")
def create_atleta(atleta: AtletaCreate, db: Session = Depends(get_db)):
    new_atleta = Atleta(
        nome=atleta.nome,
        cpf=atleta.cpf,
        centro_treinamento=atleta.centro_treinamento,
        categoria=atleta.categoria
    )
    db.add(new_atleta)
    try:
        db.commit()
        db.refresh(new_atleta)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=303, detail=f"Já existe um atleta cadastrado com o cpf: {atleta.cpf}")
    
    return new_atleta

add_pagination(app)
