from pydantic import BaseModel, ConfigDict, Field


class Estudiante(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=2, max_length=100)
    documento: str = Field(min_length=6, max_length=20)
    correo: str = Field(min_length=3, max_length=254)
    telefono: str = Field(min_length=5, max_length=10)


class EstudianteResponse(Estudiante):
    id: str


class CursoIdioma(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    estudiante: str = Field(min_length=2, max_length=120)
    estudiante_nombre: str = Field(min_length=2, max_length=100)
    idioma: str = Field(min_length=2, max_length=40)
    idioma_nivel: str = Field(min_length=2, max_length=80)
    valor_curso: float = Field(gt=0, allow_inf_nan=False)
    pagado: bool = False


class CursoIdiomaResponse(CursoIdioma):
    id: str


class EstadoPagoUpdate(BaseModel):
    pagado: bool
