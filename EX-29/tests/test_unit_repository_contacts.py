import unittest
from datetime import date, timedelta, datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from src.database.models import User, Contact
from src.repository.contacts import create_contact, get_contact, update_contact, remove_contact, birthday_list, \
    get_contacts, searcher
from src.schemas import ContactModel


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_create_contact(self):
        body = ContactModel(
            name="John",
            surname="Doe",
            email="johndoe@example.com",
            phone="1234567890",
            birthday=date.today(),
            additionally="Additional info",
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.additionally, body.additionally)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_contact(self):
        contact = Contact()
        self.session.query(Contact).filter.return_value.first.return_value = contact
        result = await get_contact(contact.id, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_get_contacts(self):
        contacts = [Contact(user_id=1), Contact(user_id=1), Contact(user_id=1)]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_not_found(self):
        contact = Contact()
        self.session.query(Contact).filter.return_value.first.return_value = None
        result = await get_contact(contact.id, self.user, self.session)
        self.assertIsNone(result)

    async def test_update_contact(self):
        contact_id = 1
        body = ContactModel(
            name="John",
            surname="Doe",
            email="johndoe@example.com",
            phone="1234567890",
            birthday=date.today(),
            additionally="Additional info",
        )
        contact = Contact(id=contact_id, name="Jane", surname="Doe", email="janedoe@example.com", phone="0987654321",
                          birthday=date.today(), additionally="Old info")
        self.session.query(Contact).filter.return_value.first.return_value = contact
        result = await update_contact(body, contact_id, self.user, self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.additionally, body.additionally)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact(self):
        contact_id = 1
        contact = Contact(id=contact_id)
        self.session.query(Contact).filter.return_value.first.return_value = contact
        result = await remove_contact(contact_id, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_get_birthday_list(self):
        contacts = [Contact(birthday=datetime.now() + timedelta(days=1)),
                    Contact(birthday=datetime.now() + timedelta(days=2)),
                    Contact(birthday=datetime.now() + timedelta(days=3)),
                    Contact(birthday=datetime.now() + timedelta(days=4)),
                    Contact(birthday=datetime.now() + timedelta(days=5)),
                    Contact(birthday=datetime.now() + timedelta(days=6)),
                    Contact(birthday=datetime.now() + timedelta(days=7)),
                    Contact(birthday=datetime.now() + timedelta(days=8)),
                    Contact(birthday=datetime.now() + timedelta(days=9)),
                    Contact(birthday=datetime.now() + timedelta(days=10)),
                    ]
        self.session.query().all.return_value = contacts
        result = await birthday_list(db=self.session)
        self.assertEqual(result, contacts[0:7])

    async def test_searcher(self):
        contact1 = Contact(name='John', surname='Doe', email='john.doe@example.com')
        contact2 = Contact(name='Jane', surname='Doe', email='jane.doe@example.com')
        contact3 = Contact(name='Alice', surname='Smith', email='alice.smith@example.com')
        self.session.query.return_value.all.return_value = [contact1, contact2, contact3]
        results = await searcher('Doe', self.session)

        assert contact1 in results
        assert contact2 in results
        assert contact3 not in results


if __name__ == '__main__':
    unittest.main()