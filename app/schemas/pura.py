"""
Pydantic schemas for Pura (temple) related models.
"""

from typing import Optional, List
from pydantic import BaseModel, Field

from .common import PaginationResponse


class PuraResponse(BaseModel):
    """Basic Pura response model."""
    
    id_pura: str = Field(..., description="Pura ID")
    nama_pura: str = Field(..., description="Pura name")
    deskripsi_singkat: Optional[str] = Field(None, description="Short description")
    tahun_berdiri: Optional[str] = Field(None, description="Year established")
    link_lokasi: Optional[str] = Field(None, description="Location link")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    link_gambar: Optional[str] = Field(None, description="Image link")
    nama_jenis_pura: Optional[str] = Field(None, description="Temple type name")
    nama_kabupaten: Optional[str] = Field(None, description="Regency name")
    
    class Config:
        from_attributes = True


class PuraListResponse(BaseModel):
    """Response model for pura list with pagination."""
    
    data: List[PuraResponse] = Field(..., description="List of pura")
    pagination: PaginationResponse = Field(..., description="Pagination metadata")


class PuraDetailResponse(BaseModel):
    """Response model for single pura detail."""
    
    data: PuraResponse = Field(..., description="Pura details")


class KabupatenResponse(BaseModel):
    """Kabupaten (regency) response model."""
    
    id_kabupaten: str = Field(..., description="Kabupaten ID")
    nama_kabupaten: str = Field(..., description="Kabupaten name")
    pura_count: int = Field(..., description="Number of pura in this kabupaten")
    
    class Config:
        from_attributes = True


class JenisPuraResponse(BaseModel):
    """Jenis Pura (temple type) response model."""
    
    id_jenis_pura: str = Field(..., description="Jenis Pura ID")
    nama_jenis_pura: str = Field(..., description="Jenis Pura name")
    pura_count: int = Field(..., description="Number of pura of this type")
    
    class Config:
        from_attributes = True 