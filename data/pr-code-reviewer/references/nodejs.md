# Reglas Node.js

Aplica a archivos de backend Node.js: .js, .ts, .mjs, .cjs
que corran en entorno servidor (APIs, servicios, scripts, workers).

---

## 🔴 BLOCKERS

### Process y Event Loop
- Uso de funciones síncronas de fs en código de servidor: readFileSync, writeFileSync, etc.
  Solo es aceptable en scripts de inicialización o CLI tools.
- Bloquear el event loop con operaciones CPU-intensive sin worker threads
- process.exit() sin manejar cleanup de conexiones abiertas
- No manejar señales de terminación: SIGTERM, SIGINT

❌ Mal (en un endpoint de API):
  app.get('/file', (req, res) => {
    const content = fs.readFileSync('/path/to/file', 'utf8');
    res.send(content);
  });

✅ Bien:
  app.get('/file', async (req, res) => {
    try {
      const content = await fs.promises.readFile('/path/to/file', 'utf8');
      res.send(content);
    } catch (error) {
      res.status(500).json({ error: 'Failed to read file' });
    }
  });

### Memory Leaks
- Event listeners que se agregan pero nunca se remueven
- Acumulación de datos en variables globales o closures
- Streams que no se cierran o destruyen correctamente
- Caché en memoria sin límite de tamaño ni expiración

❌ Mal:
  const cache = {};
  app.get('/data/:id', async (req, res) => {
    if (!cache[req.params.id]) {
      cache[req.params.id] = await fetchData(req.params.id);
    }
    res.json(cache[req.params.id]);
  });
  // El cache crece infinitamente sin límite

✅ Bien:
  const NodeCache = require('node-cache');
  const cache = new NodeCache({ stdTTL: 600, maxKeys: 1000 });

  app.get('/data/:id', async (req, res) => {
    const cached = cache.get(req.params.id);
    if (cached) return res.json(cached);

    const data = await fetchData(req.params.id);
    cache.set(req.params.id, data);
    res.json(data);
  });

### Errores No Capturados
- No tener handler para unhandledRejection
- No tener handler para uncaughtException
- Promesas sin catch que pueden crashear el proceso

✅ Siempre incluir en el entry point:
  process.on('unhandledRejection', (reason, promise) => {
    logger.error('Unhandled Rejection:', reason);
    // Decidir si hacer graceful shutdown
  });

  process.on('uncaughtException', (error) => {
    logger.error('Uncaught Exception:', error);
    // Hacer graceful shutdown
    process.exit(1);
  });

### Seguridad de Dependencias
- Usar eval() o new Function() con datos dinámicos
- Usar child_process.exec() con strings concatenados del usuario
- Deserializar datos no confiables sin validación: JSON.parse de input sin try/catch
- Servir archivos estáticos sin validar el path (path traversal)

❌ Mal (path traversal):
  app.get('/files/:name', (req, res) => {
    res.sendFile('/uploads/' + req.params.name);
  });

✅ Bien:
  const path = require('path');
  app.get('/files/:name', (req, res) => {
    const safePath = path.join(__dirname, 'uploads', path.basename(req.params.name));
    res.sendFile(safePath);
  });

---

## 🟡 WARNINGS

### Express / Framework HTTP
- Endpoints sin validación de input: body, params, query
- Endpoints sin manejo de errores (sin try/catch o middleware de errores)
- No usar helmet o headers de seguridad equivalentes
- No usar compression para respuestas grandes
- Rutas sin autenticación que deberían tenerla
- No limitar el tamaño del body en requests

❌ Mal:
  app.post('/users', async (req, res) => {
    const user = await User.create(req.body);
    res.json(user);
  });

✅ Bien:
  app.post('/users',
    authenticate,
    validateBody(createUserSchema),
    async (req, res, next) => {
      try {
        const user = await User.create(req.body);
        res.status(201).json(user);
      } catch (error) {
        next(error);
      }
    }
  );

### Base de Datos
- Conexiones que no se cierran o no usan connection pooling
- Queries sin timeout configurado
- No usar transacciones cuando se hacen múltiples writes relacionados
- Queries dentro de loops: N+1 problem
- No indexar campos que se usan frecuentemente en WHERE o JOIN

❌ Mal (N+1 problem):
  app.get('/users-with-posts', async (req, res) => {
    const users = await User.findAll();
    for (const user of users) {
      user.posts = await Post.findAll({ where: { userId: user.id } });
    }
    res.json(users);
  });

✅ Bien:
  app.get('/users-with-posts', async (req, res) => {
    const users = await User.findAll({
      include: [{ model: Post }]
    });
    res.json(users);
  });

### Environment y Configuración
- Valores de configuración hardcodeados en lugar de usar variables de entorno
- No validar que las variables de entorno requeridas existan al iniciar
- Usar valores por defecto inseguros para variables de entorno
- Mezclar configuración de diferentes environments en el mismo archivo

❌ Mal:
  const db = new Database({
    host: 'localhost',
    port: 5432,
    password: 'mypassword123'
  });

✅ Bien:
  const requiredEnvVars = ['DB_HOST', 'DB_PORT', 'DB_PASSWORD'];
  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      throw new Error(`Missing required environment variable: ${envVar}`);
    }
  }

  const db = new Database({
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT, 10),
    password: process.env.DB_PASSWORD
  });

### Logging
- Usar console.log en lugar de un logger estructurado (winston, pino, bunyan)
- No incluir contexto útil en los logs: request ID, user ID, timestamp
- Logear datos sensibles: passwords, tokens, datos personales
- No tener diferentes niveles de log: error, warn, info, debug

### Error Handling en Middleware
- No tener un middleware global de manejo de errores
- Enviar stack traces al cliente en producción
- No diferenciar entre errores operacionales y errores de programación

✅ Middleware de errores recomendado:
  app.use((err, req, res, next) => {
    logger.error({
      message: err.message,
      stack: err.stack,
      requestId: req.id,
      path: req.path,
      method: req.method
    });

    if (err.isOperational) {
      return res.status(err.statusCode).json({
        error: err.message
      });
    }

    res.status(500).json({
      error: process.env.NODE_ENV === 'production'
        ? 'Internal server error'
        : err.message
    });
  });

---

## 🔵 SUGGESTIONS

### Estructura de Proyecto
- Separar rutas, controladores, servicios y modelos en carpetas distintas
- Usar un archivo de rutas por recurso o dominio
- Centralizar la configuración en un solo módulo
- Usar inyección de dependencias o al menos factories para testabilidad

### Validación
- Usar librerías de validación como Joi, Zod, Yup o class-validator
- Validar en la capa de entrada (middleware) no en el servicio
- Definir schemas reutilizables para request y response

### Graceful Shutdown

✅ Implementar siempre:
  const server = app.listen(port);

  async function gracefulShutdown(signal) {
    logger.info(`Received ${signal}. Starting graceful shutdown...`);

    server.close(async () => {
      logger.info('HTTP server closed');

      try {
        await database.close();
        logger.info('Database connections closed');

        await cache.quit();
        logger.info('Cache connections closed');

        process.exit(0);
      } catch (error) {
        logger.error('Error during shutdown:', error);
        process.exit(1);
      }
    });

    // Forzar cierre si tarda más de 30 segundos
    setTimeout(() => {
      logger.error('Forced shutdown after timeout');
      process.exit(1);
    }, 30000);
  }

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));

### Streaming para Datos Grandes
- Usar streams en lugar de cargar todo en memoria para archivos grandes
- Usar cursor o paginación para queries que retornan muchos registros
- Pipe de streams para transformaciones de datos

❌ Mal:
  app.get('/export', async (req, res) => {
    const allRecords = await Record.findAll(); // Puede ser millones
    const csv = convertToCSV(allRecords); // Todo en memoria
    res.send(csv);
  });

✅ Bien:
  app.get('/export', async (req, res) => {
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=export.csv');

    const cursor = Record.findAllCursor();
    const transform = new CSVTransformStream();

    cursor.pipe(transform).pipe(res);
  });

### Package.json
- Fijar versiones exactas o usar lock files (package-lock.json o yarn.lock)
- Separar dependencies de devDependencies correctamente
- Definir scripts de start, build, test, lint
- Definir engines con la versión mínima de Node.js requerida
- No incluir dependencias innecesarias que aumenten el tamaño del bundle

### Testing
- Usar supertest para testing de endpoints HTTP
- Mockear dependencias externas: base de datos, APIs externas, file system
- Testear middleware de forma aislada
- Testear error handlers con diferentes tipos de error
- Usar fixtures o factories para datos de prueba en lugar de hardcodearlos

---

## 💡 NITS

### Estilo Node.js
- Preferir import/export (ESM) sobre require/module.exports (CJS) en proyectos nuevos
- Usar path.join() o path.resolve() en lugar de concatenar paths con /
- Usar util.promisify() para convertir funciones callback a promesas
- Preferir fs.promises sobre las versiones callback de fs
- Mantener consistencia en el manejo de errores: siempre async/await o siempre callbacks, no mezclar

### Naming de Archivos
- Usar kebab-case para nombres de archivos: user-controller.js, not userController.js
- Usar .routes.js, .controller.js, .service.js, .model.js como sufijos descriptivos
- Usar index.js solo como barrel file para re-exportar, no para lógica de negocio