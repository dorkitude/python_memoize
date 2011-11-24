# Python standard library imports:
import random
import unittest
import time

# Our own imports: 
from ..dorkitude_utils.base_test_case import BaseTestCase

from .. import Memoize, MemoizeGlobal


class SomethingNew(object):
    def __init__(self, output_quantity):
        self.output_quantity = output_quantity


class MemoizeTests(BaseTestCase):

    
    def test_memoize_classmethod(self):

        class MyClass(object):
            
            count = 0

            @classmethod
            @Memoize
            def increment(self):
                self.count = self.count + 1
                return self.count


        # value shouldn't change
        self.assert_equal(MyClass.increment(), 1)
        self.assert_equal(MyClass.increment(), 1)
        self.assert_equal(MyClass.increment(), 1)

        # flush cache; value should go up once
        Memoize.flush_item(MyClass)
        self.assert_equal(MyClass.increment(), 2)
        self.assert_equal(MyClass.increment(), 2)
        self.assert_equal(MyClass.increment(), 2)

        Memoize.flush()
        self.assert_equal(MyClass.increment(), 3)
        self.assert_equal(MyClass.increment(), 3)
        self.assert_equal(MyClass.increment(), 3)


    def test_memoize_with_instance_among_args(self):
        """

        This test was written to cover the case where one or more of the args
        sent to the Memoize'd method is an instance.

        """
        class WabaClass(object):
            id = 0
            
        class MyClass(object):
            count = 0
            
            @classmethod
            @Memoize
            def get_foo(cls, reward, a, b):
                cls.count = cls.count + 1
                return (cls.count, reward.output_quantity)

        r1 = SomethingNew(9999999)
        r2 = SomethingNew(9999998)
        
        self.assert_equal(MyClass.get_foo(r1,'a','b'), (1, 9999999))
        self.assert_equal(MyClass.get_foo(r1,'a','b'), (1, 9999999))
        self.assert_equal(MyClass.get_foo(r1,'a','b'), (1, 9999999))
        self.assert_equal(MyClass.get_foo(r1,'a','b'), (1, 9999999))
        
        self.assert_equal(MyClass.get_foo(r2,'a','b'), (2, 9999998))
        self.assert_equal(MyClass.get_foo(r2,'a','b'), (2, 9999998))
        self.assert_equal(MyClass.get_foo(r2,'a','b'), (2, 9999998))

        
    def test_memoize_instance_property_method(self):
        class MyClass(object):

            _count = 0

            def increment(self):
                self.__class__._count = self.__class__._count + 1
                return self._count

            @property
            @Memoize
            def count(self):
                return self._count
            
        obj = MyClass()
        
        self.assert_equal(obj.count, 0)
        obj.increment()
        self.assert_equal(obj.count, 0)
        self.assert_equal(obj.__class__._count, 1)
        
        obj2 = MyClass()
        self.assert_equal(obj2.count, 1)  # should NOT be memoized
        self.assert_equal(obj.count, 0)
        self.assert_equal(obj2.count, 1)
        obj2.increment()
        self.assert_equal(obj.count, 0)
        self.assert_equal(obj2.count, 1)
        
        
        
    def test_memoize_instance_method(self):
        class MyClass(object):

            count = 0

            @Memoize
            def increment(self):
                self.count = self.count + 1
                return self.count

            @Memoize
            def add(self, addme):
                self.count = self.count + addme
                return self.count

        obj = MyClass()

        self.assert_equal(obj.increment(), 1)
        self.assert_equal(obj.increment(), 1)

        Memoize.flush()
        self.assert_equal(obj.increment(), 2)

        obj = MyClass()
        self.assert_equal(obj.increment(), 1)
        self.assert_equal(obj.increment(), 1)
        self.assert_equal(obj.increment(), 1)

        Memoize.flush_item(obj)
        self.assert_equal(obj.add(4), 5)
        self.assert_equal(obj.add(4), 5)
        self.assert_equal(obj.add(4), 5)

        self.assert_equal(obj.increment(), 6)
        self.assert_equal(obj.increment(), 6)
        self.assert_equal(obj.increment(), 6)


    def test_memoize_global(self):

        x = 0

        @MemoizeGlobal
        def rando():
            v1 = random.choice(range(1,10000))
            v2 = random.choice(range(1,10000))
            return "{}.{}".format(v1, v2)

        self.assert_equal(rando(), rando())
        self.assert_equal(rando(), rando())
        self.assert_equal(rando(), rando())


        old_val = rando()
        MemoizeGlobal.flush()
        new_val = rando()
        self.assertNotEqual(old_val, new_val)
        self.assert_equal(rando(), new_val)
        self.assert_equal(rando(), rando())
