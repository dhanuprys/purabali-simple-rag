"""
Pydantic schemas for chat and AI-related models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    """Request model for chat prompt."""
    
    message: str = Field(..., description="User message", min_length=1, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Beritahu saya tentang Pura Tanah Lot"
            }
        }


class PuraAttachment(BaseModel):
    """Pura attachment for chat responses."""
    
    id_pura: str = Field(..., description="Pura ID")
    nama_pura: str = Field(..., description="Pura name")
    jenis_pura: str = Field(..., description="Temple type")
    kabupaten: str = Field(..., description="Regency name")
    deskripsi: str = Field(..., description="Description")
    link_lokasi: Optional[str] = Field(None, description="Location link")
    link_gambar: Optional[str] = Field(None, description="Image link")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_pura": "P001",
                "nama_pura": "Pura Tanah Lot",
                "jenis_pura": "Kahyangan Jagat",
                "kabupaten": "Tabanan",
                "deskripsi": "Pura Tanah Lot adalah pura yang terletak di atas batu karang...",
                "link_lokasi": "https://maps.google.com/...",
                "link_gambar": "https://example.com/image.jpg"
            }
        }


class PromptResponse(BaseModel):
    """Response model for chat prompt."""
    
    answer: str = Field(..., description="AI generated answer")
    attachments: List[PuraAttachment] = Field(
        default_factory=list, 
        description="Related pura attachments"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Pura Tanah Lot adalah salah satu pura paling terkenal di Bali...",
                "attachments": [
                    {
                        "id_pura": "P001",
                        "nama_pura": "Pura Tanah Lot",
                        "jenis_pura": "Kahyangan Jagat",
                        "kabupaten": "Tabanan",
                        "deskripsi": "Pura Tanah Lot adalah pura yang terletak di atas batu karang...",
                        "link_lokasi": "https://maps.google.com/...",
                        "link_gambar": "https://example.com/image.jpg"
                    }
                ]
            }
        } 