# Global Speak

API asíncrona para administrar matrículas de cursos de idiomas con FastAPI,
Pydantic y MongoDB. La colección utilizada es `matriculas` dentro de la base
de datos `global_speak`.

## Preparación en Windows (PowerShell)

1. Asegúrate de tener Python 3.10 o posterior y una instancia de MongoDB local
   activa, o una URI de MongoDB Atlas.
2. Desde la raíz del proyecto crea y activa un entorno virtual:

   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Copia la configuración de ejemplo y, si usas Atlas, reemplaza la URI por la
   tuya. No compartas ni subas credenciales:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Instala las dependencias e inicia el servidor:

   ```powershell
   python -m pip install -r requirements.txt
   python -m uvicorn main:app --reload
   ```

   Al iniciar, la API verifica que MongoDB responda. Si no está disponible,
   inicia primero MongoDB o corrige `MONGODB_URL` en `.env`.

## Pruebas en Swagger

Abre <http://127.0.0.1:8000/docs>. Crea una matrícula con `POST /matriculas`:

```json
{
  "estudiante": "Ana Pérez",
  "idioma_nivel": "Inglés B1",
  "valor_curso": 250.0,
  "pagado": false
}
```

Prueba luego la consulta general `GET /matriculas`, la consulta por ID,
la actualización completa con `PUT /matriculas/{matricula_id}` y la
eliminación con `DELETE /matriculas/{matricula_id}`. El identificador devuelto
por la creación se utiliza en las operaciones por matrícula.

## Modelo y rutas

`CursoIdioma` valida `estudiante`, `idioma_nivel`, `valor_curso` y `pagado`.
El importe debe ser positivo y `pagado` es `false` si se omite.

| Método | Ruta | Acción |
| --- | --- | --- |
| `POST` | `/matriculas` | Crear una matrícula |
| `GET` | `/matriculas` | Listar matrículas |
| `GET` | `/matriculas/{matricula_id}` | Consultar una matrícula |
| `PUT` | `/matriculas/{matricula_id}` | Reemplazar sus datos |
| `DELETE` | `/matriculas/{matricula_id}` | Eliminar una matrícula |
