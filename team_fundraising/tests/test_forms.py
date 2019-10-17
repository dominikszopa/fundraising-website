from django.urls import reverse
from .test_models import TestModels
from ..forms import SignUpForm
from ..models import Fundraiser


class SignupTests(TestModels):

    def test_signup_new_person(self):
        form = SignUpForm(
            data={
                'name': 'Test Fundraiser',
                'goal': 200,
                'email': 'name@domain.com',
                'username': 'username',
                'password1': 'j234rlj33s',
                'password2': 'j234rlj33s',
                }
        )
        self.assertTrue(form.is_valid())


class SignUpPosts(TestModels):

    def test_post_signup_new_person(self):
        response = self.client.post(
            reverse('team_fundraising:signup'),
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
        self.assertEqual(response.status_code, 200)
        fundraiser = Fundraiser.objects.get(id=3)
        self.assertEquals(str(fundraiser), 'First Fundraiser')
