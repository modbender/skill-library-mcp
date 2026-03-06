# Reglas Python

Aplica a archivos con extensión: .py

---

## 🔴 BLOCKERS

### Inyección SQL
- NUNCA concatenar o interpolar variables en queries SQL
- NUNCA usar f-strings o .format() para construir queries

❌ Mal:
  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
  cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)
  cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")

✅ Bien:
  cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
  cursor.execute("SELECT * FROM users WHERE id = :id", {"id": user_id})

  # Con SQLAlchemy:
  session.query(User).filter(User.id == user_id).first()

### Inyección de Comandos
- NUNCA usar os.system() con input del usuario
- NUNCA usar shell=True en subprocess con input del usuario

❌ Mal:
  os.system(f"ping {host}")
  subprocess.run(f"ls {directory}", shell=True)
  subprocess.call("cat " + filename, shell=True)

✅ Bien:
  subprocess.run(["ping", "-c", "4", host], shell=False)
  subprocess.run(["ls", directory], shell=False)
  # Mejor aún: usar funciones nativas de Python
  files = os.listdir(directory)

### Deserialización Insegura
- NUNCA usar pickle.loads() con datos no confiables
- NUNCA usar yaml.load() sin Loader seguro
- NUNCA usar eval() o exec() con input del usuario

❌ Mal:
  data = pickle.loads(request.data)
  config = yaml.load(file_content)
  result = eval(user_input)
  exec(user_code)

✅ Bien:
  data = json.loads(request.data)
  config = yaml.safe_load(file_content)
  # Para eval: usar ast.literal_eval solo para literales simples
  result = ast.literal_eval(user_input)  # Solo acepta literales, no código

### Manejo de Archivos Inseguro
- Path traversal: no validar rutas de archivos del usuario
- No cerrar archivos abiertos (no usar context managers)

❌ Mal:
  filepath = "/uploads/" + request.args.get("file")
  f = open(filepath, "r")
  content = f.read()

✅ Bien:
  from pathlib import Path

  base_dir = Path("/uploads").resolve()
  requested = (base_dir / request.args.get("file")).resolve()

  if not str(requested).startswith(str(base_dir)):
      raise ValueError("Path traversal detected")

  with open(requested, "r") as f:
      content = f.read()

### Secrets Hardcodeados
- Contraseñas, API keys, tokens en el código fuente
- Strings de conexión a base de datos con credenciales embebidas

❌ Mal:
  DB_PASSWORD = "super_secret_123"
  API_KEY = "sk-abc123def456ghi789"
  conn = psycopg2.connect("postgresql://admin:password@localhost/mydb")

✅ Bien:
  import os
  from dotenv import load_dotenv

  load_dotenv()

  DB_PASSWORD = os.environ["DB_PASSWORD"]
  API_KEY = os.environ["API_KEY"]
  conn = psycopg2.connect(os.environ["DATABASE_URL"])

---

## 🟡 WARNINGS

### Excepciones
- NUNCA usar bare except o except Exception sin re-raise
- NUNCA silenciar excepciones con pass
- Capturar excepciones demasiado amplias cuando se conoce el error específico

❌ Mal:
  try:
      do_something()
  except:
      pass

  try:
      value = int(user_input)
  except Exception:
      value = 0

✅ Bien:
  try:
      do_something()
  except SpecificError as e:
      logger.error("Operation failed: %s", e)
      raise

  try:
      value = int(user_input)
  except (ValueError, TypeError) as e:
      logger.warning("Invalid input: %s", e)
      value = 0

### Mutable Default Arguments
- NUNCA usar objetos mutables como argumentos por defecto

❌ Mal:
  def add_item(item, items=[]):
      items.append(item)
      return items
  # Cada llamada comparte la misma lista!

  def create_config(options={}):
      options["timestamp"] = time.time()
      return options

✅ Bien:
  def add_item(item, items=None):
      if items is None:
          items = []
      items.append(item)
      return items

  def create_config(options=None):
      if options is None:
          options = {}
      options["timestamp"] = time.time()
      return options

### Type Hints
- Funciones públicas sin type hints en parámetros y return
- Usar Any cuando se puede ser más específico
- No usar Optional[X] o X | None para valores que pueden ser None

❌ Mal:
  def get_user(id):
      ...

  def process_data(data):
      ...

✅ Bien:
  def get_user(user_id: int) -> User | None:
      ...

  def process_data(data: list[dict[str, Any]]) -> ProcessResult:
      ...

### Context Managers
- No usar with para archivos, conexiones, locks, transacciones
- Recursos que se abren pero pueden no cerrarse si hay excepción

❌ Mal:
  f = open("data.txt", "r")
  content = f.read()
  f.close()  # No se ejecuta si hay excepción antes

  conn = psycopg2.connect(dsn)
  cursor = conn.cursor()
  cursor.execute(query)
  conn.close()

✅ Bien:
  with open("data.txt", "r") as f:
      content = f.read()

  with psycopg2.connect(dsn) as conn:
      with conn.cursor() as cursor:
          cursor.execute(query)

### Global State
- Uso excesivo de variables globales
- Modificar estado global desde funciones sin que sea obvio
- Usar global keyword dentro de funciones

❌ Mal:
  counter = 0

  def increment():
      global counter
      counter += 1

✅ Bien:
  class Counter:
      def __init__(self):
          self._count = 0

      def increment(self) -> int:
          self._count += 1
          return self._count

### Logging
- Usar print() en lugar de logging en código de producción
- No configurar niveles de log adecuados
- Logear datos sensibles
- Usar string formatting en lugar de lazy formatting en logging

❌ Mal:
  print(f"User {user_id} logged in")
  logger.info(f"Processing request for {user_id}")  # f-string se evalúa siempre

✅ Bien:
  logger.info("User %s logged in", user_id)  # Lazy: solo se formatea si el nivel está activo
  logger.error("Failed to process request", extra={"user_id": user_id})

---

## 🔵 SUGGESTIONS

### Pythonic Code
- Usar list/dict/set comprehensions en lugar de loops para transformaciones simples
- Usar enumerate() en lugar de range(len()) para iterar con índice
- Usar zip() para iterar múltiples listas en paralelo
- Usar any() y all() para verificaciones en colecciones
- Usar unpacking en lugar de acceso por índice

❌ Antes:
  result = []
  for item in items:
      if item.active:
          result.append(item.name)

  for i in range(len(users)):
      print(users[i])

  found = False
  for item in items:
      if item.valid:
          found = True
          break

✅ Después:
  result = [item.name for item in items if item.active]

  for i, user in enumerate(users):
      print(user)

  found = any(item.valid for item in items)

### Pathlib sobre os.path
- Preferir pathlib.Path sobre os.path para manipulación de rutas

❌ Antes:
  import os
  filepath = os.path.join(base_dir, "data", filename)
  if os.path.exists(filepath):
      with open(filepath) as f:
          content = f.read()
  name, ext = os.path.splitext(filename)

✅ Después:
  from pathlib import Path
  filepath = Path(base_dir) / "data" / filename
  if filepath.exists():
      content = filepath.read_text()
  name = filepath.stem
  ext = filepath.suffix

### Dataclasses y Pydantic
- Usar dataclasses o Pydantic models en lugar de dicts para datos estructurados
- Usar frozen=True para objetos inmutables

❌ Antes:
  user = {
      "name": "John",
      "email": "john@example.com",
      "age": 30
  }
  # No hay validación, no hay autocompletado, fácil de escribir mal una key

✅ Después (dataclass):
  from dataclasses import dataclass

  @dataclass(frozen=True)
  class User:
      name: str
      email: str
      age: int

  user = User(name="John", email="john@example.com", age=30)

✅ Después (Pydantic para validación):
  from pydantic import BaseModel, EmailStr

  class User(BaseModel):
      name: str
      email: EmailStr
      age: int = Field(ge=0, le=150)

  user = User(name="John", email="john@example.com", age=30)

### Async (FastAPI, asyncio)
- Usar async/await para operaciones I/O bound
- No mezclar código sync y async sin usar run_in_executor
- Usar asyncio.gather() para operaciones concurrentes

❌ Mal (bloquea el event loop):
  @app.get("/users/{user_id}")
  async def get_user(user_id: int):
      user = requests.get(f"http://api/users/{user_id}")  # Bloquea!
      return user.json()

✅ Bien:
  @app.get("/users/{user_id}")
  async def get_user(user_id: int):
      async with httpx.AsyncClient() as client:
          response = await client.get(f"http://api/users/{user_id}")
      return response.json()

### Testing
- Usar pytest como framework de testing
- Usar fixtures para setup y teardown
- Usar parametrize para testear múltiples inputs
- Mockear dependencias externas con unittest.mock o pytest-mock
- Organizar tests siguiendo la estructura del proyecto

✅ Ejemplo de buen test:
  import pytest
  from unittest.mock import AsyncMock

  @pytest.fixture
  def user_service(mock_db):
      return UserService(db=mock_db)

  @pytest.mark.parametrize("user_id,expected", [
      (1, "John"),
      (2, "Jane"),
      (999, None),
  ])
  async def test_get_user(user_service, user_id, expected):
      result = await user_service.get_user(user_id)
      if expected is None:
          assert result is None
      else:
          assert result.name == expected

---

## 💡 NITS

### Estilo (PEP 8)
- Usar snake_case para funciones, métodos y variables
- Usar PascalCase para clases
- Usar UPPER_SNAKE_CASE para constantes a nivel de módulo
- Máximo 79 caracteres por línea (o 99-120 si el equipo lo acuerda)
- Dos líneas en blanco antes de funciones y clases a nivel de módulo
- Una línea en blanco antes de métodos dentro de una clase
- Imports ordenados: stdlib, third-party, local (usar isort)
- No usar backslash para continuación de línea cuando se pueden usar paréntesis

### Docstrings
- Funciones públicas deben tener docstring
- Usar formato consistente: Google style, NumPy style o reStructuredText
- Documentar parámetros, return y excepciones que se pueden lanzar

✅ Ejemplo (Google style):
  def calculate_discount(price: float, percentage: float) -> float:
      """Calcula el precio con descuento aplicado.

      Args:
          price: Precio original del producto.
          percentage: Porcentaje de descuento (0-100).

      Returns:
          Precio final después de aplicar el descuento.

      Raises:
          ValueError: Si el porcentaje no está entre 0 y 100.
      """
      if not 0 <= percentage <= 100:
          raise ValueError(f"Percentage must be between 0 and 100, got {percentage}")
      return price * (1 - percentage / 100)

### F-strings
- Preferir f-strings sobre .format() y % para string formatting (excepto en logging)
- Mantener f-strings simples: si la expresión es compleja, extraer a variable

❌ Mal:
  message = "Hello %s, you have %d messages" % (name, count)
  message = "Hello {}, you have {} messages".format(name, count)

✅ Bien:
  message = f"Hello {name}, you have {count} messages"

### Walrus Operator (Python 3.8+)
- Usar := cuando simplifica el código evitando duplicar una expresión

❌ Antes:
  match = pattern.search(text)
  if match:
      process(match)

✅ Después:
  if match := pattern.search(text):
      process(match)