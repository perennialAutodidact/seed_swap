from barters_app import views
from barters_app.models import (MaterialBarter, PlantBarter, ProduceBarter,
                                SeedBarter, ToolBarter)
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token as generate_csrf_token
from django.test import TestCase
from django.urls import reverse
from barters_app.serializers import SeedBarterSerializer
from garden_barter_proj import settings
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory
from users_app.serializers import UserDetailSerializer
from users_app.utils import Token, generate_test_user
from jwt.exceptions import DecodeError


class TestCreateBarter(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        self.user, self.valid_refresh_token = generate_test_user(
            UserModel=get_user_model(),
            email='test_user_1@gardenbarter.com',
            password='pass3412'
        )

        self.valid_access_token = Token(self.user, 'access')
    
        self.invalid_access_token = Token(self.user, 'access', expiry={'days':-1})

        self.barter_data = {
            'title': 'test barter title',
            'description': 'test barter description',
            'will_trade_for': 'item that will be traded',
            'is_free': False,
            'cross_street_1': '123 Faux St.',
            'cross_street_2': '789 Impostor Rd',
            'postal_code': '99999',
            'latitude': '',
            'longitude': ''
        }

        self.seed_barter_data = self.barter_data.copy()
        self.seed_barter_data.update({
            'genus': 'leonarus',
            'species': 'cardiaca',
            'common_name': 'motherwort',
        })

        self.seed_barter_data_not_free_no_trade = self.seed_barter_data.copy()
        self.seed_barter_data_not_free_no_trade.update({
            'is_free': False,
            'will_trade_for': ''
        })

    def generate_request(self, data):
        '''return a Factory.post() request with the provided data'''
        return self.factory.post(
            reverse('barters_app:create'),
            data,
            format='json'
        )

    def enrich_request(self, request, refresh_token, access_token, csrf_token):
        '''Ammend COOKIES, META and header data to the given request'''

        # if refresh_token and csrf_token:
        request.COOKIES.update({
            'refreshtoken': refresh_token,
            'csrftoken': csrf_token
        })
        
        # if csrf_token:
        request.META.update({
            'X-CSRFToken': csrf_token
        })

        # if access_token:
        headers = {
            'Authorization': f'Token {access_token}',
        }

        request.headers = headers

        return request

    def test_create_seed_barter_success(self):
        request = self.generate_request(
            {
                'userData': UserDetailSerializer(self.user).data,
                'barterType': 'seed_barter',
                'formData':self.seed_barter_data
            }
        )
        csrf_token = generate_csrf_token(request)

        request = self.enrich_request(request, self.valid_refresh_token, self.valid_access_token, csrf_token)

        response = views.create(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        new_barter = SeedBarter.objects.get(title=self.seed_barter_data['title'])
        self.assertEqual(new_barter.title, self.seed_barter_data['title'])
        
    def test_create_seed_barter_fail_missing_form_data(self):
        request = self.generate_request(
            {
                'user_data': UserDetailSerializer(self.user).data,
                'barterType': 'seed_barter',
                # 'formData':self.seed_barter_data
            }
        )
        csrf_token = generate_csrf_token(request)

        request = self.enrich_request(request, self.valid_refresh_token, self.valid_access_token, csrf_token)

        response = views.create(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'].startswith("Missing 'formData' object."))

    def test_create_seed_barter_fail_missing_barter_type(self):
        request = self.factory.post(
            reverse('barters_app:create'),
            {
                'userData': UserDetailSerializer(self.user).data,
                # 'barterType': 'seed_barter',
                'formData':self.seed_barter_data
            },
            format='json'
        )
        csrf_token = generate_csrf_token(request)

        request = self.enrich_request(request, self.valid_refresh_token, self.valid_access_token, csrf_token)

        response = views.create(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'].startswith("Missing property 'barterType'."))
        
    def test_create_seed_barter_fail_missing_user_data(self):
        request = self.factory.post(
            reverse('barters_app:create'),
            {
                # 'userData': UserDetailSerializer(self.user).data,
                'barterType': 'seed_barter',
                'formData':self.seed_barter_data
            },
            format='json'
        )
        csrf_token = generate_csrf_token(request)

        request = self.enrich_request(request, self.valid_refresh_token, self.valid_access_token, csrf_token)

        response = views.create(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'].startswith("Missing 'userData' object."))
        
    def test_create_seed_barter_fail_missing_not_free_no_trade(self):
        request = self.factory.post(
            reverse('barters_app:create'),
            {
                'userData': UserDetailSerializer(self.user).data,
                'barterType': 'seed_barter',
                'formData':self.seed_barter_data_not_free_no_trade
            },
            format='json'
        )
        csrf_token = generate_csrf_token(request)

        request = self.enrich_request(request, self.valid_refresh_token, self.valid_access_token, csrf_token)

        response = views.create(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'].startswith("Desired trade missing."))
        
    def test_create_seed_barter_fail_unenriched_request(self):
        request = self.factory.post(
            reverse('barters_app:create'),
            {
                'userData': UserDetailSerializer(self.user).data,
                'barterType': 'seed_barter',
                'formData':self.seed_barter_data_not_free_no_trade
            },
            format='json'
        )
        csrf_token = generate_csrf_token(request)

        # invalid access token
        request = self.enrich_request(request, self.valid_refresh_token, self.invalid_access_token, csrf_token)

        response = views.create(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['msg'], ErrorDetail('Access token expired', code='authentication_failed'))
        

        with self.assertRaises(DecodeError, msg='Not enough segments'):
            # missing access token
            request = self.enrich_request(request, self.valid_refresh_token, None, csrf_token)
            response = views.create(request)
            
            # missing csrf_token
            request = self.enrich_request(request, self.valid_refresh_token, self.valid_access_token, None)
            response = views.create(request)

