from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(user: User, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.
        Args:
            user (User): The User object to get contacts for.
            db (Session): A database session to use when querying the database.

    :param user: User: Get the user id from the database
    :param db: Session: Pass the database session to the function
    :return: A list of contacts for the specified user
    """
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id)).all()
    return contacts


async def get_contact(contact_id: int, user: User, db: Session):
    """
    The get_contact function takes in a contact_id and user, and returns the contact with that id.
        Args:
            contact_id (int): The id of the desired Contact object.
            user (User): The User object associated with this request.

    :param contact_id: int: Specify the id of the contact to be returned
    :param user: User: Get the user's id from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact


async def create_contact(body: ContactModel, user: User, db: Session):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Validate the request body
    :param user: User: Get the user id from the token
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session):
    """
    The update_contact function updates a contact in the database.
        Args:
            body (ContactModel): The updated contact object to be stored in the database.
            contact_id (int): The id of the contact to update.
            user (User): The current user, used for authorization purposes.

    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Specify the contact to be deleted
    :param user: User: Get the user id from the token
    :param db: Session: Get access to the database
    :return: A contact
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additionally = body.additionally
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            user (User): The user who is removing the contact. This is used to ensure that only contacts belonging to this
                user are deleted, and not contacts belonging to other users with similar IDs.

    :param contact_id: int: Specify the id of the contact that is to be removed
    :param user: User: Get the user's id from the database
    :param db: Session: Pass the database session to the function
    :return: A contact object if the contact is found and deleted
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def birthday_list(db: Session):
    """
    The birthday_list function returns a list of contacts whose birthday is within the next 7 days.
        The function takes in a database session and queries all contacts from the database.
        It then iterates through each contact, replacing their birth year with the current year,
        and subtracting that date from today's date to get a timedelta object. If that timedelta object
        is between -7 days and 0 days (i.e., if it's less than 7 days away), we add it to our list of upcoming birthdays.

    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthday is in the next 7 days
    """
    contacts_list = []
    dt_now = datetime.now()
    now_year = datetime.now().strftime('%Y')
    contacts_all = db.query(Contact).all()
    for contact in contacts_all:
        delta = contact.birthday.replace(year=int(now_year)) - dt_now
        if timedelta(days=-1) < delta < timedelta(days=7):
            contacts_list.append(contact)
    return contacts_list


async def searcher(part_to_search: str, db: Session):
    """
    The searcher function takes a string and a database session as arguments.
    It then searches the database for contacts that have the string in their name, surname or email.
    The function returns a list of all contacts found.

    :param part_to_search: str: Search for a contact in the database
    :param db: Session: Pass the database session to the function
    :return: A list of contacts that match the search criteria
    """
    contact_list = []
    contacts_all = db.query(Contact).all()
    for contact in contacts_all:
        if part_to_search.capitalize() in contact.name.capitalize() and contact not in contact_list:
            contact_list.append(contact)
        if part_to_search.capitalize() in contact.surname.capitalize() and contact not in contact_list:
            contact_list.append(contact)
        if part_to_search.capitalize() in contact.email.capitalize() and contact not in contact_list:
            contact_list.append(contact)
    return contact_list