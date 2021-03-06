# -*- coding: utf-8 -*-
# Copyright 2017 Google LLC All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import datetime
import sys
import unittest

import mock


class TestGeoPoint(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from google.cloud.firestore_v1beta1._helpers import GeoPoint

        return GeoPoint

    def _make_one(self, *args, **kwargs):
        klass = self._get_target_class()
        return klass(*args, **kwargs)

    def test_constructor(self):
        lat = 81.25
        lng = 359.984375
        geo_pt = self._make_one(lat, lng)
        self.assertEqual(geo_pt.latitude, lat)
        self.assertEqual(geo_pt.longitude, lng)

    def test_to_protobuf(self):
        from google.type import latlng_pb2

        lat = 0.015625
        lng = 20.03125
        geo_pt = self._make_one(lat, lng)
        result = geo_pt.to_protobuf()
        geo_pt_pb = latlng_pb2.LatLng(latitude=lat, longitude=lng)
        self.assertEqual(result, geo_pt_pb)

    def test___eq__(self):
        lat = 0.015625
        lng = 20.03125
        geo_pt1 = self._make_one(lat, lng)
        geo_pt2 = self._make_one(lat, lng)
        self.assertEqual(geo_pt1, geo_pt2)

    def test___eq__type_differ(self):
        lat = 0.015625
        lng = 20.03125
        geo_pt1 = self._make_one(lat, lng)
        geo_pt2 = object()
        self.assertNotEqual(geo_pt1, geo_pt2)
        self.assertIs(geo_pt1.__eq__(geo_pt2), NotImplemented)

    def test___ne__same_value(self):
        lat = 0.015625
        lng = 20.03125
        geo_pt1 = self._make_one(lat, lng)
        geo_pt2 = self._make_one(lat, lng)
        comparison_val = (geo_pt1 != geo_pt2)
        self.assertFalse(comparison_val)

    def test___ne__(self):
        geo_pt1 = self._make_one(0.0, 1.0)
        geo_pt2 = self._make_one(2.0, 3.0)
        self.assertNotEqual(geo_pt1, geo_pt2)

    def test___ne__type_differ(self):
        lat = 0.015625
        lng = 20.03125
        geo_pt1 = self._make_one(lat, lng)
        geo_pt2 = object()
        self.assertNotEqual(geo_pt1, geo_pt2)
        self.assertIs(geo_pt1.__ne__(geo_pt2), NotImplemented)


class TestFieldPath(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from google.cloud.firestore_v1beta1._helpers import FieldPath
        return FieldPath

    def _make_one(self, *args):
        klass = self._get_target_class()
        return klass(*args)

    def test_ctor_w_none_in_part(self):
        with self.assertRaises(ValueError):
            self._make_one('a', None, 'b')

    def test_ctor_w_empty_string_in_part(self):
        with self.assertRaises(ValueError):
            self._make_one('a', '', 'b')

    def test_ctor_w_integer_part(self):
        with self.assertRaises(ValueError):
            self._make_one('a', 3, 'b')

    def test_ctor_w_list(self):
        parts = ['a', 'b', 'c']
        with self.assertRaises(ValueError):
            self._make_one(parts)

    def test_ctor_w_tuple(self):
        parts = ('a', 'b', 'c')
        with self.assertRaises(ValueError):
            self._make_one(parts)

    def test_ctor_w_iterable_part(self):
        with self.assertRaises(ValueError):
            self._make_one('a', ['a'], 'b')

    def test_constructor_w_single_part(self):
        field_path = self._make_one('a')
        self.assertEqual(field_path.parts, ('a',))

    def test_constructor_w_multiple_parts(self):
        field_path = self._make_one('a', 'b', 'c')
        self.assertEqual(field_path.parts, ('a', 'b', 'c'))

    def test_ctor_w_invalid_chars_in_part(self):
        invalid_parts = ('~', '*', '/', '[', ']', '.')
        for invalid_part in invalid_parts:
            field_path = self._make_one(invalid_part)
            self.assertEqual(field_path.parts, (invalid_part, ))

    def test_ctor_w_double_dots(self):
        field_path = self._make_one('a..b')
        self.assertEqual(field_path.parts, ('a..b',))

    def test_ctor_w_unicode(self):
        field_path = self._make_one('一', '二', '三')
        self.assertEqual(field_path.parts, ('一', '二', '三'))

    def test_from_string_w_empty_string(self):
        parts = ''
        with self.assertRaises(ValueError):
            self._get_target_class().from_string(parts)

    def test_from_string_w_empty_field_name(self):
        parts = 'a..b'
        with self.assertRaises(ValueError):
            self._get_target_class().from_string(parts)

    def test_from_string_w_invalid_chars(self):
        invalid_parts = ('~', '*', '/', '[', ']', '.')
        for invalid_part in invalid_parts:
            with self.assertRaises(ValueError):
                self._get_target_class().from_string(invalid_part)

    def test_from_string_w_ascii_single(self):
        field_path = self._get_target_class().from_string('a')
        self.assertEqual(field_path.parts, ('a',))

    def test_from_string_w_ascii_dotted(self):
        field_path = self._get_target_class().from_string('a.b.c')
        self.assertEqual(field_path.parts, ('a', 'b', 'c'))

    def test_from_string_w_non_ascii_dotted(self):
        field_path = self._get_target_class().from_string('a.一')
        self.assertEqual(field_path.parts, ('a', '一'))

    def test___hash___w_single_part(self):
        field_path = self._make_one('a')
        self.assertEqual(hash(field_path), hash('a'))

    def test___hash___w_multiple_parts(self):
        field_path = self._make_one('a', 'b')
        self.assertEqual(hash(field_path), hash('a.b'))

    def test___hash___w_escaped_parts(self):
        field_path = self._make_one('a', '3')
        self.assertEqual(hash(field_path), hash('a.`3`'))

    def test___eq___w_matching_type(self):
        field_path = self._make_one('a', 'b')
        string_path = self._get_target_class().from_string('a.b')
        self.assertEqual(field_path, string_path)

    def test___eq___w_non_matching_type(self):
        field_path = self._make_one('a', 'c')
        other = mock.Mock()
        other.parts = 'a', 'b'
        self.assertNotEqual(field_path, other)

    def test___lt___w_matching_type(self):
        field_path = self._make_one('a', 'b')
        string_path = self._get_target_class().from_string('a.c')
        self.assertTrue(field_path < string_path)

    def test___lt___w_non_matching_type(self):
        field_path = self._make_one('a', 'b')
        other = object()
        # Python 2 doesn't raise TypeError here, but Python3 does.
        self.assertIs(field_path.__lt__(other), NotImplemented)

    def test___add__(self):
        path1 = 'a123', 'b456'
        path2 = 'c789', 'd012'
        path3 = 'c789.d012'
        field_path1 = self._make_one(*path1)
        field_path1_string = self._make_one(*path1)
        field_path2 = self._make_one(*path2)
        field_path1 += field_path2
        field_path1_string += path3
        field_path2 = field_path2 + self._make_one(*path1)
        self.assertEqual(field_path1, self._make_one(*(path1 + path2)))
        self.assertEqual(field_path2, self._make_one(*(path2 + path1)))
        self.assertEqual(field_path1_string, field_path1)
        self.assertNotEqual(field_path1, field_path2)
        with self.assertRaises(TypeError):
            field_path1 + 305

    def test_eq_or_parent_same(self):
        field_path = self._make_one('a', 'b')
        other = self._make_one('a', 'b')
        self.assertTrue(field_path.eq_or_parent(other))

    def test_eq_or_parent_prefix(self):
        field_path = self._make_one('a', 'b')
        other = self._make_one('a', 'b', 'c')
        self.assertTrue(field_path.eq_or_parent(other))
        self.assertTrue(other.eq_or_parent(field_path))

    def test_eq_or_parent_no_prefix(self):
        field_path = self._make_one('a', 'b')
        other = self._make_one('d', 'e', 'f')
        self.assertFalse(field_path.eq_or_parent(other))
        self.assertFalse(other.eq_or_parent(field_path))

    def test_to_api_repr_a(self):
        parts = 'a'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), 'a')

    def test_to_api_repr_backtick(self):
        parts = '`'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), r'`\``')

    def test_to_api_repr_dot(self):
        parts = '.'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), '`.`')

    def test_to_api_repr_slash(self):
        parts = '\\'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), r'`\\`')

    def test_to_api_repr_double_slash(self):
        parts = r'\\'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), r'`\\\\`')

    def test_to_api_repr_underscore(self):
        parts = '_33132'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), '_33132')

    def test_to_api_repr_unicode_non_simple(self):
        parts = '一'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), '`一`')

    def test_to_api_repr_number_non_simple(self):
        parts = '03'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), '`03`')

    def test_to_api_repr_simple_with_dot(self):
        field_path = self._make_one('a.b')
        self.assertEqual(field_path.to_api_repr(), '`a.b`')

    def test_to_api_repr_non_simple_with_dot(self):
        parts = 'a.一'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), '`a.一`')

    def test_to_api_repr_simple(self):
        parts = 'a0332432'
        field_path = self._make_one(parts)
        self.assertEqual(field_path.to_api_repr(), 'a0332432')

    def test_to_api_repr_chain(self):
        parts = 'a', '`', '\\', '_3', '03', 'a03', '\\\\', 'a0332432', '一'
        field_path = self._make_one(*parts)
        self.assertEqual(field_path.to_api_repr(),
                         r'a.`\``.`\\`._3.`03`.a03.`\\\\`.a0332432.`一`')


class TestFieldPathHelper(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from google.cloud.firestore_v1beta1._helpers import FieldPathHelper

        return FieldPathHelper

    def _make_one(self, *args, **kwargs):
        klass = self._get_target_class()
        return klass(*args, **kwargs)

    def test_constructor(self):
        helper = self._make_one(mock.sentinel.field_updates)
        self.assertIs(helper.field_updates, mock.sentinel.field_updates)
        self.assertEqual(helper.update_values, {})
        self.assertEqual(helper.field_paths, [])
        self.assertEqual(helper.unpacked_field_paths, {})

    def test_get_update_values_non_delete(self):
        helper = self._make_one(None)
        helper.update_values['foo'] = 'bar'
        self.assertIs(helper.get_update_values(83), helper.update_values)

    def test_get_update_values_with_delete(self):
        from google.cloud.firestore_v1beta1.constants import DELETE_FIELD

        helper = self._make_one(None)
        helper.update_values['baz'] = 98
        to_update = helper.get_update_values(DELETE_FIELD)
        self.assertIsNot(to_update, helper.update_values)
        self.assertEqual(to_update, {})

    def test_check_conflict_success(self):
        helper = self._make_one(None)
        ret_val = helper.check_conflict('foo.bar', ['foo', 'bar'], 0, {})
        # Really just making sure no exception was raised.
        self.assertIsNone(ret_val)

    def test_check_conflict_failure(self):
        helper = self._make_one(None)
        with self.assertRaises(ValueError) as exc_info:
            helper.check_conflict(
                'foo.bar', ['foo', 'bar'], 0, helper.PATH_END)

        err_msg = helper.FIELD_PATH_CONFLICT.format('foo', 'foo.bar')
        self.assertEqual(exc_info.exception.args, (err_msg,))

    def test_path_end_conflict_one_match(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        key = 'end'
        conflicting_paths = {key: helper.PATH_END}
        field_path = _helpers.FieldPath.from_string('start')
        err_val = helper.path_end_conflict(field_path, conflicting_paths)
        self.assertIsInstance(err_val, ValueError)
        conflict = _helpers.get_field_path([field_path.to_api_repr(), key])
        err_msg = helper.FIELD_PATH_CONFLICT.format(
            field_path.to_api_repr(), conflict)
        self.assertEqual(err_val.args, (err_msg,))

    def test_path_end_conflict_multiple_matches(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        end_part = 'end'
        sub_paths = collections.OrderedDict((
            (end_part, helper.PATH_END),
        ))
        middle_part = 'middle'
        conflicting_paths = collections.OrderedDict((
            (middle_part, sub_paths),
            ('nope', helper.PATH_END),
        ))

        field_path = _helpers.FieldPath.from_string('start')
        err_val = helper.path_end_conflict(field_path, conflicting_paths)
        self.assertIsInstance(err_val, ValueError)
        conflict = _helpers.get_field_path(
            [field_path.to_api_repr(), middle_part, end_part])
        err_msg = helper.FIELD_PATH_CONFLICT.format(
            field_path.to_api_repr(), conflict)
        self.assertEqual(err_val.args, (err_msg,))

    def test_add_field_path_end_success(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        curr_paths = {}
        to_update = {}
        field_path = _helpers.FieldPath.from_string('a.b.c')
        value = 1029830
        final_part = 'c'
        ret_val = helper.add_field_path_end(
            field_path, value, final_part, curr_paths, to_update)
        # Really just making sure no exception was raised.
        self.assertIsNone(ret_val)

        self.assertEqual(curr_paths, {final_part: helper.PATH_END})
        self.assertEqual(to_update, {final_part: value})
        self.assertEqual(helper.field_paths, [field_path])

    def test_add_field_path_end_failure(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        curr_paths = {'c': {'d': helper.PATH_END}}
        to_update = {'c': {'d': 'jewelry'}}
        helper.field_paths = [_helpers.FieldPath.from_string('a.b.c.d')]

        field_path = _helpers.FieldPath.from_string('a.b.c')
        value = 1029830
        final_part = 'c'
        with self.assertRaises(ValueError) as exc_info:
            helper.add_field_path_end(
                field_path, value, final_part, curr_paths, to_update)

        err_msg = helper.FIELD_PATH_CONFLICT.format(
            field_path.to_api_repr(), 'a.b.c.d')
        self.assertEqual(exc_info.exception.args, (err_msg,))
        self.assertEqual(curr_paths, {'c': {'d': helper.PATH_END}})
        self.assertEqual(to_update, {'c': {'d': 'jewelry'}})
        self.assertEqual(
            helper.field_paths, [_helpers.FieldPath.from_string('a.b.c.d')])

    def test_add_value_at_field_path_first_with_field(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        field_path = _helpers.FieldPath.from_string('zap')
        value = 121
        ret_val = helper.add_value_at_field_path(field_path, value)

        self.assertIsNone(ret_val)
        self.assertEqual(
            helper.update_values, {field_path.to_api_repr(): value})
        self.assertEqual(helper.field_paths, [field_path])
        self.assertEqual(
            helper.unpacked_field_paths,
            {field_path.to_api_repr(): helper.PATH_END})

    def test_add_value_at_field_path_first_with_path(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        field_path = _helpers.FieldPath.from_string('a.b.c')
        value = b'\x01\x02'
        ret_val = helper.add_value_at_field_path(field_path, value)

        self.assertIsNone(ret_val)
        self.assertEqual(helper.update_values, {'a': {'b': {'c': value}}})
        self.assertEqual(helper.field_paths, [field_path])
        self.assertEqual(
            helper.unpacked_field_paths, {'a': {'b': {'c': helper.PATH_END}}})

    def test_add_value_at_field_paths_at_same_level(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        field_path = _helpers.FieldPath.from_string('a.c')
        value = False
        helper.update_values = {'a': {'b': 80}}
        helper.field_paths = [_helpers.FieldPath.from_string('a.b')]
        helper.unpacked_field_paths = {'a': {'b': helper.PATH_END}}
        ret_val = helper.add_value_at_field_path(field_path, value)

        self.assertIsNone(ret_val)
        self.assertEqual(helper.update_values, {'a': {'b': 80, 'c': value}})
        self.assertEqual(
            helper.field_paths,
            [_helpers.FieldPath.from_string('a.b'), field_path])
        self.assertEqual(
            helper.unpacked_field_paths,
            {'a': {'b': helper.PATH_END, 'c': helper.PATH_END}})

    def test_add_value_at_field_paths_non_simple_field_names(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)
        field_path = _helpers.FieldPath.from_string('a.一')
        value = [1, 2, 3]
        helper.update_values = {'a': {'b': 80}}
        helper.field_paths = [_helpers.FieldPath.from_string('a.b')]
        helper.unpacked_field_paths = {'a': {'b': helper.PATH_END}}
        helper.add_value_at_field_path(field_path, value)

        self.assertEqual(helper.update_values, {'a': {'b': 80,
                                                      '一': value}
                                                })
        self.assertEqual(
            helper.field_paths,
            [_helpers.FieldPath.from_string('a.b'), field_path])
        self.assertEqual(
            helper.unpacked_field_paths,
            {'a': {'b': helper.PATH_END,
                   '一': helper.PATH_END}})

    def test_add_value_at_field_path_delete(self):
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.constants import DELETE_FIELD

        helper = self._make_one(None)

        field_path = _helpers.FieldPath.from_string('foo.bar')
        value = DELETE_FIELD
        ret_val = helper.add_value_at_field_path(field_path, value)

        self.assertIsNone(ret_val)
        self.assertEqual(helper.update_values, {})
        self.assertEqual(helper.field_paths, [field_path])
        self.assertEqual(
            helper.unpacked_field_paths, {'foo': {'bar': helper.PATH_END}})

    def test_add_value_at_field_path_failure_adding_more_specific_path(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)

        field_path = _helpers.FieldPath.from_string('DD.F')
        value = 99
        helper.update_values = {'DD': {'E': 19}}
        helper.field_paths = [_helpers.FieldPath.from_string('DD')]
        helper.unpacked_field_paths = {'DD': helper.PATH_END}
        with self.assertRaises(ValueError) as exc_info:
            helper.add_value_at_field_path(field_path, value)

        err_msg = helper.FIELD_PATH_CONFLICT.format('DD', field_path)
        self.assertEqual(exc_info.exception.args, (err_msg,))
        # Make sure inputs are unchanged.
        self.assertEqual(helper.update_values, {'DD': {'E': 19}})
        self.assertEqual(
            helper.field_paths,
            [_helpers.FieldPath.from_string('DD')])
        self.assertEqual(helper.unpacked_field_paths, {'DD': helper.PATH_END})

    def test_add_value_at_field_path_failure_adding_more_generic_path(self):
        from google.cloud.firestore_v1beta1 import _helpers

        helper = self._make_one(None)

        field_path = _helpers.FieldPath.from_string('x.y')
        value = {'t': False}
        helper.update_values = {'x': {'y': {'z': 104.5}}}
        helper.field_paths = ['x.y.z']
        helper.unpacked_field_paths = {'x': {'y': {'z': helper.PATH_END}}}
        with self.assertRaises(ValueError) as exc_info:
            helper.add_value_at_field_path(field_path, value)

        err_msg = helper.FIELD_PATH_CONFLICT.format(
            field_path.to_api_repr(), 'x.y.z')
        self.assertEqual(exc_info.exception.args, (err_msg,))
        # Make sure inputs are unchanged.
        self.assertEqual(helper.update_values, {'x': {'y': {'z': 104.5}}})
        self.assertEqual(helper.field_paths, ['x.y.z'])
        self.assertEqual(
            helper.unpacked_field_paths, {'x': {'y': {'z': helper.PATH_END}}})

    def test_parse(self):
        import six
        from google.cloud.firestore_v1beta1 import _helpers

        a_b_c = _helpers.FieldPath.from_string('a.b.c')
        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        field_updates = collections.OrderedDict((
            (a_b_c, 10),
            (_helpers.FieldPath.from_string('d'), None),
            (_helpers.FieldPath.from_string('e.f1'), [u'no', b'yes']),
            (_helpers.FieldPath.from_string('e.f2'), 4.5),
            (_helpers.FieldPath.from_string('e.f3'), (3, 1)),
            (_helpers.FieldPath.from_string('g'), {'key': True}),
            (_helpers.FieldPath('h', 'i'), '3'),
            (_helpers.FieldPath('j.k', 'l.m'), set(['2', '3'])),
            (_helpers.FieldPath('a', '一'), {1: 2}),
            (_helpers.FieldPath('a.一'), {3: 4}),
        ))
        helper = self._make_one(field_updates)
        update_values, field_paths = helper.parse()
        expected_updates = {
            'a': {
                'b': {
                    'c': field_updates[a_b_c],
                },
                '一': field_updates[_helpers.FieldPath('a', '一')]
            },
            'd': field_updates[_helpers.FieldPath.from_string('d')],
            'e': {
                'f1': field_updates[_helpers.FieldPath.from_string('e.f1')],
                'f2': field_updates[_helpers.FieldPath.from_string('e.f2')],
                'f3': field_updates[_helpers.FieldPath.from_string('e.f3')]
            },
            'g': field_updates[_helpers.FieldPath.from_string('g')],
            'h': {
                'i': field_updates[_helpers.FieldPath('h', 'i')]
            },
            'j.k': {
                'l.m': field_updates[_helpers.FieldPath('j.k', 'l.m')]
            },
            'a.一': field_updates[_helpers.FieldPath('a.一')]
        }
        self.assertEqual(update_values, expected_updates)
        self.assertEqual(field_paths, list(six.iterkeys(field_updates)))

    def test_parse_with_delete(self):
        from google.cloud.firestore_v1beta1.constants import DELETE_FIELD

        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        field_updates = collections.OrderedDict((
            ('a', 10),
            ('b', DELETE_FIELD),
        ))
        helper = self._make_one(field_updates)
        update_values, field_paths = helper.parse()
        self.assertEqual(update_values, {'a': field_updates['a']})
        self.assertEqual(
            [field_path.parts[0] for field_path in field_paths],
            list(field_updates.keys())
        )

    def test_parse_with_conflict(self):
        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        field_updates = collections.OrderedDict((
            ('a.b.c', b'\x01\x02'),
            ('a.b', {'d': 900}),
        ))
        helper = self._make_one(field_updates)
        with self.assertRaises(ValueError) as exc_info:
            helper.parse()

        err_msg = helper.FIELD_PATH_CONFLICT.format('a.b', 'a.b.c')
        self.assertEqual(exc_info.exception.args, (err_msg,))

    def test_to_field_paths(self):
        from google.cloud.firestore_v1beta1 import _helpers

        field_path = _helpers.FieldPath.from_string('a.b')
        field_updates = {field_path: 99}
        klass = self._get_target_class()

        update_values, field_paths = klass.to_field_paths(field_updates)
        self.assertEqual(
            update_values, {'a': {'b': field_updates[field_path]}})
        self.assertEqual(field_paths, [field_path])

    def test_conflict_same_field_paths(self):
        from google.cloud.firestore_v1beta1 import _helpers

        field_path_from_string = _helpers.FieldPath.from_string('a.b')
        field_path_class = _helpers.FieldPath('a', 'b')
        # User error in this case
        field_updates = {field_path_from_string: '',
                         field_path_class: ''}
        self.assertEqual(field_path_from_string, field_path_class)
        self.assertEqual(len(field_updates), 1)


class Test_verify_path(unittest.TestCase):

    @staticmethod
    def _call_fut(path, is_collection):
        from google.cloud.firestore_v1beta1._helpers import verify_path

        return verify_path(path, is_collection)

    def test_empty(self):
        path = ()
        with self.assertRaises(ValueError):
            self._call_fut(path, True)
        with self.assertRaises(ValueError):
            self._call_fut(path, False)

    def test_wrong_length_collection(self):
        path = ('foo', 'bar')
        with self.assertRaises(ValueError):
            self._call_fut(path, True)

    def test_wrong_length_document(self):
        path = ('Kind',)
        with self.assertRaises(ValueError):
            self._call_fut(path, False)

    def test_wrong_type_collection(self):
        path = (99, 'ninety-nine', 'zap')
        with self.assertRaises(ValueError):
            self._call_fut(path, True)

    def test_wrong_type_document(self):
        path = ('Users', 'Ada', 'Candy', {})
        with self.assertRaises(ValueError):
            self._call_fut(path, False)

    def test_success_collection(self):
        path = ('Computer', 'Magic', 'Win')
        ret_val = self._call_fut(path, True)
        # NOTE: We are just checking that it didn't fail.
        self.assertIsNone(ret_val)

    def test_success_document(self):
        path = ('Tokenizer', 'Seventeen', 'Cheese', 'Burger')
        ret_val = self._call_fut(path, False)
        # NOTE: We are just checking that it didn't fail.
        self.assertIsNone(ret_val)


class Test_encode_value(unittest.TestCase):

    @staticmethod
    def _call_fut(value):
        from google.cloud.firestore_v1beta1._helpers import encode_value

        return encode_value(value)

    def test_none(self):
        from google.protobuf import struct_pb2

        result = self._call_fut(None)
        expected = _value_pb(null_value=struct_pb2.NULL_VALUE)
        self.assertEqual(result, expected)

    def test_boolean(self):
        result = self._call_fut(True)
        expected = _value_pb(boolean_value=True)
        self.assertEqual(result, expected)

    def test_integer(self):
        value = 425178
        result = self._call_fut(value)
        expected = _value_pb(integer_value=value)
        self.assertEqual(result, expected)

    def test_float(self):
        value = 123.4453125
        result = self._call_fut(value)
        expected = _value_pb(double_value=value)
        self.assertEqual(result, expected)

    def test_datetime(self):
        from google.protobuf import timestamp_pb2

        dt_seconds = 1488768504
        dt_nanos = 458816000
        # Make sure precision is valid in microseconds too.
        self.assertEqual(dt_nanos % 1000, 0)
        dt_val = datetime.datetime.utcfromtimestamp(
            dt_seconds + 1e-9 * dt_nanos)

        result = self._call_fut(dt_val)
        timestamp_pb = timestamp_pb2.Timestamp(
            seconds=dt_seconds,
            nanos=dt_nanos,
        )
        expected = _value_pb(timestamp_value=timestamp_pb)
        self.assertEqual(result, expected)

    def test_string(self):
        value = u'\u2018left quote, right quote\u2019'
        result = self._call_fut(value)
        expected = _value_pb(string_value=value)
        self.assertEqual(result, expected)

    def test_bytes(self):
        value = b'\xe3\xf2\xff\x00'
        result = self._call_fut(value)
        expected = _value_pb(bytes_value=value)
        self.assertEqual(result, expected)

    def test_reference_value(self):
        client = _make_client()

        value = client.document('my', 'friend')
        result = self._call_fut(value)
        expected = _value_pb(reference_value=value._document_path)
        self.assertEqual(result, expected)

    def test_geo_point(self):
        from google.cloud.firestore_v1beta1._helpers import GeoPoint

        value = GeoPoint(50.5, 88.75)
        result = self._call_fut(value)
        expected = _value_pb(geo_point_value=value.to_protobuf())
        self.assertEqual(result, expected)

    def test_array(self):
        from google.cloud.firestore_v1beta1.proto.document_pb2 import (
            ArrayValue)

        result = self._call_fut([
            99,
            True,
            118.5
        ])

        array_pb = ArrayValue(values=[
            _value_pb(integer_value=99),
            _value_pb(boolean_value=True),
            _value_pb(double_value=118.5),
        ])
        expected = _value_pb(array_value=array_pb)
        self.assertEqual(result, expected)

    def test_map(self):
        from google.cloud.firestore_v1beta1.proto.document_pb2 import MapValue

        result = self._call_fut({
            'abc': 285,
            'def': b'piglatin',
        })

        map_pb = MapValue(fields={
            'abc': _value_pb(integer_value=285),
            'def': _value_pb(bytes_value=b'piglatin'),
        })
        expected = _value_pb(map_value=map_pb)
        self.assertEqual(result, expected)

    def test_bad_type(self):
        value = object()
        with self.assertRaises(TypeError):
            self._call_fut(value)


class Test_encode_dict(unittest.TestCase):

    @staticmethod
    def _call_fut(values_dict):
        from google.cloud.firestore_v1beta1._helpers import encode_dict

        return encode_dict(values_dict)

    def test_many_types(self):
        from google.protobuf import struct_pb2
        from google.protobuf import timestamp_pb2
        from google.cloud.firestore_v1beta1.proto.document_pb2 import (
            ArrayValue)
        from google.cloud.firestore_v1beta1.proto.document_pb2 import MapValue

        dt_seconds = 1497397225
        dt_nanos = 465964000
        # Make sure precision is valid in microseconds too.
        self.assertEqual(dt_nanos % 1000, 0)
        dt_val = datetime.datetime.utcfromtimestamp(
            dt_seconds + 1e-9 * dt_nanos)

        client = _make_client()
        document = client.document('most', 'adjective', 'thing', 'here')

        values_dict = {
            'foo': None,
            'bar': True,
            'baz': 981,
            'quux': 2.875,
            'quuz': dt_val,
            'corge': u'\N{snowman}',
            'grault': b'\xe2\x98\x83',
            'wibble': document,
            'garply': [
                u'fork',
                4.0,
            ],
            'waldo': {
                'fred': u'zap',
                'thud': False,
            },
        }
        encoded_dict = self._call_fut(values_dict)
        expected_dict = {
            'foo': _value_pb(null_value=struct_pb2.NULL_VALUE),
            'bar': _value_pb(boolean_value=True),
            'baz': _value_pb(integer_value=981),
            'quux': _value_pb(double_value=2.875),
            'quuz': _value_pb(timestamp_value=timestamp_pb2.Timestamp(
                seconds=dt_seconds,
                nanos=dt_nanos,
            )),
            'corge': _value_pb(string_value=u'\N{snowman}'),
            'grault': _value_pb(bytes_value=b'\xe2\x98\x83'),
            'wibble': _value_pb(reference_value=document._document_path),
            'garply': _value_pb(array_value=ArrayValue(values=[
                _value_pb(string_value=u'fork'),
                _value_pb(double_value=4.0),
            ])),
            'waldo': _value_pb(map_value=MapValue(fields={
                'fred': _value_pb(string_value=u'zap'),
                'thud': _value_pb(boolean_value=False),
            })),
        }
        self.assertEqual(encoded_dict, expected_dict)


class Test_extract_field_paths(unittest.TestCase):

    @staticmethod
    def _call_fut(document):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.extract_field_paths(document)

    @staticmethod
    def _make_field_path(dotted):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.FieldPath.from_string(dotted)

    def test_w_empty_document(self):
        document = {}
        expected = []
        self.assertEqual(self._call_fut(document), expected)

    def test_w_non_dict_value(self):
        document = {'a': 'b'}
        expected = [self._make_field_path('a')]
        self.assertEqual(self._call_fut(document), expected)

    def test_w_dict_value(self):
        document = {'a': {'b': 'c'}}
        expected = [self._make_field_path('a.b')]
        self.assertEqual(self._call_fut(document), expected)


class Test_filter_document_data_by_field_paths(unittest.TestCase):

    @staticmethod
    def _call_fut(document_data, field_paths):
        from google.cloud.firestore_v1beta1._helpers import (
            filter_document_data_by_field_paths,
            )

        return filter_document_data_by_field_paths(document_data, field_paths)

    def test_w_leaf_child(self):
        document = {'a': {'b': {'c': 1, 'd': 2}}, 'x': 1}
        field_paths = ['a.b.c']
        expected = {'a': {'b': {'c': 1}}}
        self.assertEqual(self._call_fut(document, field_paths), expected)

    def test_w_non_leaf_child(self):
        document = {'a': {'b': {'c': 1, 'd': 2}}, 'x': 1}
        field_paths = ['a.b']
        expected = {'a': {'b': {'c': 1, 'd': 2}}}
        self.assertEqual(self._call_fut(document, field_paths), expected)

    def test_w_root(self):
        document = {'a': {'b': {'c': 1, 'd': 2}}, 'x': 1}
        field_paths = ['a']
        expected = {'a': {'b': {'c': 1, 'd': 2}}}
        self.assertEqual(self._call_fut(document, field_paths), expected)

    def test_w_multiple_leaves(self):
        document = {'h': {'f': 5, 'g': 6}, 'e': 7}
        field_paths = ['h.f', 'h.g']
        expected = {'h': {'f': 5, 'g': 6}}
        self.assertEqual(self._call_fut(document, field_paths), expected)


class Test_reference_value_to_document(unittest.TestCase):

    @staticmethod
    def _call_fut(reference_value, client):
        from google.cloud.firestore_v1beta1._helpers import (
            reference_value_to_document)

        return reference_value_to_document(reference_value, client)

    def test_bad_format(self):
        from google.cloud.firestore_v1beta1._helpers import BAD_REFERENCE_ERROR

        reference_value = 'not/the/right/format'
        with self.assertRaises(ValueError) as exc_info:
            self._call_fut(reference_value, None)

        err_msg = BAD_REFERENCE_ERROR.format(reference_value)
        self.assertEqual(exc_info.exception.args, (err_msg,))

    def test_same_client(self):
        from google.cloud.firestore_v1beta1.document import DocumentReference

        client = _make_client()
        document = client.document('that', 'this')
        reference_value = document._document_path

        new_document = self._call_fut(reference_value, client)
        self.assertIsNot(new_document, document)

        self.assertIsInstance(new_document, DocumentReference)
        self.assertIs(new_document._client, client)
        self.assertEqual(new_document._path, document._path)

    def test_different_client(self):
        from google.cloud.firestore_v1beta1._helpers import WRONG_APP_REFERENCE

        client1 = _make_client(project='kirk')
        document = client1.document('tin', 'foil')
        reference_value = document._document_path

        client2 = _make_client(project='spock')
        with self.assertRaises(ValueError) as exc_info:
            self._call_fut(reference_value, client2)

        err_msg = WRONG_APP_REFERENCE.format(
            reference_value, client2._database_string)
        self.assertEqual(exc_info.exception.args, (err_msg,))


class Test_decode_value(unittest.TestCase):

    @staticmethod
    def _call_fut(value, client=mock.sentinel.client):
        from google.cloud.firestore_v1beta1._helpers import decode_value

        return decode_value(value, client)

    def test_none(self):
        from google.protobuf import struct_pb2

        value = _value_pb(null_value=struct_pb2.NULL_VALUE)
        self.assertIsNone(self._call_fut(value))

    def test_bool(self):
        value1 = _value_pb(boolean_value=True)
        self.assertTrue(self._call_fut(value1))
        value2 = _value_pb(boolean_value=False)
        self.assertFalse(self._call_fut(value2))

    def test_int(self):
        int_val = 29871
        value = _value_pb(integer_value=int_val)
        self.assertEqual(self._call_fut(value), int_val)

    def test_float(self):
        float_val = 85.9296875
        value = _value_pb(double_value=float_val)
        self.assertEqual(self._call_fut(value), float_val)

    @unittest.skipIf((3,) <= sys.version_info < (3, 4, 4),
                     'known datetime bug (bpo-23517) in Python')
    def test_datetime(self):
        from google.protobuf import timestamp_pb2
        from google.cloud._helpers import UTC

        dt_seconds = 552855006
        dt_nanos = 766961000
        # Make sure precision is valid in microseconds too.
        self.assertEqual(dt_nanos % 1000, 0)

        timestamp_pb = timestamp_pb2.Timestamp(
            seconds=dt_seconds,
            nanos=dt_nanos,
        )
        value = _value_pb(timestamp_value=timestamp_pb)

        expected_dt_val = datetime.datetime.utcfromtimestamp(
            dt_seconds + 1e-9 * dt_nanos).replace(tzinfo=UTC)
        self.assertEqual(self._call_fut(value), expected_dt_val)

    def test_unicode(self):
        unicode_val = u'zorgon'
        value = _value_pb(string_value=unicode_val)
        self.assertEqual(self._call_fut(value), unicode_val)

    def test_bytes(self):
        bytes_val = b'abc\x80'
        value = _value_pb(bytes_value=bytes_val)
        self.assertEqual(self._call_fut(value), bytes_val)

    def test_reference(self):
        from google.cloud.firestore_v1beta1.document import DocumentReference

        client = _make_client()
        path = (u'then', u'there-was-one')
        document = client.document(*path)
        ref_string = document._document_path
        value = _value_pb(reference_value=ref_string)

        result = self._call_fut(value, client)
        self.assertIsInstance(result, DocumentReference)
        self.assertIs(result._client, client)
        self.assertEqual(result._path, path)

    def test_geo_point(self):
        from google.cloud.firestore_v1beta1._helpers import GeoPoint

        geo_pt = GeoPoint(latitude=42.5, longitude=99.0625)
        value = _value_pb(geo_point_value=geo_pt.to_protobuf())
        self.assertEqual(self._call_fut(value), geo_pt)

    def test_array(self):
        from google.cloud.firestore_v1beta1.proto import document_pb2

        sub_value1 = _value_pb(boolean_value=True)
        sub_value2 = _value_pb(double_value=14.1396484375)
        sub_value3 = _value_pb(bytes_value=b'\xde\xad\xbe\xef')
        array_pb = document_pb2.ArrayValue(
            values=[sub_value1, sub_value2, sub_value3])
        value = _value_pb(array_value=array_pb)

        expected = [
            sub_value1.boolean_value,
            sub_value2.double_value,
            sub_value3.bytes_value,
        ]
        self.assertEqual(self._call_fut(value), expected)

    def test_map(self):
        from google.cloud.firestore_v1beta1.proto import document_pb2

        sub_value1 = _value_pb(integer_value=187680)
        sub_value2 = _value_pb(string_value=u'how low can you go?')
        map_pb = document_pb2.MapValue(fields={
            'first': sub_value1,
            'second': sub_value2,
        })
        value = _value_pb(map_value=map_pb)

        expected = {
            'first': sub_value1.integer_value,
            'second': sub_value2.string_value,
        }
        self.assertEqual(self._call_fut(value), expected)

    def test_nested_map(self):
        from google.cloud.firestore_v1beta1.proto import document_pb2

        actual_value1 = 1009876
        actual_value2 = u'hey you guys'
        actual_value3 = 90.875
        map_pb1 = document_pb2.MapValue(fields={
            'lowest': _value_pb(integer_value=actual_value1),
            'aside': _value_pb(string_value=actual_value2),
        })
        map_pb2 = document_pb2.MapValue(fields={
            'middle': _value_pb(map_value=map_pb1),
            'aside': _value_pb(boolean_value=True),
        })
        map_pb3 = document_pb2.MapValue(fields={
            'highest': _value_pb(map_value=map_pb2),
            'aside': _value_pb(double_value=actual_value3),
        })
        value = _value_pb(map_value=map_pb3)

        expected = {
            'highest': {
                'middle': {
                    'lowest': actual_value1,
                    'aside': actual_value2,
                },
                'aside': True,
            },
            'aside': actual_value3,
        }
        self.assertEqual(self._call_fut(value), expected)

    def test_unset_value_type(self):
        with self.assertRaises(ValueError):
            self._call_fut(_value_pb())

    def test_unknown_value_type(self):
        value_pb = mock.Mock(spec=['WhichOneof'])
        value_pb.WhichOneof.return_value = 'zoob_value'

        with self.assertRaises(ValueError):
            self._call_fut(value_pb)

        value_pb.WhichOneof.assert_called_once_with('value_type')


class Test_decode_dict(unittest.TestCase):

    @staticmethod
    def _call_fut(value_fields, client=mock.sentinel.client):
        from google.cloud.firestore_v1beta1._helpers import decode_dict

        return decode_dict(value_fields, client)

    @unittest.skipIf((3,) <= sys.version_info < (3, 4, 4),
                     'known datetime bug (bpo-23517) in Python')
    def test_many_types(self):
        from google.protobuf import struct_pb2
        from google.protobuf import timestamp_pb2
        from google.cloud.firestore_v1beta1.proto.document_pb2 import (
            ArrayValue)
        from google.cloud.firestore_v1beta1.proto.document_pb2 import MapValue
        from google.cloud._helpers import UTC
        from google.cloud.firestore_v1beta1._helpers import FieldPath

        dt_seconds = 1394037350
        dt_nanos = 667285000
        # Make sure precision is valid in microseconds too.
        self.assertEqual(dt_nanos % 1000, 0)
        dt_val = datetime.datetime.utcfromtimestamp(
            dt_seconds + 1e-9 * dt_nanos).replace(tzinfo=UTC)

        value_fields = {
            'foo': _value_pb(null_value=struct_pb2.NULL_VALUE),
            'bar': _value_pb(boolean_value=True),
            'baz': _value_pb(integer_value=981),
            'quux': _value_pb(double_value=2.875),
            'quuz': _value_pb(timestamp_value=timestamp_pb2.Timestamp(
                seconds=dt_seconds,
                nanos=dt_nanos,
            )),
            'corge': _value_pb(string_value=u'\N{snowman}'),
            'grault': _value_pb(bytes_value=b'\xe2\x98\x83'),
            'garply': _value_pb(array_value=ArrayValue(values=[
                _value_pb(string_value=u'fork'),
                _value_pb(double_value=4.0),
            ])),
            'waldo': _value_pb(map_value=MapValue(fields={
                'fred': _value_pb(string_value=u'zap'),
                'thud': _value_pb(boolean_value=False),
            })),
            FieldPath('a', 'b', 'c').to_api_repr():
            _value_pb(boolean_value=False)
        }
        expected = {
            'foo': None,
            'bar': True,
            'baz': 981,
            'quux': 2.875,
            'quuz': dt_val,
            'corge': u'\N{snowman}',
            'grault': b'\xe2\x98\x83',
            'garply': [
                u'fork',
                4.0,
            ],
            'waldo': {
                'fred': u'zap',
                'thud': False,
            },
            'a.b.c': False
        }
        self.assertEqual(self._call_fut(value_fields), expected)


class Test_get_field_path(unittest.TestCase):

    @staticmethod
    def _call_fut(field_names):
        from google.cloud.firestore_v1beta1._helpers import get_field_path

        return get_field_path(field_names)

    def test_w_empty(self):
        self.assertEqual(self._call_fut([]), '')

    def test_w_one_simple(self):
        self.assertEqual(self._call_fut(['a']), 'a')

    def test_w_one_starts_w_digit(self):
        self.assertEqual(self._call_fut(['0abc']), '`0abc`')

    def test_w_one_w_non_alphanum(self):
        self.assertEqual(self._call_fut(['a b c']), '`a b c`')

    def test_w_one_w_backtick(self):
        self.assertEqual(self._call_fut(['a`b']), '`a\\`b`')

    def test_w_one_w_backslash(self):
        self.assertEqual(self._call_fut(['a\\b']), '`a\\\\b`')

    def test_multiple(self):
        self.assertEqual(self._call_fut(['a', 'b', 'c']), 'a.b.c')


class Test_parse_field_path(unittest.TestCase):

    @staticmethod
    def _call_fut(field_path):
        from google.cloud.firestore_v1beta1._helpers import parse_field_path

        return parse_field_path(field_path)

    def test_wo_escaped_names(self):
        self.assertEqual(self._call_fut('a.b.c'), ['a', 'b', 'c'])

    def test_w_escaped_backtick(self):
        self.assertEqual(self._call_fut('`a\\`b`.c.d'), ['a`b', 'c', 'd'])

    def test_w_escaped_backslash(self):
        self.assertEqual(self._call_fut('`a\\\\b`.c.d'), ['a\\b', 'c', 'd'])


class Test__parse_field_name(unittest.TestCase):

    @staticmethod
    def _call_fut(field_path):
        from google.cloud.firestore_v1beta1._helpers import _parse_field_name

        return _parse_field_name(field_path)

    def test_w_no_dots(self):
        name, rest = self._call_fut('a')
        self.assertEqual(name, 'a')
        self.assertIsNone(rest)

    def test_w_first_name_simple(self):
        name, rest = self._call_fut('a.b.c')
        self.assertEqual(name, 'a')
        self.assertEqual(rest, 'b.c')

    def test_w_first_name_escaped_no_escapse(self):
        name, rest = self._call_fut('`3`.b.c')
        self.assertEqual(name, '`3`')
        self.assertEqual(rest, 'b.c')

    def test_w_first_name_escaped_w_escaped_backtick(self):
        name, rest = self._call_fut('`a\\`b`.c.d')
        self.assertEqual(name, '`a\\`b`')
        self.assertEqual(rest, 'c.d')

    def test_w_first_name_escaped_wo_closing_backtick(self):
        with self.assertRaises(ValueError):
            self._call_fut('`a\\`b.c.d')


class Test_get_nested_value(unittest.TestCase):

    DATA = {
        'top1': {
            'middle2': {
                'bottom3': 20,
                'bottom4': 22,
            },
            'middle5': True,
        },
        'top6': b'\x00\x01 foo',
    }

    @staticmethod
    def _call_fut(field_path, data):
        from google.cloud.firestore_v1beta1._helpers import get_nested_value

        return get_nested_value(field_path, data)

    def test_simple(self):
        self.assertIs(self._call_fut('top1', self.DATA), self.DATA['top1'])

    def test_nested(self):
        self.assertIs(
            self._call_fut('top1.middle2', self.DATA),
            self.DATA['top1']['middle2'])
        self.assertIs(
            self._call_fut('top1.middle2.bottom3', self.DATA),
            self.DATA['top1']['middle2']['bottom3'])

    def test_missing_top_level(self):
        from google.cloud.firestore_v1beta1._helpers import (
            FIELD_PATH_MISSING_TOP)

        field_path = 'top8'
        with self.assertRaises(KeyError) as exc_info:
            self._call_fut(field_path, self.DATA)

        err_msg = FIELD_PATH_MISSING_TOP.format(field_path)
        self.assertEqual(exc_info.exception.args, (err_msg,))

    def test_missing_key(self):
        from google.cloud.firestore_v1beta1._helpers import (
            FIELD_PATH_MISSING_KEY)

        with self.assertRaises(KeyError) as exc_info:
            self._call_fut('top1.middle2.nope', self.DATA)

        err_msg = FIELD_PATH_MISSING_KEY.format('nope', 'top1.middle2')
        self.assertEqual(exc_info.exception.args, (err_msg,))

    def test_bad_type(self):
        from google.cloud.firestore_v1beta1._helpers import (
            FIELD_PATH_WRONG_TYPE)

        with self.assertRaises(KeyError) as exc_info:
            self._call_fut('top6.middle7', self.DATA)

        err_msg = FIELD_PATH_WRONG_TYPE.format('top6', 'middle7')
        self.assertEqual(exc_info.exception.args, (err_msg,))


class Test_get_doc_id(unittest.TestCase):

    @staticmethod
    def _call_fut(document_pb, expected_prefix):
        from google.cloud.firestore_v1beta1._helpers import get_doc_id

        return get_doc_id(document_pb, expected_prefix)

    @staticmethod
    def _dummy_ref_string(collection_id):
        from google.cloud.firestore_v1beta1.client import DEFAULT_DATABASE

        project = u'bazzzz'
        return u'projects/{}/databases/{}/documents/{}'.format(
            project, DEFAULT_DATABASE, collection_id)

    def test_success(self):
        from google.cloud.firestore_v1beta1.proto import document_pb2

        prefix = self._dummy_ref_string('sub-collection')
        actual_id = 'this-is-the-one'
        name = '{}/{}'.format(prefix, actual_id)

        document_pb = document_pb2.Document(name=name)
        document_id = self._call_fut(document_pb, prefix)
        self.assertEqual(document_id, actual_id)

    def test_failure(self):
        from google.cloud.firestore_v1beta1.proto import document_pb2

        actual_prefix = self._dummy_ref_string('the-right-one')
        wrong_prefix = self._dummy_ref_string('the-wrong-one')
        name = '{}/{}'.format(actual_prefix, 'sorry-wont-works')

        document_pb = document_pb2.Document(name=name)
        with self.assertRaises(ValueError) as exc_info:
            self._call_fut(document_pb, wrong_prefix)

        exc_args = exc_info.exception.args
        self.assertEqual(len(exc_args), 4)
        self.assertEqual(exc_args[1], name)
        self.assertEqual(exc_args[3], wrong_prefix)


class Test_process_server_timestamp(unittest.TestCase):

    @staticmethod
    def _call_fut(document_data, split_on_dots):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.process_server_timestamp(
            document_data, split_on_dots=split_on_dots)

    def test_no_fields_w_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers

        data = collections.OrderedDict((
            ('one', 1),
            ('two', 2.25),
            ('three', [False, True, True]),
        ))
        expected_field_paths = [
            _helpers.FieldPath('one'),
            _helpers.FieldPath('two'),
            _helpers.FieldPath('three')
        ]
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=True)
        self.assertEqual(transform_paths, [])
        self.assertEqual(field_paths, expected_field_paths)
        self.assertIs(actual_data, data)

    def test_no_fields_wo_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers

        data = collections.OrderedDict((
            ('one', 1),
            ('two', 2.25),
            ('three', [False, True, True]),
        ))
        expected_field_paths = [
            _helpers.FieldPath('one'),
            _helpers.FieldPath('two'),
            _helpers.FieldPath('three')
        ]
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=False)
        self.assertEqual(transform_paths, [])
        self.assertEqual(field_paths, expected_field_paths)
        self.assertIs(actual_data, data)

    def test_simple_fields_w_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        nested1 = collections.OrderedDict((
            ('bottom2', SERVER_TIMESTAMP),
            ('bottom3', 1.5),
        ))
        nested2 = collections.OrderedDict((
            ('bottom7', SERVER_TIMESTAMP),
        ))
        data = collections.OrderedDict((
            ('top1', nested1),
            ('top4', SERVER_TIMESTAMP),
            ('top5', 200),
            ('top6', nested2),
        ))
        expected_transform_paths = [
            _helpers.FieldPath('top1', 'bottom2'),
            _helpers.FieldPath('top4'),
            _helpers.FieldPath('top6', 'bottom7')
        ]
        expected_field_paths = [
            _helpers.FieldPath('top1', 'bottom3'),
            _helpers.FieldPath('top5')]
        expected_data = {
            'top1': {
                'bottom3': data['top1']['bottom3'],
            },
            'top5': data['top5'],
        }
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=True)
        self.assertEqual(
            transform_paths,
            expected_transform_paths
        )
        self.assertEqual(field_paths, expected_field_paths)
        self.assertEqual(actual_data, expected_data)

    def test_simple_fields_wo_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        nested1 = collections.OrderedDict((
            ('bottom2', SERVER_TIMESTAMP),
            ('bottom3', 1.5),
        ))
        nested2 = collections.OrderedDict((
            ('bottom7', SERVER_TIMESTAMP),
        ))
        data = collections.OrderedDict((
            ('top1', nested1),
            ('top4', SERVER_TIMESTAMP),
            ('top5', 200),
            ('top6', nested2),
        ))
        expected_transform_paths = [
            _helpers.FieldPath('top1', 'bottom2'),
            _helpers.FieldPath('top4'),
            _helpers.FieldPath('top6', 'bottom7')
        ]
        expected_field_paths = [
            _helpers.FieldPath('top1', 'bottom3'),
            _helpers.FieldPath('top5')]
        expected_data = {
            'top1': {
                'bottom3': data['top1']['bottom3'],
            },
            'top5': data['top5'],
        }
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=False)
        self.assertEqual(
            transform_paths,
            expected_transform_paths
        )
        self.assertEqual(field_paths, expected_field_paths)
        self.assertEqual(actual_data, expected_data)

    def test_field_updates_w_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        data = collections.OrderedDict((
            ('a', {'b': 10}),
            ('c.d', {'e': SERVER_TIMESTAMP}),
            ('f.g', SERVER_TIMESTAMP),
        ))
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=True)
        self.assertEqual(transform_paths, [_helpers.FieldPath('c', 'd', 'e'),
                                           _helpers.FieldPath('f', 'g')])

        expected_data = {'a': {'b': data['a']['b']}}
        self.assertEqual(actual_data, expected_data)

    def test_field_updates_wo_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        data = collections.OrderedDict((
            ('a', {'b': 10}),
            ('c.d', {'e': SERVER_TIMESTAMP}),
            ('f.g', SERVER_TIMESTAMP),
        ))
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=False)
        self.assertEqual(transform_paths, [_helpers.FieldPath('c', 'd', 'e'),
                                           _helpers.FieldPath('f.g')])

        expected_data = {'a': {'b': data['a']['b']}}
        self.assertEqual(actual_data, expected_data)

    def test_field_updates_w_empty_value_w_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        data = collections.OrderedDict((
            ('a', {'b': 10}),
            ('c.d', {'e': SERVER_TIMESTAMP}),
            ('f.g', SERVER_TIMESTAMP),
            ('h', {}),
        ))
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=True)
        self.assertEqual(
            transform_paths,
            [_helpers.FieldPath('c', 'd', 'e'),
             _helpers.FieldPath('f', 'g')])

        expected_data = {'a': {'b': data['a']['b']}, 'h': {}}
        self.assertEqual(actual_data, expected_data)

    def test_field_updates_w_empty_value_wo_split_on_dots(self):
        import collections
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        # "Cheat" and use OrderedDict-s so that iteritems() is deterministic.
        data = collections.OrderedDict((
            ('a', {'b': 10}),
            ('c.d', {'e': SERVER_TIMESTAMP}),
            ('f.g', SERVER_TIMESTAMP),
            ('h', {}),
        ))
        transform_paths, actual_data, field_paths = self._call_fut(
            data, split_on_dots=False)
        self.assertEqual(
            transform_paths,
            [_helpers.FieldPath('c', 'd', 'e'),
             _helpers.FieldPath('f.g')])

        expected_data = {'a': {'b': data['a']['b']}, 'h': {}}
        self.assertEqual(actual_data, expected_data)


class Test_canonicalize_field_paths(unittest.TestCase):

    @staticmethod
    def _call_fut(field_paths):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.canonicalize_field_paths(field_paths)

    def _test_helper(self, to_convert):
        from google.cloud.firestore_v1beta1 import _helpers

        paths = [
            _helpers.FieldPath.from_string(path) for path in to_convert
        ]
        found = self._call_fut(paths)

        self.assertEqual(found, sorted(to_convert.values()))

    def test_w_native_strings(self):
        to_convert = {
            '0abc.deq': '`0abc`.deq',
            'abc.654': 'abc.`654`',
            '321.0deq._321': '`321`.`0deq`._321',
        }
        self._test_helper(to_convert)

    def test_w_unicode(self):
        to_convert = {
            u'0abc.deq': '`0abc`.deq',
            u'abc.654': 'abc.`654`',
            u'321.0deq._321': '`321`.`0deq`._321',
        }
        self._test_helper(to_convert)


class Test_get_transform_pb(unittest.TestCase):

    @staticmethod
    def _call_fut(document_path, transform_paths):
        from google.cloud.firestore_v1beta1._helpers import get_transform_pb

        return get_transform_pb(document_path, transform_paths)

    def test_it(self):
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.gapic import enums
        from google.cloud.firestore_v1beta1.proto import write_pb2

        document_path = _make_ref_string(
            u'cereal', u'deebee', u'buzzf', u'beep')
        transform_paths = [
            _helpers.FieldPath.from_string('man.bear'),
            _helpers.FieldPath.from_string('pig'),
            _helpers.FieldPath.from_string('apple.x.y')]
        transform_pb = self._call_fut(document_path, transform_paths)

        server_val = enums.DocumentTransform.FieldTransform.ServerValue
        transform1 = write_pb2.DocumentTransform.FieldTransform(
            field_path='apple.x.y',
            set_to_server_value=server_val.REQUEST_TIME,
        )
        transform2 = write_pb2.DocumentTransform.FieldTransform(
            field_path='man.bear',
            set_to_server_value=server_val.REQUEST_TIME,
        )
        transform3 = write_pb2.DocumentTransform.FieldTransform(
            field_path='pig',
            set_to_server_value=server_val.REQUEST_TIME,
        )

        expected_pb = write_pb2.Write(
            transform=write_pb2.DocumentTransform(
                document=document_path,
                field_transforms=[transform1, transform2, transform3],
            ),
        )
        self.assertEqual(transform_pb, expected_pb)


class Test_pbs_for_create(unittest.TestCase):

    @staticmethod
    def _call_fut(document_path, document_data):
        from google.cloud.firestore_v1beta1._helpers import pbs_for_create

        return pbs_for_create(document_path, document_data)

    @staticmethod
    def _make_write_w_document(document_path, **data):
        from google.cloud.firestore_v1beta1.proto import document_pb2
        from google.cloud.firestore_v1beta1.proto import write_pb2
        from google.cloud.firestore_v1beta1._helpers import encode_dict
        from google.cloud.firestore_v1beta1.proto import common_pb2

        return write_pb2.Write(
            update=document_pb2.Document(
                name=document_path,
                fields=encode_dict(data),
            ),
            current_document=common_pb2.Precondition(exists=False),
        )

    @staticmethod
    def _make_write_w_transform(document_path, fields):
        from google.cloud.firestore_v1beta1.proto import write_pb2
        from google.cloud.firestore_v1beta1.gapic import enums

        server_val = enums.DocumentTransform.FieldTransform.ServerValue
        transforms = [
            write_pb2.DocumentTransform.FieldTransform(
                field_path=field, set_to_server_value=server_val.REQUEST_TIME)
            for field in fields
        ]

        return write_pb2.Write(
            transform=write_pb2.DocumentTransform(
                document=document_path,
                field_transforms=transforms,
            ),
        )

    def _helper(self, do_transform=False, empty_val=False):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        document_data = {
            'cheese': 1.5,
            'crackers': True,
        }

        if do_transform:
            document_data['butter'] = SERVER_TIMESTAMP

        if empty_val:
            document_data['mustard'] = {}

        write_pbs = self._call_fut(document_path, document_data)

        if empty_val:
            update_pb = self._make_write_w_document(
                document_path, cheese=1.5, crackers=True, mustard={},
            )
        else:
            update_pb = self._make_write_w_document(
                document_path, cheese=1.5, crackers=True,
            )
        expected_pbs = [update_pb]

        if do_transform:
            expected_pbs.append(
                self._make_write_w_transform(document_path, fields=['butter']))

        self.assertEqual(write_pbs, expected_pbs)

    def test_without_transform(self):
        self._helper()

    def test_w_transform(self):
        self._helper(do_transform=True)

    def test_w_transform_and_empty_value(self):
        self._helper(do_transform=True, empty_val=True)


class Test_pbs_for_set_no_merge(unittest.TestCase):

    @staticmethod
    def _call_fut(document_path, document_data):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.pbs_for_set_no_merge(document_path, document_data)

    @staticmethod
    def _make_write_w_document(document_path, **data):
        from google.cloud.firestore_v1beta1.proto import document_pb2
        from google.cloud.firestore_v1beta1.proto import write_pb2
        from google.cloud.firestore_v1beta1._helpers import encode_dict

        return write_pb2.Write(
            update=document_pb2.Document(
                name=document_path,
                fields=encode_dict(data),
            ),
        )

    @staticmethod
    def _make_write_w_transform(document_path, fields):
        from google.cloud.firestore_v1beta1.proto import write_pb2
        from google.cloud.firestore_v1beta1.gapic import enums

        server_val = enums.DocumentTransform.FieldTransform.ServerValue
        transforms = [
            write_pb2.DocumentTransform.FieldTransform(
                field_path=field, set_to_server_value=server_val.REQUEST_TIME)
            for field in fields
        ]

        return write_pb2.Write(
            transform=write_pb2.DocumentTransform(
                document=document_path,
                field_transforms=transforms,
            ),
        )

    def test_w_empty_document(self):
        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        document_data = {}

        write_pbs = self._call_fut(document_path, document_data)

        update_pb = self._make_write_w_document(document_path)
        expected_pbs = [update_pb]
        self.assertEqual(write_pbs, expected_pbs)

    def test_w_only_server_timestamp(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        document_data = {'butter': SERVER_TIMESTAMP}

        write_pbs = self._call_fut(document_path, document_data)

        update_pb = self._make_write_w_document(document_path)
        transform_pb = self._make_write_w_transform(document_path, ['butter'])
        expected_pbs = [update_pb, transform_pb]
        self.assertEqual(write_pbs, expected_pbs)

    def _helper(self, do_transform=False, empty_val=False):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        document_data = {
            'cheese': 1.5,
            'crackers': True,
        }

        if do_transform:
            document_data['butter'] = SERVER_TIMESTAMP

        if empty_val:
            document_data['mustard'] = {}

        write_pbs = self._call_fut(document_path, document_data)

        if empty_val:
            update_pb = self._make_write_w_document(
                document_path, cheese=1.5, crackers=True, mustard={},
            )
        else:
            update_pb = self._make_write_w_document(
                document_path, cheese=1.5, crackers=True,
            )
        expected_pbs = [update_pb]

        if do_transform:
            expected_pbs.append(
                self._make_write_w_transform(document_path, fields=['butter']))

        self.assertEqual(write_pbs, expected_pbs)

    def test_defaults(self):
        self._helper()

    def test_w_transform(self):
        self._helper(do_transform=True)

    def test_w_transform_and_empty_value(self):
        # Exercise #5944
        self._helper(do_transform=True, empty_val=True)


class Test_all_merge_paths(unittest.TestCase):

    @staticmethod
    def _call_fut(document_data):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.all_merge_paths(document_data)

    @staticmethod
    def _make_field_path(*fields):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.FieldPath(*fields)

    def test_w_empty(self):
        document_data = {}

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data)

        self.assertEqual(transform_paths, [])
        self.assertEqual(actual_data, {})
        self.assertEqual(data_merge, [])
        self.assertEqual(transform_merge, [])
        self.assertEqual(merge, [])

    def test_w_simple(self):
        document_data = {'a': {'b': 'c'}}

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data)

        path = self._make_field_path('a', 'b')
        self.assertEqual(transform_paths, [])
        self.assertEqual(actual_data, document_data)
        self.assertEqual(data_merge, [path])
        self.assertEqual(transform_merge, [])
        self.assertEqual(merge, [path])

    def test_w_server_timestamp(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_data = {'a': {'b': SERVER_TIMESTAMP}}

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data)

        path = self._make_field_path('a', 'b')
        self.assertEqual(transform_paths, [path])
        self.assertEqual(actual_data, {})
        self.assertEqual(data_merge, [])
        self.assertEqual(transform_merge, [path])
        self.assertEqual(merge, [path])

    def test_w_simple_and_server_timestamp(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_data = {'a': {'b': 'd', 'c': SERVER_TIMESTAMP}}

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data)

        path_a_b = self._make_field_path('a', 'b')
        path_a_c = self._make_field_path('a', 'c')
        self.assertEqual(transform_paths, [path_a_c])
        self.assertEqual(actual_data, {'a': {'b': 'd'}})
        self.assertEqual(data_merge, [path_a_b])
        self.assertEqual(transform_merge, [path_a_c])
        self.assertEqual(merge, [path_a_b, path_a_c])


class Test_normalize_merge_paths(unittest.TestCase):

    @staticmethod
    def _call_fut(document_data, merge):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.normalize_merge_paths(document_data, merge)

    @staticmethod
    def _make_field_path(*fields):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.FieldPath(*fields)

    def test_w_empty_document_empty_merge_list(self):
        document_data = {}

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data, [])

        self.assertEqual(transform_paths, [])
        self.assertEqual(actual_data, {})
        self.assertEqual(data_merge, [])
        self.assertEqual(transform_merge, [])
        self.assertEqual(merge, [])

    def test_w_merge_path_miss(self):
        document_data = {}
        merge_path = self._make_field_path('a', 'b')

        with self.assertRaises(KeyError):
            self._call_fut(document_data, [merge_path])

    def test_w_merge_path_parent(self):
        document_data = {'a': {'b': 'c', 'd': 'e'}}

        with self.assertRaises(ValueError):
            self._call_fut(document_data, ['a', 'a.b'])

        with self.assertRaises(ValueError):
            self._call_fut(document_data, ['a.b', 'a'])

    def test_w_simple(self):
        document_data = {'a': {'b': 'c', 'd': 'e'}}
        merge_path = self._make_field_path('a', 'b')

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data, [merge_path])

        self.assertEqual(transform_paths, [])
        self.assertEqual(actual_data, {'a': {'b': 'c'}})
        self.assertEqual(data_merge, [merge_path])
        self.assertEqual(transform_merge, [])
        self.assertEqual(merge, [merge_path])

    def test_w_server_timestamp(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_data = {'a': {'b': SERVER_TIMESTAMP, 'c': 'd'}}
        merge_string = 'a.b'
        merge_path = self._make_field_path('a', 'b')

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data, [merge_string])

        self.assertEqual(transform_paths, [merge_path])
        self.assertEqual(actual_data, {})
        self.assertEqual(data_merge, [])
        self.assertEqual(transform_merge, [merge_path])
        self.assertEqual(merge, [merge_path])

    def test_w_simple_and_server_timestamp(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_data = {'a': {'b': SERVER_TIMESTAMP, 'c': 'd'}}
        merge_path = self._make_field_path('a')

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data, [merge_path])

        path_a_b = self._make_field_path('a', 'b')
        path_a_c = self._make_field_path('a', 'c')
        self.assertEqual(transform_paths, [path_a_b])
        self.assertEqual(actual_data, {'a': {'c': 'd'}})
        self.assertEqual(data_merge, [path_a_c])
        self.assertEqual(transform_merge, [])
        self.assertEqual(merge, [merge_path])

    def test_w_simple_and_server_timestamp_two_merge_paths(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_data = {'a': {'b': SERVER_TIMESTAMP, 'c': 'd'}}
        path_a_b = self._make_field_path('a', 'b')
        path_a_c = self._make_field_path('a', 'c')

        (
            transform_paths, actual_data, data_merge, transform_merge, merge,
        ) = self._call_fut(document_data, [path_a_b, path_a_c])

        self.assertEqual(transform_paths, [path_a_b])
        self.assertEqual(actual_data, {'a': {'c': 'd'}})
        self.assertEqual(data_merge, [path_a_c])
        self.assertEqual(transform_merge, [path_a_b])
        self.assertEqual(merge, [path_a_b, path_a_c])


class Test_pbs_for_set_with_merge(unittest.TestCase):

    @staticmethod
    def _call_fut(document_path, document_data, merge):
        from google.cloud.firestore_v1beta1 import _helpers

        return _helpers.pbs_for_set_with_merge(
            document_path, document_data, merge=merge)

    @staticmethod
    def _make_write_w_document(document_path, **data):
        from google.cloud.firestore_v1beta1.proto import document_pb2
        from google.cloud.firestore_v1beta1.proto import write_pb2
        from google.cloud.firestore_v1beta1._helpers import encode_dict

        return write_pb2.Write(
            update=document_pb2.Document(
                name=document_path,
                fields=encode_dict(data),
            ),
        )

    @staticmethod
    def _make_write_w_transform(document_path, fields):
        from google.cloud.firestore_v1beta1.proto import write_pb2
        from google.cloud.firestore_v1beta1.gapic import enums

        server_val = enums.DocumentTransform.FieldTransform.ServerValue
        transforms = [
            write_pb2.DocumentTransform.FieldTransform(
                field_path=field, set_to_server_value=server_val.REQUEST_TIME)
            for field in fields
        ]

        return write_pb2.Write(
            transform=write_pb2.DocumentTransform(
                document=document_path,
                field_transforms=transforms,
            ),
        )

    @staticmethod
    def _update_document_mask(update_pb, field_paths):
        from google.cloud.firestore_v1beta1.proto import common_pb2

        update_pb.update_mask.CopyFrom(
            common_pb2.DocumentMask(field_paths=field_paths))

    def test_with_merge_true_wo_transform(self):
        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        document_data = {
            'cheese': 1.5,
            'crackers': True,
        }

        write_pbs = self._call_fut(document_path, document_data, merge=True)

        update_pb = self._make_write_w_document(document_path, **document_data)
        self._update_document_mask(
            update_pb, field_paths=sorted(document_data))
        expected_pbs = [update_pb]
        self.assertEqual(write_pbs, expected_pbs)

    def test_with_merge_field_wo_transform(self):
        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        document_data = {
            'cheese': 1.5,
            'crackers': True,
        }

        write_pbs = self._call_fut(
            document_path, document_data, merge=['cheese'])

        update_pb = self._make_write_w_document(
            document_path, cheese=document_data['cheese'])
        self._update_document_mask(
            update_pb, field_paths=['cheese'])
        expected_pbs = [update_pb]
        self.assertEqual(write_pbs, expected_pbs)

    def test_with_merge_true_w_transform(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        update_data = {
            'cheese': 1.5,
            'crackers': True,
        }
        document_data = update_data.copy()
        document_data['butter'] = SERVER_TIMESTAMP

        write_pbs = self._call_fut(document_path, document_data, merge=True)

        update_pb = self._make_write_w_document(document_path, **update_data)
        self._update_document_mask(
            update_pb, field_paths=sorted(update_data))
        transform_pb = self._make_write_w_transform(
            document_path, fields=['butter'])
        expected_pbs = [
            update_pb,
            transform_pb,
        ]
        self.assertEqual(write_pbs, expected_pbs)

    def test_with_merge_field_w_transform(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        update_data = {
            'cheese': 1.5,
            'crackers': True,
        }
        document_data = update_data.copy()
        document_data['butter'] = SERVER_TIMESTAMP

        write_pbs = self._call_fut(
            document_path, document_data, merge=['cheese', 'butter'])

        update_pb = self._make_write_w_document(
            document_path, cheese=document_data['cheese'])
        self._update_document_mask(update_pb, ['cheese'])
        transform_pb = self._make_write_w_transform(
            document_path, fields=['butter'])
        expected_pbs = [
            update_pb,
            transform_pb,
        ]
        self.assertEqual(write_pbs, expected_pbs)

    def test_with_merge_field_w_transform_masking_simple(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        update_data = {
            'cheese': 1.5,
            'crackers': True,
        }
        document_data = update_data.copy()
        document_data['butter'] = {'pecan': SERVER_TIMESTAMP}

        write_pbs = self._call_fut(
            document_path, document_data, merge=['butter.pecan'])

        update_pb = self._make_write_w_document(document_path)
        transform_pb = self._make_write_w_transform(
            document_path, fields=['butter.pecan'])
        expected_pbs = [
            update_pb,
            transform_pb,
        ]
        self.assertEqual(write_pbs, expected_pbs)

    def test_with_merge_field_w_transform_parent(self):
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP

        document_path = _make_ref_string(u'little', u'town', u'of', u'ham')
        update_data = {
            'cheese': 1.5,
            'crackers': True,
        }
        document_data = update_data.copy()
        document_data['butter'] = {
            'popcorn': 'yum',
            'pecan': SERVER_TIMESTAMP,
        }

        write_pbs = self._call_fut(
            document_path, document_data, merge=['cheese', 'butter'])

        update_pb = self._make_write_w_document(
            document_path,
            cheese=update_data['cheese'],
            butter={'popcorn': 'yum'},
        )
        self._update_document_mask(update_pb, ['cheese', 'butter'])
        transform_pb = self._make_write_w_transform(
            document_path, fields=['butter.pecan'])
        expected_pbs = [
            update_pb,
            transform_pb,
        ]
        self.assertEqual(write_pbs, expected_pbs)


class Test_pbs_for_update(unittest.TestCase):

    @staticmethod
    def _call_fut(client, document_path, field_updates, option):
        from google.cloud.firestore_v1beta1._helpers import pbs_for_update

        return pbs_for_update(client, document_path, field_updates, option)

    def _helper(self, option=None, do_transform=False, **write_kwargs):
        from google.cloud.firestore_v1beta1 import _helpers
        from google.cloud.firestore_v1beta1.client import Client
        from google.cloud.firestore_v1beta1.client import ExistsOption
        from google.cloud.firestore_v1beta1.constants import SERVER_TIMESTAMP
        from google.cloud.firestore_v1beta1.gapic import enums
        from google.cloud.firestore_v1beta1.proto import common_pb2
        from google.cloud.firestore_v1beta1.proto import document_pb2
        from google.cloud.firestore_v1beta1.proto import write_pb2

        document_path = _make_ref_string(
            u'toy', u'car', u'onion', u'garlic')
        field_path1 = 'bitez.yum'
        value = b'\x00\x01'
        field_path2 = 'blog.internet'

        field_updates = {field_path1: value}
        if do_transform:
            field_updates[field_path2] = SERVER_TIMESTAMP

        # NOTE: ``Client.write_option()`` is a ``@staticmethod`` so
        #       we don't need a client instance.
        write_pbs = self._call_fut(
            Client, document_path, field_updates, option)

        map_pb = document_pb2.MapValue(fields={
            'yum': _value_pb(bytes_value=value),
        })

        if do_transform:
            field_paths = [field_path1, 'blog']
        else:
            field_paths = [field_path1]

        expected_update_pb = write_pb2.Write(
            update=document_pb2.Document(
                name=document_path,
                fields={'bitez': _value_pb(map_value=map_pb)},
            ),
            update_mask=common_pb2.DocumentMask(field_paths=field_paths),
            **write_kwargs
        )
        if isinstance(option, ExistsOption):
            precondition = common_pb2.Precondition(exists=False)
            expected_update_pb.current_document.CopyFrom(precondition)
        expected_pbs = [expected_update_pb]
        if do_transform:
            transform_paths = _helpers.FieldPath.from_string(field_path2)
            server_val = enums.DocumentTransform.FieldTransform.ServerValue
            expected_transform_pb = write_pb2.Write(
                transform=write_pb2.DocumentTransform(
                    document=document_path,
                    field_transforms=[
                        write_pb2.DocumentTransform.FieldTransform(
                            field_path=transform_paths.to_api_repr(),
                            set_to_server_value=server_val.REQUEST_TIME,
                        ),
                    ],
                ),
            )
            expected_pbs.append(expected_transform_pb)
        self.assertEqual(write_pbs, expected_pbs)

    def test_without_option(self):
        from google.cloud.firestore_v1beta1.proto import common_pb2

        precondition = common_pb2.Precondition(exists=True)
        self._helper(current_document=precondition)

    def test_with_exists_option(self):
        from google.cloud.firestore_v1beta1.client import ExistsOption

        option = ExistsOption(False)
        self._helper(option=option)

    def test_update_and_transform(self):
        from google.cloud.firestore_v1beta1.proto import common_pb2

        precondition = common_pb2.Precondition(exists=True)
        self._helper(current_document=precondition, do_transform=True)


class Test_pb_for_delete(unittest.TestCase):

    @staticmethod
    def _call_fut(document_path, option):
        from google.cloud.firestore_v1beta1._helpers import pb_for_delete

        return pb_for_delete(document_path, option)

    def _helper(self, option=None, **write_kwargs):
        from google.cloud.firestore_v1beta1.proto import write_pb2

        document_path = _make_ref_string(
            u'chicken', u'philly', u'one', u'two')
        write_pb = self._call_fut(document_path, option)

        expected_pb = write_pb2.Write(
            delete=document_path,
            **write_kwargs
        )
        self.assertEqual(write_pb, expected_pb)

    def test_without_option(self):
        self._helper()

    def test_with_option(self):
        from google.protobuf import timestamp_pb2
        from google.cloud.firestore_v1beta1.proto import common_pb2
        from google.cloud.firestore_v1beta1.client import LastUpdateOption

        update_time = timestamp_pb2.Timestamp(
            seconds=1309700594,
            nanos=822211297,
        )
        option = LastUpdateOption(update_time)
        precondition = common_pb2.Precondition(update_time=update_time)
        self._helper(option=option, current_document=precondition)


class Test_get_transaction_id(unittest.TestCase):

    @staticmethod
    def _call_fut(transaction, **kwargs):
        from google.cloud.firestore_v1beta1._helpers import get_transaction_id

        return get_transaction_id(transaction, **kwargs)

    def test_no_transaction(self):
        ret_val = self._call_fut(None)
        self.assertIsNone(ret_val)

    def test_invalid_transaction(self):
        from google.cloud.firestore_v1beta1.transaction import Transaction

        transaction = Transaction(mock.sentinel.client)
        self.assertFalse(transaction.in_progress)
        with self.assertRaises(ValueError):
            self._call_fut(transaction)

    def test_after_writes_not_allowed(self):
        from google.cloud.firestore_v1beta1._helpers import ReadAfterWriteError
        from google.cloud.firestore_v1beta1.transaction import Transaction

        transaction = Transaction(mock.sentinel.client)
        transaction._id = b'under-hook'
        transaction._write_pbs.append(mock.sentinel.write)

        with self.assertRaises(ReadAfterWriteError):
            self._call_fut(transaction)

    def test_after_writes_allowed(self):
        from google.cloud.firestore_v1beta1.transaction import Transaction

        transaction = Transaction(mock.sentinel.client)
        txn_id = b'we-are-0fine'
        transaction._id = txn_id
        transaction._write_pbs.append(mock.sentinel.write)

        ret_val = self._call_fut(transaction, read_operation=False)
        self.assertEqual(ret_val, txn_id)

    def test_good_transaction(self):
        from google.cloud.firestore_v1beta1.transaction import Transaction

        transaction = Transaction(mock.sentinel.client)
        txn_id = b'doubt-it'
        transaction._id = txn_id
        self.assertTrue(transaction.in_progress)

        self.assertEqual(self._call_fut(transaction), txn_id)


class Test_metadata_with_prefix(unittest.TestCase):

    @staticmethod
    def _call_fut(database_string):
        from google.cloud.firestore_v1beta1._helpers import (
            metadata_with_prefix)

        return metadata_with_prefix(database_string)

    def test_it(self):
        database_string = u'projects/prahj/databases/dee-bee'
        metadata = self._call_fut(database_string)

        self.assertEqual(metadata, [
            ('google-cloud-resource-prefix', database_string),
        ])


def _value_pb(**kwargs):
    from google.cloud.firestore_v1beta1.proto.document_pb2 import Value

    return Value(**kwargs)


def _make_ref_string(project, database, *path):
    from google.cloud.firestore_v1beta1 import _helpers

    doc_rel_path = _helpers.DOCUMENT_PATH_DELIMITER.join(path)
    return u'projects/{}/databases/{}/documents/{}'.format(
        project, database, doc_rel_path)


def _make_credentials():
    import google.auth.credentials

    return mock.Mock(spec=google.auth.credentials.Credentials)


def _make_client(project='quark'):
    from google.cloud.firestore_v1beta1.client import Client

    credentials = _make_credentials()
    return Client(project=project, credentials=credentials)
