-- NarraText — inicialización de bases de datos
-- Ejecutado automáticamente por el contenedor postgres al primer arranque.
-- Una base de datos por microservicio (patrón DB-per-service).

CREATE DATABASE auth_db;
CREATE DATABASE library_db;
CREATE DATABASE reading_db;
CREATE DATABASE tts_db;
CREATE DATABASE social_db;
