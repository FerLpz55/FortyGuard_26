---
name: papamike
description: >-
  Utiliza este skill cuando trabajes en el backend de OmniTherm o requieras programar
  código en Python con FastAPI. Aplica estrictamente patrones de Clean Architecture, 
  principios SOLID, y guías de seguridad de OWASP Top 10.
---

# 🕵️‍♂️ PapaMike Backend Development Protocol

¡Saludos! Estás asumiendo el protocolo **PapaMike**, diseñado para asegurar la más alta calidad y seguridad en el desarrollo del backend de OmniTherm (FastAPI/PostgreSQL).

Tu responsabilidad es actuar bajo los siguientes principios inquebrantables. Lee y aplica estas reglas en cada modificación del código base:

## 1. Arquitectura Limpia (Clean Architecture)
- **Separación por Capas**: El código DEBE dividirse estrictamente en:
  - `routers` (o endpoints `/api/v1/`): Únicamente reciben peticiones, manejan inyección de dependencias (`Depends`) y devuelven respuestas HTTP. Nunca tienen lógica de negocio.
  - `services/`: Contienen toda la lógica de negocio. Orquestan los repositorios.
  - `repositories/`: Contienen toda la lógica de acceso a datos (SQLAlchemy). No devuelven diccionarios, devuelven modelos u objetos mapeados.
  - `models/`: Definición de tablas de SQLAlchemy.
  - `schemas/`: Pydantic models para validación de entrada/salida.
- **Evitar Dependencias Circulares**: Mantén un árbol de dependencias unidireccional (Routers -> Services -> Repositories -> Models).

## 2. Principios SOLID
- **S**ingle Responsibility: Cada clase, función y archivo debe tener una sola razón para cambiar.
- **D**ependency Inversion: (Especialmente en FastAPI). Inyecta la sesión de base de datos (`AsyncSession`) desde el router hacia el servicio, y del servicio al repositorio. Nunca inicialices conexiones de BD dentro de la lógica de negocio.

## 3. Seguridad Estricta (OWASP Top 10)
- **A01: Broken Access Control**: Usa siempre `Depends(get_current_user)` para proteger endpoints. Valida propiedad de recursos (ej: `Site.user_id == user.id`).
- **A02: Cryptographic Failures**: Hashea siempre las contraseñas con algoritmos fuertes (ej. `bcrypt` nativo, no uses `passlib` obsoleto). Nunca expongas hashes o tokens en logs o en las respuestas de la API. Mantén los secretos y claves en variables de entorno (respaldadas por un `.env.example`).
- **A03: Injection**: Usa el ORM (SQLAlchemy) en todo momento (con sentencias `select`, `where`). Nunca concatenes strings para consultas SQL.

## 4. Infraestructura & Entorno (Vercel / Docker)
- El entorno usa PostgreSQL (probablemente vía **Supabase** en producción).
- Soporta configuración *Serverless* usando `NullPool` en la conexión SQLAlchemy si `ENVIRONMENT` es `production` o `vercel`, evitando agotar el Connection Pooler externo (PgBouncer).
- Todo cambio de esquema requiere la generación de una migración con **Alembic**. No crees tablas usando `.metadata.create_all()`.

## 5. Pruebas y TDD
- Antes de dar por finalizada una tarea grande, debes asegurar la ejecución de un *Smoke Test* integral (ej. usar scripts como `test_smoke.py` o `run_all.sh` que levante el entorno, corra migraciones, simule la API y luego la derribe).

## Tu Forma de Actuar
- Responde de forma técnica, precisa y proactiva. Si te encuentras con errores 500, lee el Stack Trace, ubica el problema en la separación de capas o en la base de datos, repáralo, e inténtalo de nuevo hasta lograr que compile y funcione al 100%. 
- No crees archivos duplicados; revisa la estructura existente antes de proponer nuevos archivos.
