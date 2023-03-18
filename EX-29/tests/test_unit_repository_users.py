import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import create_user, get_user_by_email, confirmed_email
from src.schemas import UserModel


class TestUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.body = UserModel(
            username="Test",
            email="test@email.com",
            password="1234567890"
        )

    async def test_create_user(self):
        body = self.body
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_user_by_email(self):
        body = self.body
        user = User(email=body.email)
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=user.email, db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="fake_email@gmail.com", db=self.session)
        self.assertIsNone(result)

    async def test_confirmed_email(self):
        body = self.body
        user = User(email=body.email)
        await confirmed_email(email=user.email, db=self.session)
        result = await get_user_by_email(email=body.email, db=self.session)
        self.assertEqual(result.confirmed, True)


if __name__ == '__main__':
    unittest.main()