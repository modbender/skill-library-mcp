# Reglas de Seguridad

Estas reglas aplican a TODOS los lenguajes. La seguridad nunca es opcional.

---

## 🔴 BLOCKERS — SIEMPRE RECHAZAR

### Secrets Expuestos

Detectar cualquiera de estos patrones:

- Variables con nombres como password, secret, api_key, token, auth con valores hardcodeados
- Strings que parecen JWT: eyJ seguido de caracteres base64
- Strings que parecen API keys: longitud mayor a 20 caracteres alfanuméricos mezclados
- URLs con credenciales embebidas: protocol://user:password@host
- Archivos .env, .pem, .key commiteados al repositorio
- Comentarios con credenciales de ejemplo que parecen reales

### Inyección SQL

❌ NUNCA concatenar input del usuario en queries:

  JavaScript: const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
  JavaScript: const query = "SELECT * FROM users WHERE name = '" + userName + "'";
  PHP: $query = "SELECT * FROM users WHERE id = " . $_GET['id'];

✅ SIEMPRE usar queries parametrizadas:

  JavaScript: const query = 'SELECT * FROM users WHERE id = $1';
              const result = await db.query(query, [req.params.id]);
  PHP: $stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
       $stmt->execute(['id' => $id]);

### Inyección de Comandos

❌ NUNCA ejecutar comandos con input del usuario sin sanitizar:

  JavaScript: exec(`rm -rf ${userInput}`);
  JavaScript: child_process.exec('ls ' + directory);
  PHP: shell_exec("cat " . $filename);

✅ SIEMPRE usar funciones seguras con argumentos separados:

  JavaScript: execFile('ls', [directory]);
  PHP: escapeshellarg($filename);

### XSS (Cross-Site Scripting)

❌ NUNCA insertar input del usuario como HTML sin sanitizar:

  JavaScript: element.innerHTML = userInput;
  JavaScript: document.write(userInput);
  React: dangerouslySetInnerHTML={{__html: userComment}}
  PHP: echo $_GET['name'];

✅ SIEMPRE sanitizar:

  JavaScript: element.textContent = userInput;
  React: import DOMPurify from 'dompurify';
         dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userComment)}}
  PHP: echo htmlspecialchars($name, ENT_QUOTES, 'UTF-8');

### Autenticación y Autorización
- Endpoints de API sin middleware de autenticación
- Verificación de roles o permisos solo en el frontend
- Tokens sin fecha de expiración
- Comparación de passwords en texto plano sin hashing
- Uso de algoritmos de hash débiles para passwords: MD5, SHA1
- Sesiones que no se invalidan al hacer logout

---

## 🟡 WARNINGS

### CORS
- Access-Control-Allow-Origin con valor * en producción
- Métodos HTTP permitidos demasiado amplios sin necesidad
- Headers permitidos excesivamente permisivos

### Dependencias
- Dependencias con vulnerabilidades conocidas (CVE)
- Versiones no fijadas que podrían cambiar sin control
- Dependencias abandonadas o sin mantenimiento activo

### Logging Inseguro
- Logging de datos sensibles: passwords, tokens, tarjetas de crédito
- Logging de datos personales sin necesidad: emails, teléfonos, direcciones
- Stack traces completos expuestos al usuario final en producción
- Logging de request bodies completos que pueden contener datos sensibles

### Headers de Seguridad Faltantes
- Content-Security-Policy
- X-Content-Type-Options: nosniff
- Strict-Transport-Security
- X-Frame-Options

### Rate Limiting
- Endpoints públicos sin rate limiting
- Endpoints de autenticación sin protección contra fuerza bruta
- Endpoints de upload sin límite de tamaño de archivo

---

## 🔵 SUGGESTIONS

### Mejoras de Seguridad
- Implementar CSRF tokens en formularios
- Usar HttpOnly y Secure flags en cookies
- Implementar Content Security Policy estricta
- Validar y sanitizar todos los inputs en el backend independientemente del frontend
- Usar prepared statements en absolutamente todas las queries
- Implementar logging de auditoría para acciones sensibles
- Rotar secrets y tokens periódicamente