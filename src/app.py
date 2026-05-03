"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from src import models, database, schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=database.engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    try:
        db.execute(text("SELECT 1"))
        active_nodes = db.query(models.Node).filter(models.Node.status == "active").count()
        return {"status": "ok", "db": "connected", "nodes_count": active_nodes}
    except Exception:
        return {"status": "error", "db": "disconnected", "nodes_count": 0}

@app.post("/api/nodes", response_model=schemas.NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(node: schemas.NodeCreate, db: Session = Depends(database.get_db)):
    if db.query(models.Node).filter(models.Node.name == node.name).first():
        raise HTTPException(status_code=409, detail="Node with this name already exists")
    db_node = models.Node(name=node.name, host=node.host, port=node.port)
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

@app.get("/api/nodes", response_model=list[schemas.NodeResponse])
def list_nodes(db: Session = Depends(database.get_db)):
    return db.query(models.Node).all()

@app.get("/api/nodes/{name}", response_model=schemas.NodeResponse)
def get_node(name: str, db: Session = Depends(database.get_db)):
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@app.put("/api/nodes/{name}", response_model=schemas.NodeResponse)
def update_node(name: str, node_update: schemas.NodeUpdate, db: Session = Depends(database.get_db)):
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if node_update.host is not None:
        node.host = node_update.host
    if node_update.port is not None:
        node.port = node_update.port
    db.commit()
    db.refresh(node)
    return node

@app.delete("/api/nodes/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(name: str, db: Session = Depends(database.get_db)):
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = "inactive"
    db.commit()
