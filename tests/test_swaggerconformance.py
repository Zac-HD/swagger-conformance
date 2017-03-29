import logging
import unittest
import re
import os.path as osp

import responses

import swaggerconformance
import swaggerconformance.template
import swaggerconformance.client

TEST_SCHEMA_DIR = osp.relpath(osp.join(osp.dirname(osp.realpath(__file__)),
                                       'test_schemas/'))
TEST_SCHEMA_PATH = osp.join(TEST_SCHEMA_DIR, 'test_schema.json')
FULL_PUT_SCHEMA_PATH = osp.join(TEST_SCHEMA_DIR, 'full_put_schema.json')
PETSTORE_SCHEMA_PATH = osp.join(TEST_SCHEMA_DIR, 'petstore.json')
UBER_SCHEMA_PATH = osp.join(TEST_SCHEMA_DIR, 'uber.json')
SCHEMA_URL_BASE = 'http://127.0.0.1:5000/api'
CONTENT_TYPE_JSON = 'application/json'


class APITemplateTestCase(unittest.TestCase):

    def setUp(self):
        self.client = swaggerconformance.client.SwaggerClient(TEST_SCHEMA_PATH)

    def tearDown(self):
        # No teardown of test fixtures required.
        pass

    def test_schema_parse(self):
        endpoints_clctn = swaggerconformance.template.APITemplate(self.client)
        expected_endpoints = {'/schema', '/apps', '/apps/{appid}'}
        self.assertSetEqual(set(endpoints_clctn.endpoints.keys()),
                            expected_endpoints)

    @responses.activate
    def test_endpoint_manually(self):
        api_template = swaggerconformance.template.APITemplate(self.client)

        # Find the template GET operation on the /apps/{appid} endpoint.
        app_id_get_op = None
        for operation_template in api_template.template_operations():
            if (operation_template.operation.method == 'get' and
                    operation_template.operation.path == '/apps/{appid}'):
                self.assertIsNone(app_id_get_op)
                app_id_get_op = operation_template
        self.assertIsNotNone(app_id_get_op)

        # The operation takes one parameter, 'appid', which is a string.
        self.assertEqual(list(app_id_get_op.parameters.keys()), ['appid'])
        self.assertEqual(app_id_get_op.parameters['appid'].type, 'string')

        # Send an example parameter in to the endpoint manually, catch the
        # request, and respond.
        params = {'appid': 'test_string'}
        responses.add(responses.GET, SCHEMA_URL_BASE + '/apps/test_string',
                      json={}, status=404,
                      content_type=CONTENT_TYPE_JSON)
        result = self.client.request(app_id_get_op, params)
        self.assertEqual(result.status, 404)


class ParameterTypesTestCase(unittest.TestCase):

    @responses.activate
    def test_full_put(self):
        # Handle all the basic endpoints.
        responses.add(responses.GET, SCHEMA_URL_BASE + '/schema',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/example',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.DELETE, SCHEMA_URL_BASE + '/example',
                      json=None, status=204,
                      content_type=CONTENT_TYPE_JSON)

        # Handle the PUT requests on the endpoint which expects an integer path
        # parameter. Don't validate the body as we expect pyswagger to do so.
        url_re = re.compile(SCHEMA_URL_BASE + r'/example/-?\d+')
        responses.add(responses.PUT, url_re,
                      json=None, status=204,
                      content_type=CONTENT_TYPE_JSON)

        # Now just kick off the validation process.
        swaggerconformance.validate_schema(FULL_PUT_SCHEMA_PATH)


class ExternalExamplesTestCase(unittest.TestCase):

    @responses.activate
    def test_swaggerio_petstore(self):
        # Example responses matching the required models.
        pet = {
            "id": 0,
            "category": {
                "id": 0,
                "name": "string"
            },
            "name": "doggie",
            "photoUrls": [
                "string"
            ],
            "tags": [
                {
                    "id": 0,
                    "name": "string"
                }
            ],
            "status": "available"
        }
        pets = [pet]
        inventory = {"additionalProp1": 0, "additionalProp2": 0}
        order = {"id": 0,
                 "petId": 0,
                 "quantity": 0,
                 "shipDate": "2017-03-21T23:13:44.949Z",
                 "status": "placed",
                 "complete": True}
        api_response = {"code": 0, "type": "string", "message": "string"}
        user = {"id": 0,
                "username": "string",
                "firstName": "string",
                "lastName": "string",
                "email": "string",
                "password": "string",
                "phone": "string",
                "userStatus": 0}

        # Handle all the basic endpoints.
        responses.add(responses.GET, SCHEMA_URL_BASE + '/pet',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.POST, SCHEMA_URL_BASE + '/pet',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.PUT, SCHEMA_URL_BASE + '/pet',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        url_re = re.compile(SCHEMA_URL_BASE + r'/pet/-?\d+')
        responses.add(responses.GET, url_re,
                      json=pet, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.POST, url_re,
                      json=api_response, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.DELETE, url_re,
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/pet/findByStatus',
                      json=pets, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/pet/findByTags',
                      json=pets, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/store',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/store/inventory',
                      json=inventory, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.POST, SCHEMA_URL_BASE + '/store/order',
                      json=order, status=200,
                      content_type=CONTENT_TYPE_JSON)
        url_re = re.compile(SCHEMA_URL_BASE + r'/store/order/-?\d+')
        responses.add(responses.GET, url_re,
                      json=order, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.DELETE, url_re,
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/user',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.POST, SCHEMA_URL_BASE + '/user',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.DELETE, SCHEMA_URL_BASE + '/user',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        url_re = re.compile(SCHEMA_URL_BASE + r'/user/(?!login).+')
        responses.add(responses.GET, url_re,
                      json=user, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.PUT, url_re,
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.DELETE, url_re,
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        url_re = re.compile(SCHEMA_URL_BASE +
                            r'/user/login\?username=.*&password=.*')
        responses.add(responses.GET, url_re,
                      json="example", status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/user/logout',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.POST,
                      SCHEMA_URL_BASE + '/user/createWithArray',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.POST,
                      SCHEMA_URL_BASE + '/user/createWithList',
                      json=None, status=200,
                      content_type=CONTENT_TYPE_JSON)

        # Handle the PUT requests on the endpoint which expects an integer path
        # parameter. Don't validate the body as we expect pyswagger to do so.
        url_re = re.compile(SCHEMA_URL_BASE + r'/example/-?\d+')
        responses.add(responses.PUT, url_re,
                      json=None, status=204,
                      content_type=CONTENT_TYPE_JSON)

        # Now just kick off the validation process.
        swaggerconformance.validate_schema(PETSTORE_SCHEMA_PATH)

    @responses.activate
    def test_openapi_uber(self):
        profile = {"first_name": "steve",
                   "last_name": "stevenson",
                   "email": "example@stevemail.com",
                   "picture": "http://steve.com/stevepic.png",
                   "promo_code": "12341234"}
        activities = {"offset": 123,
                      "limit": 99,
                      "count": 432,
                      "history": [{"uuid": 9876543210}]}
        product = {"product_id": "example",
                   "description": "it's a product",
                   "display_name": "bestproductno1",
                   "capacity": "4 hippos",
                   "image": "http://hippotransports.com/hippocar.png"}
        products = [product]
        price_estimate = {"product_id": "example",
                          "currency_code": "gbp",
                          "display_name": "it's a product",
                          "estimate": "123.50",
                          "low_estimate": 123,
                          "high_estimate": 124,
                          "surge_multiplier": 22.2}
        price_estimates = [price_estimate]
        responses.add(responses.GET, SCHEMA_URL_BASE + '/estimates/price',
                      json=price_estimates, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/estimates/time',
                      json=products, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/history',
                      json=activities, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/me',
                      json=profile, status=200,
                      content_type=CONTENT_TYPE_JSON)
        responses.add(responses.GET, SCHEMA_URL_BASE + '/products',
                      json=products, status=200,
                      content_type=CONTENT_TYPE_JSON)

        # Now just kick off the validation process.
        swaggerconformance.validate_schema(UBER_SCHEMA_PATH)


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s:%(levelname)-7s:%(funcName)s:%(message)s'
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
    unittest.main()
