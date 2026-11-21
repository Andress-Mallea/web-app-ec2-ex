# Hotel Mirador · web-app-ec2-ex

Sistema de recepción de un hotel: habitaciones, huéspedes y reservas.

- `backend/`: API REST en Flask con **arquitectura por capas** (`routes -> services -> repositories -> models`) y SQLite.
- `frontend/`: HTML, CSS y JavaScript sin frameworks.

Todo corre con Docker Compose: el backend usa el servidor de desarrollo de Flask y el frontend el servidor estático de Python. No hay nginx ni gunicorn.

## Levantar el proyecto

```bash
docker compose up --build
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:8080 |
| API | http://localhost:8000/api |
| Salud | http://localhost:8000/api/health |

En una EC2 se usan las mismas URL con la IP pública (abrir los puertos 8080 y 8000 en el security group). El frontend arma la URL de la API con el mismo host desde el que se abrió la página.

La primera vez se cargan datos de ejemplo. Para empezar con la base vacía:

```bash
docker compose down -v
```

El código de las dos carpetas está montado en los contenedores: al guardar un archivo del backend, Flask se recarga solo; en el frontend basta con refrescar el navegador.

## Pruebas

```bash
docker compose exec backend pytest -q
```

## Estructura (MVC)

```
REGLAS.md                      reglas de negocio del hotel
backend/
├── run.py                     punto de entrada (flask --app run:app)
├── app/
│   ├── __init__.py            create_app: composición de capas, CORS, blueprints y manejo de errores
│   ├── config.py              configuración de Flask y SQLAlchemy
│   ├── errors.py              excepciones de dominio (400, 404, 409, 422)
│   ├── seed.py                datos de ejemplo
│   ├── routes/                presentación: blueprints HTTP y armado de DTOs
│   ├── services/              lógica de negocio: casos de uso, 10 reglas, DTOs y Strategy de precios
│   ├── repositories/          acceso a datos: consultas SQLAlchemy y db.session
│   ├── models/                modelos: entidades SQLAlchemy y mapeo a tablas
│   └── views/                 serializadores JSON (contrato con el frontend)
└── tests/
    ├── test_api.py            pruebas base de la API
    └── test_business_rules.py pruebas de las 10 reglas de negocio
frontend/
├── index.html
└── src/
    ├── api.js                    ← único archivo con fetch
    ├── main.js                   ← arranque
    ├── utils.js                  ← $, el, formatMoney
    ├── base/
    │   └── base.css              ← variables, reset, tipografía
    ├── blocks/
    │   ├── header/
    │   │   └── header.css
    │   ├── tabs/
    │   │   ├── tabs.css
    │   │   └── tabs.js
    │   ├── page/
    │   │   └── page.css
    │   ├── card/
    │   │   └── card.css
    │   ├── form/
    │   │   └── form.css
    │   ├── button/
    │   │   ├── button.css
    │   │   └── button.js
    │   ├── table/
    │   │   ├── table.css
    │   │   └── table.js
    │   ├── badge/
    │   │   ├── badge.css
    │   │   └── badge.js
    │   └── alert/
    │       ├── alert.css
    │       └── alert.js
    └── features/
        ├── rooms.js
        ├── guests.js
        └── reservations.js
```
El backend organiza sus dependencias en una sola dirección (routes -> services -> repositories -> models):

Presentación (routes/): lee la petición HTTP, arma DTOs, llama al servicio y devuelve JSON; no usa db.session ni Model.query.

Servicios (services/): concentra los casos de uso, las 10 reglas de negocio (REGLAS.md), los DTOs (dto.py) y el patrón Strategy de tarifas (pricing.py); nunca importa Flask.

Repositorios (repositories/): encapsula todas las consultas SQLAlchemy y la persistencia, sin lógica de negocio.

Modelos (models/): define las entidades y sus tablas sin conocer capas superiores.

Errores (errors.py): las excepciones de dominio (BusinessRuleError, NotFoundError, ConflictError, ValidationError) se traducen a HTTP en un único errorhandler en app/__init__.py.
## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/rooms?status=` | lista de habitaciones |
| GET | `/api/rooms/:id` | una habitación |
| POST | `/api/rooms` | crea `{ number, type, price_per_night, capacity }` |
| PUT | `/api/rooms/:id` | modifica `type`, `status`, `price_per_night` o `capacity` |
| DELETE | `/api/rooms/:id` | elimina (409 si tiene reservas) |
| GET | `/api/guests` | lista de huéspedes |
| GET | `/api/guests/:id` | un huésped |
| POST | `/api/guests` | crea `{ full_name, email, document }` |
| DELETE | `/api/guests/:id` | elimina (409 si tiene reservas) |
| GET | `/api/reservations?status=&guest_id=` | lista de reservas |
| GET | `/api/reservations/:id` | una reserva |
| POST | `/api/reservations` | crea `{ room_id, guest_id, check_in, check_out, guests_count }` |
| PATCH | `/api/reservations/:id/cancel` | cancela |
| PATCH | `/api/reservations/:id/check-in` | registra el ingreso |
| PATCH | `/api/reservations/:id/check-out` | registra la salida |

Valores válidos:

- `type`: `single`, `double`, `family`, `suite`.
- `status` de habitación: `available`, `maintenance`.
- `status` de reserva: `confirmed`, `checked_in`, `checked_out`, `cancelled`.
- Fechas en formato `AAAA-MM-DD`; precios en bolivianos.

Los errores se devuelven como `{ "error": "mensaje" }` con el código HTTP correspondiente (422 cuando se incumple una regla de negocio; ver REGLAS.md).


