"""
Dashboard Schemas

Pydantic models for dashboard-related responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class MissionMapItem(BaseModel):
    """Mission location data for map visualization."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    location: Optional[Dict[str, Any]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interested: int = 0
    heared: int = 0
    saved: int = 0
    total_expenses: float = 0.0


class OutreachSummary(BaseModel):
    """Aggregated outreach statistics."""
    total_interested: int = 0
    total_heared: int = 0
    total_saved: int = 0
    total_contacts: int = 0


class ExpenseSummary(BaseModel):
    """Aggregated expense statistics."""
    total_amount: float = 0.0
    total_budget: float = 0.0
    budget_utilization: float = 0.0
    by_category: Dict[str, float] = {}


class DashboardStats(BaseModel):
    """Aggregated dashboard statistics."""
    model_config = ConfigDict(from_attributes=True)
    
    total_missions: int = 0
    active_missions: int = 0
    total_evangelists: int = 0
    outreach: OutreachSummary = OutreachSummary()
    expenses: ExpenseSummary = ExpenseSummary()


class DashboardMapResponse(BaseModel):
    """Map data response with mission locations."""
    model_config = ConfigDict(from_attributes=True)
    
    missions: List[MissionMapItem] = []


class DashboardSummaryResponse(BaseModel):
    """Combined dashboard summary with stats and map data."""
    model_config = ConfigDict(from_attributes=True)
    
    stats: DashboardStats
    missions: List[MissionMapItem] = []
