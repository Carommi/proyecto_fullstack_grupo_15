from pydantic import BaseModel, ConfigDict, Field


class CursoIdioma(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    estudiante: str = Field(min_length=2, max_length=120)
    idioma_nivel: str = Field(min_length=2, max_length=80)
    valor_curso: float = Field(gt=0, allow_inf_nan=False)
    pagado: bool = False


class CursoIdiomaResponse(CursoIdioma):
    id: str
