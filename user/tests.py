from django.test import TestCase, RequestFactory

from .views import *
from authorization.views import *
import json

token = ""

class ResearchTests(TestCase):

    def setUp(self) -> None:
        pass

    def testA1_url_register(self):

            global token

            userdata = {
            "email":"sad222@a.com",
            "name":"231322 !!!",
            "password":"jasdjasjd2!",
            "is_research":0,
            "info":{
                "name":"231322 !!!",
                "age":20,
                "gender":"male"
            },
            "settings":{
                "user":"sad222@a.com",
                "locale":"ua"
            },
            "system_info":{
                "user":"sad222@a.com",
                "os":"unknown"
            }        
            }

            request = RequestFactory().post(
                'api/v1/users', userdata, content_type = "application/json")
            response = RegistrationUserAPIView.as_view()(request)
            self.assertEqual(response.status_code, 201)  
            rendered_content = json.loads(response.rendered_content)
            token = rendered_content['tokens']['access']  
 
