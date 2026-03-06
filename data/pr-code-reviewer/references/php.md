# Reglas PHP

Aplica a archivos con extensión: .php

---

## 🔴 BLOCKERS

### Inyección SQL
- NUNCA concatenar variables en queries SQL
- NUNCA usar variables de $_GET, $_POST, $_REQUEST directamente en queries
- NUNCA confiar en magic_quotes o addslashes como protección

❌ Mal:
  $query = "SELECT * FROM users WHERE id = " . $_GET['id'];
  $query = "SELECT * FROM users WHERE name = '$name'";
  $result = mysqli_query($conn, "DELETE FROM posts WHERE id = {$_POST['id']}");

✅ Bien (PDO):
  $stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
  $stmt->execute(['id' => $id]);
  $user = $stmt->fetch(PDO::FETCH_ASSOC);

✅ Bien (MySQLi):
  $stmt = $mysqli->prepare('SELECT * FROM users WHERE id = ?');
  $stmt->bind_param('i', $id);
  $stmt->execute();
  $result = $stmt->get_result();

### XSS (Cross-Site Scripting)
- NUNCA hacer echo de variables sin escapar
- NUNCA confiar en el input del usuario para output HTML

❌ Mal:
  echo $_GET['name'];
  echo $user['bio'];
  <?= $comment->body ?>

✅ Bien:
  echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
  echo htmlspecialchars($user['bio'], ENT_QUOTES, 'UTF-8');
  <?= htmlspecialchars($comment->body, ENT_QUOTES, 'UTF-8') ?>

✅ Mejor (crear helper):
  function e($string) {
    return htmlspecialchars($string, ENT_QUOTES, 'UTF-8');
  }
  echo e($user['bio']);

### Inyección de Comandos
- NUNCA pasar input del usuario a funciones de ejecución de comandos sin sanitizar

❌ Mal:
  exec("ls " . $_GET['dir']);
  system("ping " . $host);
  shell_exec("cat " . $filename);
  passthru("convert " . $uploadedFile);

✅ Bien:
  exec("ls " . escapeshellarg($dir));
  system("ping " . escapeshellarg($host));
  // Mejor aún: usar funciones nativas de PHP en lugar de comandos del sistema
  $files = scandir($dir); // En lugar de exec("ls ...")

### Inclusión de Archivos
- NUNCA usar variables del usuario en include/require sin validar

❌ Mal:
  include($_GET['page'] . '.php');
  require($module . '.php');

✅ Bien:
  $allowedPages = ['home', 'about', 'contact'];
  $page = in_array($_GET['page'], $allowedPages) ? $_GET['page'] : 'home';
  include($page . '.php');

### Upload de Archivos Inseguro
- NUNCA confiar en el nombre o tipo MIME enviado por el cliente
- NUNCA guardar archivos subidos en directorios accesibles sin validación

❌ Mal:
  $target = "uploads/" . $_FILES['file']['name'];
  move_uploaded_file($_FILES['file']['tmp_name'], $target);

✅ Bien:
  $allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  $finfo = new finfo(FILEINFO_MIME_TYPE);
  $mimeType = $finfo->file($_FILES['file']['tmp_name']);

  if (!in_array($mimeType, $allowedTypes)) {
    throw new Exception('Tipo de archivo no permitido');
  }

  $extension = array_search($mimeType, [
    'jpg' => 'image/jpeg',
    'png' => 'image/png',
    'gif' => 'image/gif',
  ]);

  $newName = bin2hex(random_bytes(16)) . '.' . $extension;
  $target = '/var/uploads/' . $newName; // Fuera del document root
  move_uploaded_file($_FILES['file']['tmp_name'], $target);

### Deserialización Insegura
- NUNCA usar unserialize() con datos del usuario

❌ Mal:
  $data = unserialize($_COOKIE['user_data']);
  $obj = unserialize(file_get_contents('php://input'));

✅ Bien:
  $data = json_decode($_COOKIE['user_data'], true);
  // Si necesitas unserialize, usa allowed_classes
  $data = unserialize($input, ['allowed_classes' => false]);

---

## 🟡 WARNINGS

### Funciones Obsoletas y Peligrosas
- mysql_* funciones: usar PDO o MySQLi en su lugar
- ereg, eregi: usar preg_match en su lugar
- create_function(): usar closures anónimas
- extract() con datos del usuario: sobreescribe variables del scope
- eval(): casi nunca es necesario, buscar alternativa

### Manejo de Errores
- No usar try/catch en operaciones que pueden fallar
- catch vacíos que silencian errores
- No configurar error reporting adecuadamente para producción
- Mostrar errores detallados al usuario en producción

❌ Mal:
  try {
    $result = riskyOperation();
  } catch (Exception $e) {
    // silencio
  }

  // En producción:
  ini_set('display_errors', 1);
  error_reporting(E_ALL);

✅ Bien:
  try {
    $result = riskyOperation();
  } catch (SpecificException $e) {
    $logger->error('Operation failed', [
      'error' => $e->getMessage(),
      'context' => $relevantData
    ]);
    throw new UserFriendlyException('La operación no pudo completarse');
  }

  // En producción:
  ini_set('display_errors', 0);
  ini_set('log_errors', 1);
  error_reporting(E_ALL);

### Tipado
- Funciones sin type hints en parámetros
- Funciones sin return type declaration
- No usar strict_types en archivos nuevos
- Usar mixed cuando se puede ser más específico

❌ Mal:
  function getUser($id) {
    // ...
  }

✅ Bien:
  declare(strict_types=1);

  function getUser(int $id): ?User {
    // ...
  }

### Passwords
- NUNCA usar md5() o sha1() para hashear passwords
- NUNCA almacenar passwords en texto plano
- NUNCA crear tu propio sistema de hashing

❌ Mal:
  $hash = md5($password);
  $hash = sha1($password . $salt);

✅ Bien:
  // Hashear:
  $hash = password_hash($password, PASSWORD_DEFAULT);

  // Verificar:
  if (password_verify($inputPassword, $storedHash)) {
    // Password correcto
  }

### Sesiones
- session_start() sin configurar opciones de seguridad
- No regenerar session ID después del login
- No destruir sesión correctamente en logout
- Session fixation: no validar que la sesión pertenece al usuario

✅ Configuración segura de sesiones:
  ini_set('session.cookie_httponly', 1);
  ini_set('session.cookie_secure', 1);
  ini_set('session.use_strict_mode', 1);
  ini_set('session.cookie_samesite', 'Lax');
  session_start();

  // Después del login exitoso:
  session_regenerate_id(true);

  // En logout:
  session_unset();
  session_destroy();
  setcookie(session_name(), '', time() - 3600, '/');

### CSRF
- Formularios POST sin token CSRF
- No validar token CSRF en el servidor
- Token CSRF predecible o reutilizable

✅ Implementación básica:
  // Generar token:
  if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
  }

  // En el formulario:
  <input type="hidden" name="csrf_token" value="<?= e($_SESSION['csrf_token']) ?>">

  // Validar en el servidor:
  if (!hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'] ?? '')) {
    http_response_code(403);
    die('Invalid CSRF token');
  }

---

## 🔵 SUGGESTIONS

### PSR Standards
- Seguir PSR-1: Basic Coding Standard
- Seguir PSR-4: Autoloading Standard (namespaces que coincidan con la estructura de directorios)
- Seguir PSR-12: Extended Coding Style Guide
- Usar PSR-3: Logger Interface (compatible con Monolog, etc.)
- Usar PSR-7: HTTP Message Interface cuando sea apropiado

### Arquitectura
- Separar lógica de negocio de la capa de presentación
- No poner lógica SQL directamente en controladores
- Usar Repository pattern para acceso a datos
- Usar Service layer para lógica de negocio compleja
- Usar Dependency Injection en lugar de instanciar dependencias dentro de clases

❌ Mal:
  class UserController {
    public function getUser(int $id): Response {
      $pdo = new PDO('mysql:host=localhost;dbname=app', 'root', 'pass');
      $stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
      $stmt->execute(['id' => $id]);
      $user = $stmt->fetch();
      return new Response(json_encode($user));
    }
  }

✅ Bien:
  class UserController {
    public function __construct(
      private readonly UserService $userService
    ) {}

    public function getUser(int $id): Response {
      $user = $this->userService->findById($id);
      if (!$user) {
        return new Response('Not found', 404);
      }
      return new Response(json_encode($user));
    }
  }

### Composer y Dependencias
- Usar Composer para autoloading y gestión de dependencias
- Fijar versiones en composer.json o usar composer.lock
- No commitear la carpeta vendor (usar .gitignore)
- Separar require de require-dev correctamente
- Mantener dependencias actualizadas y sin vulnerabilidades conocidas

### Null Safety
- Usar null coalescing operator ?? en lugar de isset ternarios
- Usar nullsafe operator ?-> (PHP 8+) para cadenas de llamadas
- Tipar nullable explícitamente con ? cuando una función puede retornar null

❌ Antes:
  $city = isset($user) && isset($user->address) ? $user->address->city : 'Unknown';

✅ Después (PHP 8+):
  $city = $user?->address?->city ?? 'Unknown';

### Enums (PHP 8.1+)
- Usar enums en lugar de constantes sueltas para valores finitos
- Preferir backed enums cuando se necesita persistir el valor

❌ Antes:
  const STATUS_ACTIVE = 'active';
  const STATUS_INACTIVE = 'inactive';
  const STATUS_BANNED = 'banned';

✅ Después:
  enum UserStatus: string {
    case Active = 'active';
    case Inactive = 'inactive';
    case Banned = 'banned';
  }

### Match Expression (PHP 8+)
- Preferir match sobre switch cuando se retorna un valor
- match es estricto en comparación (===) y no necesita break

❌ Antes:
  switch ($status) {
    case 'active':
      $label = 'Activo';
      break;
    case 'inactive':
      $label = 'Inactivo';
      break;
    default:
      $label = 'Desconocido';
  }

✅ Después:
  $label = match($status) {
    'active' => 'Activo',
    'inactive' => 'Inactivo',
    default => 'Desconocido',
  };

---

## 💡 NITS

### Estilo
- Usar camelCase para métodos y variables
- Usar PascalCase para clases, interfaces, traits, enums
- Usar UPPER_SNAKE_CASE para constantes
- Abrir llaves en la misma línea para estructuras de control
- Abrir llaves en línea nueva para clases y métodos (PSR-12)
- Un namespace por archivo
- Un use import por línea, ordenados alfabéticamente
- Línea en blanco después de la declaración de namespace
- Línea en blanco después del bloque de use imports

### PHP Moderno
- Preferir constructor property promotion (PHP 8+)
- Preferir named arguments para funciones con muchos parámetros opcionales
- Usar readonly properties cuando el valor no debe cambiar después de la inicialización
- Usar union types en lugar de docblocks para tipado
- Usar str_contains(), str_starts_with(), str_ends_with() (PHP 8+) en lugar de strpos hacks

❌ Antes:
  if (strpos($haystack, $needle) !== false) {}

✅ Después:
  if (str_contains($haystack, $needle)) {}