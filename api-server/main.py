"""
main.py — AutoCommerce V25 Entry Point
=======================================
FastAPI app with:
  - Multi-tenant JWT middleware
  - Alembic auto-migrations on startup (CLI-only in production)
  - Sentry error tracking
  - Structured JSON logging (structlog)
  - CORS with explicit origins (no wildcard in production)
  - Enterprise Security: SecurityHeaders, AuditLog, InputValidation, CSRF
  - Rate limiting via Redis (distributed, cross-worker)
  - Body size limits, trace IDs, PII redaction
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager








import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse








# ─────────────────────────────────────────────────────────────────────────────
# P0.7 FIX: payment_links_router removed from main.py — registered via api/v1/__init__.py
from api.v1 import router as api_router
from api.v1.health import router as health_router
from config import settings
from middleware.audit_log import AuditLogMiddleware
from middleware.body_limit import BodySizeLimitMiddleware
from middleware.csrf_protection import CSRFProtectionMiddleware  # P0-3 FIX: was defined but never imported
from middleware.input_validation import InputValidationMiddleware
from middleware.rate_limit import RateLimitExceeded, SlowAPIMiddleware, _rate_limit_exceeded_handler, limiter








# ── Enterprise Security Middlewares (v18) ─────────────────────────────────────
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.tenant import TenantMiddleware
from middleware.trace_id import TraceIDMiddleware
from models.database import engine
from preflight_secrets import check_secrets as _preflight_check_secrets








# ─── Logging ──────────────────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
