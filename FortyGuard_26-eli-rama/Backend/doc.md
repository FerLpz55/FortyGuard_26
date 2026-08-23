# Guía de Endpoints API - OmniTherm (Backend)

Esta es la guía rápida de los endpoints disponibles en el backend de OmniTherm (construidos con FastAPI y PostgreSQL). Todos los endpoints base inician bajo el prefijo `/api/v1`.

## 1. Autenticación (`/auth`)
*   `POST /api/v1/auth/register`: Registra un nuevo usuario en la plataforma.
*   `POST /api/v1/auth/login`: Inicia sesión y devuelve un token JWT `access_token` y `refresh_token`.
*   `GET /api/v1/auth/me`: Retorna los detalles del usuario actualmente autenticado (requiere JWT).
*   `POST /api/v1/auth/refresh`: Renueva el token de acceso usando el `refresh_token`.

## 2. Gestión de Sitios (`/sites`)
*   `POST /api/v1/sites`: Crea un nuevo sitio (bodega, centro de datos, etc.).
*   `GET /api/v1/sites`: Lista todos los sitios asociados al usuario autenticado.
*   `GET /api/v1/sites/{site_id}`: Retorna los detalles de un sitio específico.
*   `PATCH /api/v1/sites/{site_id}`: Actualiza la información de un sitio.
*   `DELETE /api/v1/sites/{site_id}`: Elimina un sitio (soft delete o hard delete según configuración).

## 3. Temperatura e Históricos (`/sites/{site_id}/temperature`) - *En desarrollo*
*(Nota: Actualmente retornan HTTP 500/501 ya que dependen de la integración final con FortyGuard en fases posteriores).*
*   `GET /api/v1/sites/{site_id}/temperature/latest`: Obtiene la última lectura registrada de un sitio.
*   `GET /api/v1/sites/{site_id}/temperature/history`: Retorna el historial de temperaturas en un rango de fechas.
*   `GET /api/v1/sites/{site_id}/temperature/stats`: Devuelve las estadísticas de temperatura (min, max, avg).

## 4. Consumo Energético (`/sites/{site_id}/energy`)
*   `POST /api/v1/sites/{site_id}/energy`: Registra el consumo energético manual o por API de un sitio.
*   `GET /api/v1/sites/{site_id}/energy/history`: Retorna el historial de consumos.

## 5. Alertas (`/sites/{site_id}/alerts` y `/alerts`)
*   `GET /api/v1/sites/{site_id}/alerts`: Lista las alertas de anomalías térmicas en un sitio.
*   `PATCH /api/v1/alerts/{alert_id}/acknowledge`: Marca una alerta como leída/reconocida.
*   `GET /api/v1/alerts/summary`: Resumen global de alertas (no leídas, críticas, etc.) por usuario.

## 6. Agente IA (`/agent`) - *En desarrollo*
*   `POST /api/v1/agent/chat`: Interactúa con el agente RAG usando Google ADK. (HTTP 501 - Not Implemented).
*   `POST /api/v1/agent/execute`: Solicita la ejecución de una acción domótica o configuración. (HTTP 501 - Not Implemented).
