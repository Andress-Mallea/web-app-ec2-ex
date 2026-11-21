# Reglas de Negocio · Hotel Mirador

1. **Sin solapamiento de reservas**
   - **Regla:** Al crear una reserva (`POST /api/reservations`), la habitación seleccionada no puede tener otra reserva activa (`confirmed` o `checked_in`) cuyas fechas se superpongan con el rango solicitado (`check_in_existente < check_out_nuevo` y `check_out_existente > check_in_nuevo`).
   - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "La habitación ya tiene una reserva activa en las fechas seleccionadas"}`.

2. **Salida posterior al ingreso**
   - **Regla:** Al crear una reserva (`POST /api/reservations`), la fecha de salida (`check_out`) debe ser estrictamente posterior a la fecha de ingreso (`check_in`), garantizando al menos una noche de estadía.
   - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "La fecha de salida debe ser posterior a la fecha de ingreso"}`.

3. **Ingreso no en el pasado**
   - **Regla:** Al crear una reserva (`POST /api/reservations`), la fecha de ingreso (`check_in`) debe ser igual o posterior a la fecha actual del sistema.
   - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "La fecha de ingreso no puede ser anterior a hoy"}`.

4. **Capacidad máxima de la habitación**
   - **Regla:** Al crear una reserva (`POST /api/reservations`), la cantidad de huéspedes (`guests_count`) debe ser al menos 1 y no puede superar la capacidad (`capacity`) de la habitación elegida.
   - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "La cantidad de huéspedes debe estar entre 1 y la capacidad de la habitación (<capacity>)"}`.

5. **Habitación disponible**
   - **Regla:** Al crear una reserva (`POST /api/reservations`), la habitación debe encontrarse en estado `available`; no se permiten reservas sobre habitaciones en estado `maintenance`.
   - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "La habitación está en mantenimiento y no puede reservarse"}`.

6. **Descuento por estadía larga (7 noches o más)**
   - **Regla:** Al crear una reserva (`POST /api/reservations`), si la duración es de 7 noches o más (`(check_out - check_in).days >= 7`), el sistema aplica automáticamente un 10% de descuento sobre el total base (`noches * price_per_night * 0.90`).
   - **Respuesta de la API:** Regla de cálculo automático; responde `201 Created` con el campo `total_price` ya reflejando el 10% de descuento.

7. **Penalidad por cancelación tardía**
   - **Regla:** Al cancelar una reserva (`PATCH /api/reservations/<id>/cancel`), si faltan menos de 48 horas para el ingreso (`(check_in - hoy).days < 2`), se cobra la primera noche (`total_price = room.price_per_night`); si se cancela con 48 horas o más de anticipación, no se cobra nada (`total_price = 0`).
   - **Respuesta de la API:** Regla de cálculo automático; responde `200 OK` con el estado `cancelled` y el `total_price` actualizado según corresponda.

8. **Transiciones de estado válidas**
   - **Regla:** Al cambiar el estado de una reserva (`check-in`, `check-out` o `cancel`), solo se permiten las transiciones `confirmed -> checked_in`, `confirmed -> cancelled` y `checked_in -> checked_out`; cualquier otra transición (como hacer `check-out` sin `check-in` o `check-in` sobre una reserva cancelada) queda prohibida.
   - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "No se puede realizar '<acción>' en una reserva con estado '<estado>'"}`.

9. **Check-in no anticipado**
   - **Regla:** Al registrar un check-in (`PATCH /api/reservations/<id>/check-in`), la fecha actual del sistema debe ser igual o posterior a la fecha de ingreso (`check_in`) registrada en la reserva.
   - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "No se puede hacer check-in antes de la fecha de ingreso (<check_in>)"}`.

10. **Límite de reservas activas por huésped**
    - **Regla:** Al crear una reserva (`POST /api/reservations`), el huésped no puede tener ya 3 o más reservas activas simultáneamente (en estado `confirmed` o `checked_in`).
    - **Respuesta de la API:** `422 Unprocessable Entity` con `{"error": "El huésped ya alcanzó el límite de 3 reservas activas simultáneas"}`.