from .test_models import TestModels
from ..forms import SignUpForm, DonationForm, FundraiserForm


class SignupTests(TestModels):

    def test_signup_valid(self):
        form = SignUpForm(
            data={
                'name': 'Test Fundraiser',
                'email': 'name@domain.com',
                'username': 'username',
                'password1': 'j234rlj33s',
                'password2': 'j234rlj33s',
                }
        )
        self.assertTrue(form.is_valid())

    def test_signup_save(self):
        form = SignUpForm(
            data={
                'name': 'Test Fundraiser',
                'email': 'name@domain.com',
                'username': 'username',
                'password1': 'j234rlj33s',
                'password2': 'j234rlj33s',
                }
            )
        user = form.save()
        self.assertEqual(user.username, 'username')


class DonationFormTests(TestModels):

    def test_simple_donation_valid(self):
        form = DonationForm(
            data={
                'name': 'Donator',
                'amount': '50',
                'email': 'name@domain.com',
            }
        )
        self.assertTrue(form.is_valid())

    def test_other_donation_valid(self):
        form = DonationForm(
            data={
                'name': 'Donator',
                'amount': 'other',
                'other_amount': '33',
                'email': 'name@domain.com',
            }
        )
        self.assertTrue(form.is_valid())


class FundraiserFormTest(TestModels):

    def test_simple_fundraiser(self):
        form = FundraiserForm(
            data={
                'campaign': '1',
                'name': 'Test Post',
                'goal': '200',
                'email': 'name@domain.com',
                'username': 'username',
                'password1': 'j234rlj33s',
                'password2': 'j234rlj33s',
            }
        )
        self.assertTrue(form.is_valid())
