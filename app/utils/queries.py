from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.exceptions import CustomException


async def get_or_404(db: AsyncSession, model, **kwargs):
    conditions = [getattr(model, key) == value for key, value in kwargs.items()]
    query = select(model).where(and_(*conditions))
    result = await db.execute(query)
    data = result.scalars().first()
    if data is None:
        raise HTTPException(status_code=400, detail="Data not found")
    return data


async def get_one_object(db, model, **kwargs):
    conditions = [getattr(model, key) == value for key, value in kwargs.items()]
    query = select(model).where(and_(*conditions))
    result = await db.execute(query)
    return result.scalars().first()


async def get_objects(db, model, **kwargs):
    conditions = [getattr(model, key) == value for key, value in kwargs.items()]
    query = select(model).where(and_(*conditions))
    result = await db.execute(query)
    return result.scalars().all()


async def fetch_query(db: AsyncSession, query):
    try:
        # Execute the query
        result = await db.execute(query)

        # Use scalars() to get an iterator for scalar results (e.g., one column from each row)
        return result.scalars().all()  # Fetch all results as a list

    except NoResultFound:
        # Handle case where no results are found and you expect exactly one
        return None

    except MultipleResultsFound:
        # Handle case where multiple results are found when exactly one is expected
        raise ValueError("Multiple results found when only one was expected.")

    except Exception as e:
        # Handle other exceptions such as database errors
        raise e

