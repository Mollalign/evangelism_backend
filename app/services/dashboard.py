"""
Dashboard Service

Business logic for dashboard data aggregation.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.mission import Mission
from app.models.outreach import OutreachData, OutreachNumbers
from app.models.expense import Expense
from app.models.mission_user import MissionUser
from app.repositories.mission import MissionRepository
from app.schemas.dashboard import (
    DashboardStats,
    DashboardMapResponse,
    DashboardSummaryResponse,
    MissionMapItem,
    OutreachSummary,
    ExpenseSummary
)


class DashboardService:
    """Service for dashboard data operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mission_repo = MissionRepository(db)
    
    async def get_dashboard_stats(self, account_id: str) -> DashboardStats:
        """Get aggregated dashboard statistics for an account."""
        account_uuid = UUID(account_id)
        
        # Count total and active missions
        total_missions_query = select(func.count(Mission.id)).where(
            Mission.account_id == account_uuid,
            Mission.deleted_at.is_(None)
        )
        total_missions_result = await self.db.execute(total_missions_query)
        total_missions = total_missions_result.scalar() or 0
        
        # Active missions (started and not ended)
        now = datetime.now(timezone.utc)
        active_missions_query = select(func.count(Mission.id)).where(
            Mission.account_id == account_uuid,
            Mission.deleted_at.is_(None),
            Mission.start_date <= now,
            (Mission.end_date.is_(None) | (Mission.end_date >= now))
        )
        active_missions_result = await self.db.execute(active_missions_query)
        active_missions = active_missions_result.scalar() or 0
        
        # Count evangelists (users assigned to missions)
        evangelists_query = select(func.count(func.distinct(MissionUser.user_id))).join(
            Mission, MissionUser.mission_id == Mission.id
        ).where(
            Mission.account_id == account_uuid,
            Mission.deleted_at.is_(None)
        )
        evangelists_result = await self.db.execute(evangelists_query)
        total_evangelists = evangelists_result.scalar() or 0
        
        # Aggregate outreach numbers
        outreach_query = select(
            func.coalesce(func.sum(OutreachNumbers.interested), 0).label('interested'),
            func.coalesce(func.sum(OutreachNumbers.heared), 0).label('heared'),
            func.coalesce(func.sum(OutreachNumbers.saved), 0).label('saved')
        ).where(
            OutreachNumbers.account_id == account_uuid,
            OutreachNumbers.deleted_at.is_(None)
        )
        outreach_result = await self.db.execute(outreach_query)
        outreach_row = outreach_result.one()
        
        # Count total contacts from outreach data
        contacts_query = select(func.count(OutreachData.id)).where(
            OutreachData.account_id == account_uuid,
            OutreachData.deleted_at.is_(None)
        )
        contacts_result = await self.db.execute(contacts_query)
        total_contacts = contacts_result.scalar() or 0
        
        outreach_summary = OutreachSummary(
            total_interested=int(outreach_row.interested),
            total_heared=int(outreach_row.heared),
            total_saved=int(outreach_row.saved),
            total_contacts=total_contacts
        )
        
        # Aggregate expenses
        expense_query = select(
            func.coalesce(func.sum(Expense.amount), 0).label('total')
        ).where(
            Expense.account_id == account_uuid,
            Expense.deleted_at.is_(None)
        )
        expense_result = await self.db.execute(expense_query)
        total_expenses = float(expense_result.scalar() or 0)
        
        # Get total budget from missions
        budget_query = select(
            func.coalesce(func.sum(Mission.budget), 0)
        ).where(
            Mission.account_id == account_uuid,
            Mission.deleted_at.is_(None)
        )
        budget_result = await self.db.execute(budget_query)
        total_budget = float(budget_result.scalar() or 0)
        
        # Budget utilization
        budget_utilization = (total_expenses / total_budget * 100) if total_budget > 0 else 0
        
        # Expenses by category
        category_query = select(
            Expense.category,
            func.sum(Expense.amount).label('amount')
        ).where(
            Expense.account_id == account_uuid,
            Expense.deleted_at.is_(None)
        ).group_by(Expense.category)
        category_result = await self.db.execute(category_query)
        by_category = {row.category: float(row.amount) for row in category_result.all()}
        
        expense_summary = ExpenseSummary(
            total_amount=total_expenses,
            total_budget=total_budget,
            budget_utilization=round(budget_utilization, 2),
            by_category=by_category
        )
        
        return DashboardStats(
            total_missions=total_missions,
            active_missions=active_missions,
            total_evangelists=total_evangelists,
            outreach=outreach_summary,
            expenses=expense_summary
        )
    
    async def get_map_data(self, account_id: str) -> DashboardMapResponse:
        """Get mission locations for map visualization."""
        account_uuid = UUID(account_id)
        
        # Get missions with their outreach numbers and expenses
        missions_query = select(Mission).options(
            selectinload(Mission.outreach_numbers),
            selectinload(Mission.expenses)
        ).where(
            Mission.account_id == account_uuid,
            Mission.deleted_at.is_(None),
            Mission.location.isnot(None)
        ).order_by(Mission.created_at.desc())
        
        result = await self.db.execute(missions_query)
        missions = result.scalars().all()
        
        map_items = []
        for mission in missions:
            # Calculate totals from outreach numbers
            interested = 0
            heared = 0
            saved = 0
            if mission.outreach_numbers:
                interested = mission.outreach_numbers.interested or 0
                heared = mission.outreach_numbers.heared or 0
                saved = mission.outreach_numbers.saved or 0
            
            # Sum expenses
            total_expenses = sum(
                e.amount for e in mission.expenses if e.deleted_at is None
            )
            
            map_items.append(MissionMapItem(
                id=str(mission.id),
                name=mission.name,
                location=mission.location,
                start_date=mission.start_date.isoformat() if mission.start_date else None,
                end_date=mission.end_date.isoformat() if mission.end_date else None,
                interested=interested,
                heared=heared,
                saved=saved,
                total_expenses=total_expenses
            ))
        
        return DashboardMapResponse(missions=map_items)
    
    async def get_dashboard_summary(self, account_id: str) -> DashboardSummaryResponse:
        """Get combined dashboard summary with stats and map data."""
        stats = await self.get_dashboard_stats(account_id)
        map_data = await self.get_map_data(account_id)
        
        return DashboardSummaryResponse(
            stats=stats,
            missions=map_data.missions
        )
