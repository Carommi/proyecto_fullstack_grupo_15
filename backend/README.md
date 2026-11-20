# Global Speak

API asíncrona para administrar matrículas de cursos de idiomas con FastAPI,
Pydantic y MongoDB. La colección utilizada es `matriculas` dentro de la base
de datos `global_speak`.

## Preparación en Windows (PowerShell)

1. Asegúrate de tener Python 3.10 o posterior y una instancia de MongoDB local
   activa, o una URI de MongoDB Atlas.
2. Desde la raíz del proyecto, prepara e inicia la API:

   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python -m uvicorn main:app --reload
   ```

   La configuración predeterminada usa MongoDB en
   `mongodb://localhost:27017` y la base de datos `global_speak`. Para usar
   MongoDB Atlas u otra instancia, define `MONGODB_URL` y, opcionalmente,
   `DATABASE_NAME` en `backend/.env`. No compartas ni subas credenciales. Al
   iniciar, la API verifica que MongoDB responda.

3. En una segunda terminal sirve el frontend:

   ```powershell
   cd Frontend
   py -m http.server 5500
   ```

4. Abre <http://127.0.0.1:5500> en el navegador. El frontend ya está
   configurado para usar la API en `http://127.0.0.1:8000`; las operaciones
   se guardan en MongoDB y no en el almacenamiento local del navegador.

## Pruebas en Swagger

Abre <http://127.0.0.1:8000/docs>. Crea una matrícula con `POST /matriculas`:

```json
{
  "estudiante": "<id del estudiante>",
  "estudiante_nombre": "Ana Pérez",
  "idioma": "Inglés",
  "idioma_nivel": "B1 - Intermedio",
  "valor_curso": 450000,
  "pagado": false
}
```

Primero crea un estudiante con `POST /estudiantes` y usa el `id` de la
respuesta como `estudiante`. La interfaz también permite crear, consultar,
actualizar y eliminar estudiantes, además de crear y consultar matrículas,
registrar pagos y eliminar matrículas.

## Modelo y rutas

`Estudiante` valida los datos del directorio. `CursoIdioma` valida el
estudiante, el idioma, el nivel, el valor positivo del curso y el estado del
pago. `pagado` es `false` si se omite.

| Método | Ruta | Acción |
| --- | --- | --- |
| `POST` | `/estudiantes` | Crear un estudiante |
| `GET` | `/estudiantes` | Listar estudiantes |
| `PUT` | `/estudiantes/{estudiante_id}` | Actualizar un estudiante |
| `DELETE` | `/estudiantes/{estudiante_id}` | Eliminar un estudiante |
| `POST` | `/matriculas` | Crear una matrícula |
| `GET` | `/matriculas` | Listar matrículas |
| `GET` | `/matriculas/{matricula_id}` | Consultar una matrícula |
| `PUT` | `/matriculas/{matricula_id}` | Reemplazar los datos de una matrícula |
| `PATCH` | `/matriculas/{matricula_id}` | Actualizar su estado de pago |
| `DELETE` | `/matriculas/{matricula_id}` | Eliminar una matrícula |
