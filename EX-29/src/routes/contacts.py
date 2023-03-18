from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel, ResponseContact
from src.services.auth import auth_service
from src.services.messages import NOT_FOUND, TO_MANY_REQUESTS

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/search{part_to_search}", response_model=List[ResponseContact],
            description=TO_MANY_REQUESTS,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def searcher(field: str = Path(min_length=2, max_length=20), db: Session = Depends(get_db)):
    """
    The searcher function searches for contacts in the database.
        It takes a field as an argument and returns all contacts that match the search criteria.

    :param field: str: Search for a contact in the database
    :param max_length: Limit the length of the field
    :param db: Session: Get the database session
    :return: A list of contacts
    """
    contacts = await repository_contacts.searcher(field, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return contacts


@router.get("/bday", response_model=List[ResponseContact], description=TO_MANY_REQUESTS,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def birthday_list(db: Session = Depends(get_db)):
    """
    The birthday_list function returns a list of contacts with birthdays in the current month.

    :param db: Session: Pass the database connection to the function
    :return: A list of contacts with a birthday in the next 7 days
    """
    contact = await repository_contacts.birthday_list(db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return contact


@router.post('/create', response_model=ResponseContact, status_code=status.HTTP_201_CREATED,
             description=TO_MANY_REQUESTS,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactModel object as input, which is validated by pydantic.
        The function also takes an optional db Session object and current_user User object as inputs,
            both of which are provided by dependency injection via FastAPI's Depends decorator.

    :param body: ContactModel: Get the contact data from the request body
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user
    :return: A contactmodel object
    """
    contact = await repository_contacts.create_contact(body, current_user, db)
    return contact


@router.get('/all', response_model=List[ResponseContact], description=TO_MANY_REQUESTS,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts for the current user.
        The function is called by the get_contacts endpoint, which is defined in
        main.py and mapped to /api/v{ver}/contacts.

    :param db: Session: Get the database session,
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    """
    contacts = await repository_contacts.get_contacts(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return contacts


@router.get('/{contact_id}', response_model=ResponseContact, description=TO_MANY_REQUESTS,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int = Path(1, ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by its id.

    :param contact_id: int: Specify the contact id to be returned
    :param ge: Set the minimum value of the parameter
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return contact


@router.put("/update/{contact_id}", response_model=ResponseContact, description=TO_MANY_REQUESTS,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel, contact_id: int = Path(1, ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id of the contact to be updated, and a body containing all fields that need to be updated.
        If no fields are provided, then nothing will change in the database.

    :param body: ContactModel: Pass the data from the request body to the function
    :param contact_id: int: Specify the contact to be deleted
    :param ge: Specify that the contact_id must be greater than or equal to 1
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :return: A contactmodel object
    """
    contact = await repository_contacts.update_contact(body, contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return contact


@router.delete("/delete/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               description=TO_MANY_REQUESTS,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(contact_id: int = Path(1, ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
        The function takes in an integer representing the id of the contact to be removed,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Get the contact id from the url
    :param ge: Specify that the value of the parameter must be greater than or equal to 1
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user from the database
    :return: A contact object
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return contact