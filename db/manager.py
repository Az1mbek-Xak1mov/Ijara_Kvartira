from sqlalchemy import select, insert, delete, update
from sqlalchemy.orm import Session, sessionmaker

from db.engine import engine
from db.models import Apartment, Owner, Renter, LikedListing

session = sessionmaker(engine)()


async def save(model, values):
    query_insert = insert(model).values(**values)
    session.execute(query_insert)
    session.commit()


async def save_liked(model, values, filter_by_keys=None):
    if filter_by_keys:
        filters = {key: values[key] for key in filter_by_keys}
        exists = session.execute(
            select(model).filter_by(**filters)
        ).first()
        if exists:
            return

    query_insert = insert(model).values(**values)
    session.execute(query_insert)
    session.commit()


async def select_one(model, filter_value):
    query_select = select(model).filter(model.chat_id == filter_value)
    result = session.execute(query_select)
    return result.scalars().first()

async def select_one_apart(model, filter_value):
    query_select = select(model).filter(model.id == filter_value)
    result = session.execute(query_select)
    return result.scalars().first()

async def delete_record(model, filter_value):
    with Session(engine) as session:
        if model == Apartment:
            query_delete = delete(model).filter(
                model.owner_id == select(Owner.id).where(Owner.chat_id == filter_value).scalar_subquery()
            )
        else:
            query_delete = delete(model).filter(model.chat_id == filter_value)

        session.execute(query_delete)
        session.commit()

async def update_record(model, id, new_value):
    with Session(engine) as session:
        query_update = (
            update(model)
            .where(model.chat_id == id)
            .values(phone_number=new_value)
        )
        session.execute(query_update)
        session.commit()


async def get_last_apartment_by_owner_chat_id(chat_id):
    query = (
        select(Apartment)
        .join(Owner, Owner.chat_id == Apartment.owner_id)
        .filter(Owner.chat_id == chat_id)
        .order_by(Apartment.id.desc())
        .limit(1)
    )
    result = session.execute(query)
    return result.scalars().first()
