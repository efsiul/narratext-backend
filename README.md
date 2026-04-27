# NarraText — Backend

Backend del proyecto NarraText. Mono-repo Maven multi-módulo con arquitectura hexagonal por microservicio.

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Java 17 |
| Framework | Spring Boot 3.2.5 + Spring Cloud 2023.0.3 |
| Discovery | Eureka (`discovery-service`) |
| Gateway | Spring Cloud Gateway (`gateway-service`) |
| Persistencia | PostgreSQL 14 (una BD por microservicio) |
| Migraciones | Flyway 10 |
| Mapper | MapStruct 1.5.5 |
| JWT | Auth0 java-jwt 4.4.0 |
| TTS engine | `edge-tts-http` (Python, externo) |
| Contenedores | Docker + docker-compose |

## Microservicios

| Puerto | Servicio | BD |
|---|---|---|
| 8760 | `discovery-service` | — |
| 8820 | `gateway-service` | — |
| 8821 | `auth-service` | `auth_db` |
| 8830 | `library-service` | `library_db` |
| 8831 | `reading-service` | `reading_db` |
| 8832 | `tts-service` | `tts_db` |
| 8833 | `social-service` | `social_db` |
| 8834 | `notification-service` | — |
| 5000 | `edge-tts-http` (externo) | — |

## Inicio rápido

```bash
# 1. Copiar variables de entorno
cp .env.example .env
# Editar .env con tus valores reales

# 2. Copiar edge-tts-http desde BOPOSV2_SCO
cp -r /ruta/a/BOPOSV2_SCO/edge-tts-http ./edge-tts-http

# 3. Levantar infraestructura base
docker-compose up postgres edge-tts-http

# 4. Compilar (requiere Java 17 + Maven 3.9+)
mvn clean package -DskipTests

# 5. Levantar todo
docker-compose up
```

## Estructura de cada microservicio

```
{servicio}/
├── pom.xml
├── Dockerfile
└── src/main/java/com/narratext/{servicio}/
    ├── domain/
    │   ├── model/          ← entidades de dominio (POJOs puros, sin Spring)
    │   ├── port/
    │   │   ├── in/         ← interfaces de casos de uso
    │   │   └── out/        ← interfaces de repositorios y gateways
    │   └── service/        ← implementación de los casos de uso
    ├── application/
    │   ├── usecase/        ← @Service que implementan port.in
    │   └── dto/            ← DTOs de aplicación
    └── infrastructure/
        ├── adapter/
        │   ├── in/rest/    ← @RestController, DTOs REST
        │   └── out/
        │       ├── persistence/  ← JPA entities, repositories, mappers
        │       └── client/       ← Feign clients
        └── config/         ← @Configuration, SecurityConfig
```

## Convenciones de API

- Verbos HTTP estándar: `GET`, `POST`, `PUT`, `DELETE`
- Prefijo de ruta: `/api/v1/{recurso}`
- Paginación: `Page<T>` de Spring Data
- Soft-delete: columna `deleted_at timestamp`
- Prefijo de tablas: `lt_{servicio}_{entidad}` (ej. `lt_auth_user`)
- Packages: `com.narratext.{servicio}` (ej. `com.narratext.auth`)
