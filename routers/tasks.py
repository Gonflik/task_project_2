from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.task import Task, TaskStatus
from schemas import TaskUpdate, TaskOut, TaskCreate
from limiter import limiter
from mails import send_completion_email

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=list[TaskOut])
@limiter.limit("10/minute")
async def get_tasks(
    request: Request,
    status: TaskStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=5, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Task)

    if status:
        stmt = stmt.where(Task.status==status)
    
    offset = (page - 1) * per_page
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.scalars(stmt)
    return result.all()

@router.get("/{task_id}", response_model=TaskOut)
@limiter.limit("10/minute")
async def get_single_task(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id==task_id)
    result = await db.scalar(stmt)
    if not result:
        raise HTTPException(status_code=404, detail=f"Task with id:{task_id} not found!")
    return result


@router.post("/", response_model=TaskOut, status_code=201)
@limiter.limit("10/minute")
async def create_task(request: Request, payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.patch("/{task_id}", response_model=TaskOut, status_code=200)
@limiter.limit("10/minute")
async def partial_update_task(request: Request, payload: TaskUpdate, task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id==task_id)
    task = await db.scalar(stmt)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id:{task_id} not found!")
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task

@router.patch("/{task_id}/completed", response_model=TaskOut)
@limiter.limit("10/minute")
async def status_update_task(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id==task_id)
    task = await db.scalar(stmt)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id:{task_id} not found!")
    
    task.status = TaskStatus.COMPLETED
    await db.commit()
    await db.refresh(task)
    await send_completion_email(task.email, task.title)
    return task

@router.delete("/{task_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_task(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.id==task_id)
    task = await db.scalar(stmt)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id:{task_id} not found!")
    
    await db.delete(task)
    await db.commit()


