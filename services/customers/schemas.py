from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CrearClienteRequest(BaseModel):
    usuario_id: Optional[str] = None
    nombre_completo: str = Field(min_length=3)
    email: EmailStr
    telefono: str = Field(pattern=r'^\+?[0-9]{10,15}$')
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None


class ClienteResponse(BaseModel):
    cliente_id: str
    nombre_completo: str
    email: str
    telefono: str
    ciudad: Optional[str]
    pais: Optional[str]
    creado_en: datetime
