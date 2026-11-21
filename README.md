# Hotel Mirador · web-app-ec2-ex

Sistema de recepción de un hotel: habitaciones, huéspedes y reservas.

- `backend/`: API REST en Flask con **arquitectura por capas** (`routes -> services -> repositories -> models`) y SQLite.
- `frontend/`: HTML, CSS y JavaScript sin frameworks, con **capa de API** (`api.js`) y CSS **BEM** dividido por bloque.

Todo corre con Docker Compose: el backend usa el servidor de desarrollo de Flask y el frontend el servidor estático de Python. No hay nginx ni gunicorn.

## Levantar el proyecto

```bash
docker compose up --build
```

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:8080 |
| API      | http://localhost:8000/api |
| Salud    | http://localhost:8000/api/health |

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

## Estructura y arquitectura por capas

```text
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
├── index.html                 único HTML (marcado con clases BEM)
└── src/
    ├── api.js                 única capa que usa fetch
    ├── main.js                punto de entrada
    ├── utils.js               helpers de DOM y formato de dinero
    ├── base/
    │   └── base.css           variables CSS, reset y tipografía
    ├── blocks/                un bloque BEM por carpeta
    │   ├── header/            header.css
    │   ├── tabs/              tabs.css · tabs.js
    │   ├── page/              page.css
    │   ├── card/              card.css
    │   ├── form/              form.css
    │   ├── button/            button.css · button.js
    │   ├── table/             table.css · table.js
    │   ├── badge/             badge.css · badge.js
    │   └── alert/             alert.css · alert.js
    └── features/              pantallas que consumen los bloques
        ├── rooms.js
        ├── guests.js
        └── reservations.js
```
## Documentación de Refactorización (Backend y Arquitectura)

### 1. Resumen de la Interacción
1. Se analizó el enunciado del examen (*Hotel Mirador*) y el estado inicial del backend en Flask organizado en MVC, donde los controladores concentraban validación, acceso a datos (`Model.query`, `db.session`), lógica de negocio y respuestas HTTP.
2. Se redactó `REGLAS.md` con las 10 reglas de negocio identificadas en el relato de la gerente y se propuso la estructura de carpetas para migrar a una arquitectura por capas.
3. El usuario consultó sobre la inclusión de patrones adicionales (como `Decorator`) y solicitó incorporar el patrón **DTO**, actualizando el árbol de carpetas antes de escribir el código.
4. Se implementó el backend paso a paso por capas: excepciones de dominio (`errors.py`), repositorios (`repositories/`), servicios con DTOs y Strategy (`services/`), rutas HTTP (`routes/`), raíz de composición y manejador único de errores (`app/__init__.py`), además del ajuste en `seed.py`.
5. Se crearon las 10 pruebas automatizadas en `backend/tests/test_business_rules.py`, se redactó la sección de arquitectura para `README.md` y se verificó la ejecución con Docker Compose (`19 passed` en `pytest`, manteniendo intactas las 9 pruebas originales).

### 2. Propuestas (IA vs. Usuario)
- **Propuesta inicial de la IA:**
  - Migrar de MVC a **Arquitectura por Capas** con dependencias unidireccionales (`routes -> services -> repositories -> models`), siguiendo el enfoque de la rama `arq-2-capas` del material de clase.
  - Aplicar **Service Layer**, **Repository** y **Strategy** (para el cálculo de tarifas y descuento por estadía larga), junto con excepciones de dominio traducidas en un único `@app.errorhandler(AppError)`.
  - Mantener intactos `models/`, `views/`, `config.py` y los archivos de Docker, eliminando la carpeta antigua `controllers/`.
- **Cambios y contrapropuestas del usuario:**
  - Cuestionó por qué no se incluían otros patrones como **Decorator**.
  - Solicitó sumar explícitamente el patrón **DTO** (`app/services/dto.py`) y regenerar el árbol de carpetas con esa incorporación.
  - Verificó el estado de `models/`, `views/`, `config.py`, `seed.py`, `views/__init__.py` y los archivos de Docker antes de pasar a las pruebas y a la estrategia de commits pequeños.

### 3. Decisiones Aceptadas (Qué se quedó y por qué)
- **Arquitectura por Capas (`routes -> services -> repositories -> models`):** Aísla responsabilidades de forma estricta y evita que la lógica de negocio se filtre a las rutas o a las consultas SQL.
- **Service Layer + Repository + Strategy + DTO:** Conjunto de patrones alineado con `arq-2-capas` que resuelve problemas concretos sin caer en sobreingeniería.
- **Manejador único de errores (`app/errors.py` + `app/__init__.py`):** Centraliza la traducción de excepciones de dominio a códigos HTTP (`400`, `404`, `409`, `422`) en un solo punto.
- **Actualización de `app/seed.py`:** Se integró `select_pricing_strategy` para que la reserva inicial de 7 noches refleje el 10% de descuento desde el arranque.
- **Conservación de `models/`, `views/`, `config.py` y Docker:** Se mantuvieron sin cambios para preservar el contrato JSON del frontend y cumplir con el entorno Docker Compose sin Nginx ni Gunicorn.

### 4. Decisiones Descartadas (Qué se descartó y por qué)
- **Patrón Decorator:** Descartado porque en el curso se aplica principalmente para autenticación/permisos (`@requires_auth`), funcionalidad ausente en este examen, y la traducción de errores ya se resuelve de forma más limpia con `@app.errorhandler(AppError)` en Flask.
- **Patrón State:** Evaluado para la máquina de estados de reservas (Regla 8), pero descartado para evitar sobreingeniería frente a `ALLOWED_TRANSITIONS` dentro de `ReservationService`, manteniendo la complejidad acorde a `arq-2-capas`.
- **Reexportaciones en `views/__init__.py`:** Descartado porque cada archivo de ruta importa directamente su serializador específico sin necesidad de indirección extra.
- **Modificar `Dockerfile` o `docker-compose.yml`:** Descartado porque el punto de entrada (`run.py`) y las dependencias (`requirements.txt`) no cambiaron y la consigna exige mantener el entorno sin Nginx ni Gunicorn.

### 5. Arquitectura del Backend
Se migró el backend de MVC a una **Arquitectura por Capas** con flujo unidireccional (`routes -> services -> repositories -> models`):

- **`backend/app/routes/` (Presentación):** Recibe la petición HTTP, valida presencia/tipos básicos, construye el DTO, invoca al servicio y devuelve JSON. *Por qué:* desacopla HTTP de la lógica de negocio y elimina cualquier uso de `db.session` o `Model.query` en los endpoints.
- **`backend/app/services/` (Lógica de negocio):** Contiene los casos de uso, las 10 reglas de negocio, los DTOs y las estrategias de precio, sin importar Flask. *Por qué:* permite reutilizar y probar las reglas independientemente del framework web y centraliza el control de `commit`.
- **`backend/app/repositories/` (Acceso a datos):** Único lugar que interactúa con `db.session` y consultas SQLAlchemy (`select`, `has_overlap`, `count_active_by_guest`), sin reglas de negocio. *Por qué:* evita consultas duplicadas y concentra los cambios de persistencia en un solo lugar.
- **`backend/app/models/` (Modelos):** Define las entidades SQLAlchemy y su mapeo a tablas sin conocer las capas superiores. *Por qué:* mantiene las entidades limpias y respetando la dirección única de dependencias.
- **`backend/app/views/` (Serialización):** Convierte modelos a diccionarios JSON. *Por qué:* se conservó intacta para garantizar compatibilidad total con el frontend existente.
- **`backend/app/errors.py` y `backend/app/__init__.py`:** Definen las excepciones de dominio y la raíz de composición (`create_app()`), donde se cablean repositorios y servicios y se registra `@app.errorhandler(AppError)`. *Por qué:* evita instanciar repositorios dentro de las rutas y unifica el formato de respuestas de error.

### 6. Patrones de Diseño
- **Service Layer (`app/services/`):**
  - *Por qué se eligió:* En el MVC original toda la lógica vivía en los controladores. Centralizar los casos de uso en servicios evita duplicación de reglas y desacopla el negocio de Flask.
- **Repository (`app/repositories/`):**
  - *Por qué se eligió:* Las consultas `Model.query` estaban dispersas en los controladores. Encapsularlas en repositorios con nombres de dominio (`has_overlap`, `count_active_by_guest`) aísla SQLAlchemy del resto de la aplicación.
- **Strategy (`app/services/pricing.py`):**
  - *Por qué se eligió:* El cálculo de tarifas varía según la duración de la estadía (`StandardPricing` vs. `LongStayDiscountPricing`). Separar cada política en una clase cumple con el principio Abierto/Cerrado (O de SOLID) y evita condicionales rígidos en el servicio.
- **DTO (`app/services/dto.py`):**
  - *Por qué se eligió:* Usar `@dataclass(frozen=True)` (`RoomCreateInput`, `ReservationCreateInput`, etc.) evita que los servicios reciban diccionarios crudos de Flask (`request.get_json()`), garantizando contratos de entrada explícitos e inmutables entre capas.

### 7. Reglas de Negocio
Todas las reglas se implementaron en `ReservationService` (y `pricing.py`) devolviendo `422 Unprocessable Entity` mediante `BusinessRuleError` cuando se incumplen, con su respectiva prueba en `backend/tests/test_business_rules.py`:

1. **Sin solapamiento de reservas:** Rechaza reservas si la habitación ya tiene otra reserva activa (`confirmed` o `checked_in`) en fechas superpuestas. *Por qué:* evita la sobreventa de habitaciones; la consulta de solapamiento se delegó a `ReservationRepository.has_overlap` para mantener el servicio libre de SQL.
2. **Salida posterior al ingreso:** Exige `check_out > check_in`. *Por qué:* impide reservas de cero o negativas noches y totales negativos.
3. **Ingreso no en el pasado:** Exige `check_in >= date.today()`. *Por qué:* bloquea el registro retroactivo de reservas por error del recepcionista.
4. **Capacidad máxima de la habitación:** Exige `1 <= guests_count <= room.capacity`. *Por qué:* garantiza que no se asignen más huéspedes de los que soporta la habitación.
5. **Habitación disponible:** Rechaza reservas sobre habitaciones en estado `maintenance`. *Por qué:* evita vender habitaciones fuera de servicio.
6. **Descuento por estadía larga (7+ noches):** Aplica 10% de descuento automático mediante `LongStayDiscountPricing`. *Por qué:* elimina cálculos manuales y discrepancias usando el patrón Strategy.
7. **Penalidad por cancelación tardía:** Si se cancela con menos de 48 horas de anticipación (`(check_in - hoy).days < 2`), cobra la primera noche; con 48 horas o más, el total pasa a `0`. *Por qué:* automatiza la política comercial de cancelaciones en `calculate_cancellation_total`.
8. **Transiciones de estado válidas:** Solo permite `confirmed -> checked_in`, `confirmed -> cancelled` y `checked_in -> checked_out` mediante `ALLOWED_TRANSITIONS`. *Por qué:* evita estados inconsistentes como hacer check-out sin check-in o reactivar una reserva cancelada.
9. **Check-in no anticipado:** Impide hacer check-in antes de la fecha `check_in` de la reserva. *Por qué:* asegura coherencia entre la fecha contratada y el ingreso efectivo.
10. **Límite de reservas activas por huésped:** Impide que un huésped tenga más de 3 reservas activas simultáneas (`confirmed` o `checked_in`), apoyándose en `ReservationRepository.count_active_by_guest`. *Por qué:* frena el acaparamiento y reventa de habitaciones.

## Frontend: capa de API y BEM

**Capa de API (`src/api.js`).** Es el único archivo que usa `fetch`. Centraliza la URL base (mismo host de la página, puerto 8000), los headers (`Content-Type: application/json`) y el manejo de errores: como `fetch` no rechaza en 4xx/5xx, siempre se revisa `res.ok`, se lee el JSON de error y se lanza un `ApiError` con el mensaje del campo `error` de la API y el `status` HTTP. Si la respuesta es 204 devuelve `null`. Expone una función por operación (`listRooms()`, `createReservation(data)`, `cancelReservation(id)`, `checkInReservation(id)`, etc.). El resto del JavaScript no conoce URLs ni métodos HTTP.

**Metodología BEM.** Las clases siguen `bloque__elemento--modificador`:

- Todos los selectores CSS son de una sola clase (ej. `.tabs__item--active`, `.card__title`); no hay estilos por `#id`, por etiqueta ni selectores anidados.
- Los modificadores siempre acompañan a la clase base (`class="badge badge--cancelled"`).
- Los bloques no llevan márgenes externos: el espaciado entre vecinos lo define el contenedor mediante un *mix* (`class="card page__item"`).
- JavaScript refleja el estado con `classList.toggle("tabs__item--active", ...)` y se engancha al HTML con atributos `data-*` (`data-js`, `data-action`, `data-id`, `data-tab`), nunca con clases de estilo.
- Todo dato dinámico se renderiza con `textContent`, sin `innerHTML`, para evitar XSS.

**CSS separado.** Hay un solo `index.html`. El CSS se divide en `src/base/base.css` (variables, reset, tipografía) y un archivo por bloque en `src/blocks/<bloque>/<bloque>.css`; todos se enlazan desde `index.html`, primero la base y luego los bloques. Los bloques con lógica (`tabs`, `alert`, `badge`, `button`, `table`) tienen además su `.js` en la misma carpeta. Las pantallas (`rooms`, `guests`, `reservations`) viven en `src/features/` porque no son bloques BEM, sino consumidoras de bloques.

**Reglas de negocio en la UI.** Los errores 422 del backend (`{ "error": "..." }`) se muestran en una alerta roja con el mensaje exacto de la API. El total de cada reserva se muestra tal como lo devuelve la API, ya con el descuento del 10 % (7 o más noches) o la penalidad de cancelación tardía (menos de 48 h) aplicados; el frontend no recalcula nada.

El frontend usa módulos ES (`<script type="module">`), por lo que debe abrirse desde el servidor (Docker Compose), no con doble clic sobre `index.html`. No se agregó ningún framework ni librería nueva.

## Decisiones del frontend: qué propuso cada quien

El refactor del frontend se hizo con asistencia de una IA (Claude, de Anthropic). El estudiante definió los requisitos, el estándar y las correcciones; la IA propuso el código y el estudiante lo revisó, lo probó en el navegador y decidió qué conservar.

### Quién aportó qué

| Quién | Aportó |
|-------|--------|
| **Estudiante** | Requisitos del examen y el estándar BEM de la clase (nomenclatura, selectores planos, prohibiciones). La estructura de clase `src/blocks/<bloque>/` (un bloque, una carpeta). La corrección de la primera propuesta de la IA. La pregunta sobre si `src/` era necesaria y la decisión de mantenerla. La revisión de `Dockerfile` y `docker-compose.yml`. El orden de commits, las pruebas en el navegador y la validación final. |
| **IA** | Código de `api.js` y `ApiError`. Clases BEM del HTML y CSS de cada bloque. Los helpers JS (`utils.js`, `badge.js`, `button.js`, `table.js`, `alert.js`, `tabs.js`). Las pantallas en `features/`. La delegación de eventos y los ganchos `data-*`. La verificación de que Docker no necesitaba cambios. El orden de commits sugerido. |

### Lo que se quedó

| Decisión | Propuesta de | Por qué se quedó |
|----------|--------------|------------------|
| `api.js` como única capa con `fetch`, con `ApiError`, revisión de `res.ok` y `null` en 204 | Estudiante (requisito) / IA (código) | `fetch` no rechaza en 4xx/5xx. Así el mensaje 422 de las reglas llega intacto a la pantalla y el resto del código no conoce URLs. |
| Nomenclatura BEM con selectores de una sola clase | Estudiante (estándar) / IA (aplicación) | Misma especificidad, sin colisiones ni parches con selectores largos. |
| Un bloque, una carpeta: `src/blocks/<bloque>/<bloque>.css` y `.js` si tiene lógica | Estudiante | Es el estándar de la clase. Para borrar un componente se borra una carpeta y no queda CSS huérfano. |
| `base.css` con variables, reset y tipografía | Examen | Un solo lugar para colores y `box-sizing`. Los bloques usan `var(--...)`. |
| Mixes `page__item` y `page__alert` para el espaciado | IA (por el estándar) | Un bloque no lleva márgenes externos: la distancia con los vecinos la decide el contenedor. |
| Atributos `data-*` (`data-js`, `data-action`, `data-id`, `data-tab`) como ganchos de JS | IA (por el estándar) | Un cambio de estilos no rompe la lógica. Separa lo que se ve de lo que JS necesita encontrar. |
| Delegación de eventos en los `<tbody>` | IA | Reemplaza los `onclick` en línea. Un solo listener funciona aunque la tabla se redibuje. |
| `textContent` y `createElement` en lugar de `innerHTML` | Estándar BEM de la clase / IA | El original usaba `innerHTML` con una función de escape. Así se evita XSS. |
| Carpeta `features/` para rooms, guests y reservations | IA | Las pantallas no son bloques BEM: son consumidoras de bloques. |
| `main.js` y `utils.js` | IA | Punto de entrada único y helpers compartidos sin duplicar código. |
| `<script type="module">` | IA | Permite `import`/`export` sin bundler y funciona con el servidor estático de Python. |
| Mostrar el total tal como lo devuelve la API | Examen | La API decide. El frontend no recalcula el descuento ni la penalidad. |
| Mantener la carpeta `src/` | IA (recomendación) / Estudiante (decisión) | No es técnicamente necesaria, pero alinea con la estructura de la clase y separa el código de la configuración. |

### Lo que se descartó

| Descartado | Propuesto por | Por qué se descartó |
|------------|---------------|---------------------|
| Carpeta `css/` plana con todos los bloques juntos y `js/app.js` monolítico | IA (primera versión) | Lo rechazó el estudiante: cumplía "un CSS por bloque" del examen, pero contradecía el estándar de clase (bloque = carpeta). Se rehízo con `src/blocks/`. |
| Un `.html` por bloque (como en el ejemplo `todo-card.html`) | Ejemplo de clase | El examen exige un solo `index.html`. El marcado se queda ahí. |
| Carpeta por elemento y por modificador de la versión original de BEM | BEM original | Para este proyecto una carpeta por bloque alcanza, como indica la clase. |
| `onclick="..."` en línea, `getElementById` y selectores por etiqueta (`.tabs button.active`) | Código original | Los ids y las etiquetas atan JS y CSS al marcado. BEM y los `data-*` lo evitan. |
| `innerHTML` con la función `esc()` | Código original | Se reemplazó por `textContent`, que no interpreta HTML. |
| Frameworks o bundler (Vite, React) | No propuesto | El examen los prohíbe. Todo funciona con HTML, CSS y JS puros. |
| Recalcular descuento y penalidad en el frontend | No propuesto | Duplicaría reglas de negocio. Quien decide es el backend. |
| Cambiar `Dockerfile` y `docker-compose.yml` | IA (condicional) | No hizo falta: `COPY . .` y el montaje `./frontend:/site` ya incluyen `src/`. |
| Eliminar `src/` | Alternativa válida | Se mantuvo por alinearse con la estructura de clase. |

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/api/rooms?status=`            | lista de habitaciones |
| GET    | `/api/rooms/:id`                | una habitación |
| POST   | `/api/rooms`                    | crea `{ number, type, price_per_night, capacity }` |
| PUT    | `/api/rooms/:id`                | modifica `type`, `status`, `price_per_night` o `capacity` |
| DELETE | `/api/rooms/:id`                | elimina (409 si tiene reservas) |
| GET    | `/api/guests`                   | lista de huéspedes |
| GET    | `/api/guests/:id`               | un huésped |
| POST   | `/api/guests`                   | crea `{ full_name, email, document }` |
| DELETE | `/api/guests/:id`               | elimina (409 si tiene reservas) |
| GET    | `/api/reservations?status=&guest_id=` | lista de reservas |
| GET    | `/api/reservations/:id`         | una reserva |
| POST   | `/api/reservations`             | crea `{ room_id, guest_id, check_in, check_out, guests_count }` |
| PATCH  | `/api/reservations/:id/cancel`  | cancela |
| PATCH  | `/api/reservations/:id/check-in`  | registra el ingreso |
| PATCH  | `/api/reservations/:id/check-out` | registra la salida |

Valores válidos:

- `type`: `single`, `double`, `family`, `suite`.
- `status` de habitación: `available`, `maintenance`.
- `status` de reserva: `confirmed`, `checked_in`, `checked_out`, `cancelled`.
- Fechas en formato `AAAA-MM-DD`; precios en bolivianos.

Los errores se devuelven como `{ "error": "mensaje" }` con el código HTTP correspondiente (422 cuando se incumple una regla de negocio; ver `REGLAS.md`).
