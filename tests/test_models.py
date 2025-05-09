# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        logging.debug(f'Created product: {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found = Product.find(product.id)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)
        self.assertEqual(found.available, product.available)
        self.assertEqual(found.category, product.category)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        logging.debug(f'Created product: {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        pid = product.id
        product.id = None
        self.assertRaises(DataValidationError, product.update)
        product.id = pid
        logging.debug(f'inserted product: {product}')
        product.description = 'foo'
        product.update()
        self.assertEqual(product.description, 'foo')

        products = Product.all()
        self.assertEqual(len(products), 1)

        found = Product.find(product.id)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.description, product.description)

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        logging.debug(f'Created product: {product}')
        product.create()

        products = Product.all()
        self.assertEqual(len(products), 1)

        product.delete()

        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)

        for _ in range(5):
            ProductFactory().create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should find a product by the given name"""
        products = []

        for _ in range(5):
            product = ProductFactory()
            product.create()
            products.append(product)

        name = products[0].name
        occurrences = sum([1 for p in products if p.name == name])

        found_products = Product.find_by_name(name)
        self.assertEqual(occurrences, sum([1 for p in found_products if p.name == name]))

        for p in found_products:
            self.assertEqual(p.name, name)

    def test_find_by_availability(self):
        """It should find a product by the given availability"""
        products = []

        for _ in range(10):
            product = ProductFactory()
            product.create()
            products.append(product)

        availability = products[0].available
        occurrences = sum([1 for p in products if p.available == availability])

        found_products = Product.find_by_availability(availability)
        self.assertEqual(occurrences, sum([1 for p in found_products if p.available == availability]))

        for p in found_products:
            self.assertEqual(p.available, availability)

    def test_find_by_category(self):
        """It should find a product by the given category"""
        products = []

        for _ in range(10):
            product = ProductFactory()
            product.create()
            products.append(product)

        category = products[0].category
        occurrences = sum([1 for p in products if p.category == category])

        found_products = Product.find_by_category(category)
        self.assertEqual(occurrences, sum([1 for p in found_products if p.category == category]))

        for p in found_products:
            self.assertEqual(p.category, category)

    def test_find_by_price(self):
        """It should find a product by the given price"""
        products = []

        for _ in range(10):
            product = ProductFactory()
            product.create()
            products.append(product)

        price = products[0].price
        occurrences = sum([1 for p in products if p.price == price])

        found_products = Product.find_by_price(price)
        self.assertEqual(occurrences, sum([1 for p in found_products if p.price == price]))

        for p in found_products:
            self.assertEqual(p.price, price)

    def test_find_by_price_string(self):
        """It should find a product by the given price"""
        products = []

        for _ in range(10):
            product = ProductFactory()
            product.create()
            products.append(product)

        price = products[0].price
        occurrences = sum([1 for p in products if p.price == price])

        found_products = Product.find_by_price(str(price))
        self.assertEqual(occurrences, sum([1 for p in found_products if p.price == price]))

        for p in found_products:
            self.assertEqual(p.price, price)
