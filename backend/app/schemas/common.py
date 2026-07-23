"""Schemas shared across endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    environment: str = Field(examples=["development"])


class VersionResponse(BaseModel):
    name: str = Field(examples=["FlowMind"])
    version: str = Field(examples=["0.1.0"])
    api_prefix: str = Field(examples=["/api/v1"])


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
