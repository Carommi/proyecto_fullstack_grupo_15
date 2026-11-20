from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from bson import ObjectId
from decouple import config
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from database import client, estudiantes_collection, matriculas_collection
from models import (
    CursoIdioma,
    CursoIdiomaResponse,
    EstadoPagoUpdate,
    Estudiante,
    EstudianteResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        await client.admin.command("ping")
        yield
    finally:
        client.close()


app = FastAPI(
    title="Global Speak",
    description="API para gestionar matrículas de cursos de idiomas.",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in config(
        "ALLOWED_ORIGINS",
        default=(
            "http://localhost:3000,http://localhost:5173,"
            "http://localhost:5500,http://127.0.0.1:5500"
        ),
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_matricula_id(matricula_id: str) -> ObjectId:
    if not ObjectId.is_valid(matricula_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El identificador de matrícula no es válido.",
        )
    return ObjectId(matricula_id)


def serialize_matricula(document: dict) -> CursoIdiomaResponse:
    return CursoIdiomaResponse(
        id=str(document["_id"]),
        estudiante=document["estudiante"],
        estudiante_nombre=document.get("estudiante_nombre", document["estudiante"]),
        idioma=document.get("idioma", "No especificado"),
        idioma_nivel=document["idioma_nivel"],
        valor_curso=document["valor_curso"],
        pagado=document["pagado"],
    )


def parse_estudiante_id(estudiante_id: str) -> ObjectId:
    if not ObjectId.is_valid(estudiante_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El identificador de estudiante no es válido.",
        )
    return ObjectId(estudiante_id)


def serialize_estudiante(document: dict) -> EstudianteResponse:
    return EstudianteResponse(
        id=str(document["_id"]),
        nombre=document["nombre"],
        documento=document["documento"],
        correo=document["correo"],
        telefono=document["telefono"],
    )


async def preparar_matricula(matricula: CursoIdioma) -> dict:
    document = matricula.model_dump()
    estudiante_id = parse_estudiante_id(matricula.estudiante)
    estudiante = await estudiantes_collection.find_one({"_id": estudiante_id})
    if estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el estudiante seleccionado.",
        )
    document["estudiante_nombre"] = estudiante["nombre"]
    return document


async def find_matricula(matricula_id: str) -> dict:
    object_id = parse_matricula_id(matricula_id)
    document = await matriculas_collection.find_one({"_id": object_id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la matrícula.",
        )
    return document


@app.get("/", tags=["General"])
async def inicio() -> dict[str, str]:
    return {"servicio": "Global Speak", "documentacion": "/docs"}


@app.post(
    "/estudiantes",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Estudiantes"],
)
async def crear_estudiante(estudiante: Estudiante) -> EstudianteResponse:
    document = estudiante.model_dump()
    result = await estudiantes_collection.insert_one(document)
    document["_id"] = result.inserted_id
    return serialize_estudiante(document)


@app.get(
    "/estudiantes",
    response_model=list[EstudianteResponse],
    tags=["Estudiantes"],
)
async def listar_estudiantes() -> list[EstudianteResponse]:
    documents = await estudiantes_collection.find().to_list(length=None)
    return [serialize_estudiante(document) for document in documents]


@app.put(
    "/estudiantes/{estudiante_id}",
    response_model=EstudianteResponse,
    tags=["Estudiantes"],
)
async def actualizar_estudiante(
    estudiante_id: str,
    estudiante: Estudiante,
) -> EstudianteResponse:
    object_id = parse_estudiante_id(estudiante_id)
    document = estudiante.model_dump()
    result = await estudiantes_collection.update_one(
        {"_id": object_id},
        {"$set": document},
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el estudiante.",
        )
    return serialize_estudiante({"_id": object_id, **document})


@app.delete(
    "/estudiantes/{estudiante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Estudiantes"],
)
async def eliminar_estudiante(estudiante_id: str) -> Response:
    object_id = parse_estudiante_id(estudiante_id)
    result = await estudiantes_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el estudiante.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/matriculas",
    response_model=CursoIdiomaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Matrículas"],
)
async def crear_matricula(matricula: CursoIdioma) -> CursoIdiomaResponse:
    document = await preparar_matricula(matricula)
    result = await matriculas_collection.insert_one(document)
    document["_id"] = result.inserted_id
    return serialize_matricula(document)


@app.get(
    "/matriculas",
    response_model=list[CursoIdiomaResponse],
    tags=["Matrículas"],
)
async def listar_matriculas() -> list[CursoIdiomaResponse]:
    documents = await matriculas_collection.find().to_list(length=None)
    return [serialize_matricula(document) for document in documents]


@app.get(
    "/matriculas/{matricula_id}",
    response_model=CursoIdiomaResponse,
    tags=["Matrículas"],
)
async def obtener_matricula(matricula_id: str) -> CursoIdiomaResponse:
    document = await find_matricula(matricula_id)
    return serialize_matricula(document)


@app.put(
    "/matriculas/{matricula_id}",
    response_model=CursoIdiomaResponse,
    tags=["Matrículas"],
)
async def actualizar_matricula(
    matricula_id: str,
    matricula: CursoIdioma,
) -> CursoIdiomaResponse:
    object_id = parse_matricula_id(matricula_id)
    document = await preparar_matricula(matricula)
    result = await matriculas_collection.update_one(
        {"_id": object_id},
        {"$set": document},
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la matrícula.",
        )
    updated_document = {"_id": object_id, **document}
    return serialize_matricula(updated_document)


@app.patch(
    "/matriculas/{matricula_id}",
    response_model=CursoIdiomaResponse,
    tags=["Matrículas"],
)
async def actualizar_estado_pago(
    matricula_id: str,
    estado_pago: EstadoPagoUpdate,
) -> CursoIdiomaResponse:
    object_id = parse_matricula_id(matricula_id)
    result = await matriculas_collection.update_one(
        {"_id": object_id},
        {"$set": estado_pago.model_dump()},
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la matrícula.",
        )
    document = await matriculas_collection.find_one({"_id": object_id})
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la matrícula después de actualizarla.",
        )
    return serialize_matricula(document)


@app.delete(
    "/matriculas/{matricula_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Matrículas"],
)
async def eliminar_matricula(matricula_id: str) -> Response:
    object_id = parse_matricula_id(matricula_id)
    result = await matriculas_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la matrícula.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
