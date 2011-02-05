# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import re

import pytest

from synaptiks import xinput


def pytest_funcarg__test_keyboard(request):
    """
    The virtual testing keyboard as :class:`synaptiks.xinput.InputDevice`.
    """
    display = request.getfuncargvalue('display')
    return next(xinput.InputDevice.find_devices_by_name(
        display, 'Virtual core XTEST keyboard'))


def pytest_funcarg__test_pointer(request):
    """
    The virtual testing pointer as :class:`synaptiks.xinput.InputDevice`.
    """
    display = request.getfuncargvalue('display')
    return next(xinput.InputDevice.find_devices_by_name(
        display, 'Virtual core XTEST pointer'))


def pytest_funcarg__test_device_properties(request):
    """
    A list of all properties defined on XTEST devices.
    """
    return ['Device Enabled', 'Coordinate Transformation Matrix',
            'XTEST Device']


def pytest_funcarg__touchpad(request):
    """
    The touchpad as :class:`synaptiks.xinput.InputDevice`.
    """
    display = request.getfuncargvalue('display')
    return next(xinput.InputDevice.find_devices_with_property(
        display, 'Synaptics Off'))


def test_assert_xinput_version(display):
    # just check, that no unexpected exception is raised
    try:
        xinput.assert_xinput_version(display)
    except xinput.XInputVersionError:
        # this is an expected exception
        pass


def test_is_property_defined_existing_property(display):
    assert xinput.is_property_defined(display, 'Device Enabled')
    assert xinput.is_property_defined(display, u'Device Enabled')


def test_inputdevice_all_devices(display):
    devices = list(xinput.InputDevice.all_devices(display))
    assert devices
    assert all(isinstance(d, xinput.InputDevice) for d in devices)
    assert all(d.id for d in devices)
    assert all(d.name for d in devices)
    # assert self-identity
    assert all(d == d for d in devices)
    assert all(not (d != d) for d in devices)


def test_inputdevice_find_devices_by_name_existing_devices(display):
    name = 'Virtual core XTEST keyboard'
    devices = list(xinput.InputDevice.find_devices_by_name(display, name))
    assert len(devices) == 1
    assert devices[0].name == name


def test_inputdevice_find_devices_by_name_non_existing(display):
    name = 'a non-existing device'
    devices = list(xinput.InputDevice.find_devices_by_name(display, name))
    assert not devices


def test_inputdevice_find_devices_by_name_existing_devices_regex(display):
    pattern = re.compile('.*XTEST.*')
    devices = list(xinput.InputDevice.find_devices_by_name(display, pattern))
    assert devices
    assert all('XTEST' in d.name for d in devices)


def test_inputdevice_eq_ne(test_keyboard, test_pointer):
    assert test_keyboard == test_keyboard
    assert test_keyboard != test_pointer


def test_inputdevice_iter(test_keyboard, test_device_properties):
    assert set(test_keyboard) == set(test_device_properties)


def test_inputdevice_len(test_keyboard, test_device_properties):
    assert len(test_keyboard) == len(test_device_properties)


def test_inputdevice_contains(test_keyboard, test_device_properties):
    assert all(p in test_keyboard for p in test_device_properties)


def test_inputdevice_contains_undefined_property(test_keyboard):
    assert not 'a undefined property' in test_keyboard


def test_inputdevice_getitem(test_keyboard):
    assert test_keyboard['Device Enabled'] == [1]
    assert test_keyboard['XTEST Device'] == [1]
    assert test_keyboard['Coordinate Transformation Matrix'] == \
           [1., 0., 0., 0., 1., 0., 0., 0., 1.]


def test_inputdevice_getitem_non_defined_property(test_keyboard):
    with pytest.raises(xinput.UndefinedPropertyError) as excinfo:
        test_keyboard['a undefined property']
    assert excinfo.value.name == 'a undefined property'


def test_inputdevice_getitem_non_existing_property(test_keyboard):
    with pytest.raises(KeyError) as excinfo:
        test_keyboard['Button Labels']
    assert not isinstance(excinfo.value, xinput.UndefinedPropertyError)


def test_input_device_set_bool_alias():
    assert xinput.InputDevice.set_bool == xinput.InputDevice.set_byte


def test_input_device_set_byte(test_keyboard):
    property = 'Device Enabled'
    assert test_keyboard[property] == [1]
    test_keyboard.set_byte(property, [0])
    assert test_keyboard[property] == [0]
    test_keyboard.set_byte(property, [1])
    assert test_keyboard[property] == [1]


def test_input_device_set_float(touchpad):
    property = 'Synaptics Circular Scrolling Distance'
    orig_value = touchpad[property]
    touchpad.set_float(property, [1.0])
    assert touchpad[property] == [1.0]
    touchpad.set_float(property, orig_value)
    assert touchpad[property] == orig_value