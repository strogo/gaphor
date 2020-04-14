"""Test case that checks the working of the autocoder.py module."""

from gaphor.application import distribution
from gaphor.codegen.autocoder import generate
from gaphor.codegen.override import Overrides


class PseudoFile:
    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data

    def close(self):
        pass


def test_loading():
    model_file = distribution().locate_file("test-models/test-model.gaphor")
    outfile = PseudoFile()

    generate(model_file, outfile)

    assert outfile.data == GENERATED, f'"""{outfile.data}"""'


GENERATED = """# This file is generated by codegen.py. DO NOT EDIT!

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Callable, List, Optional

from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.element import Element
from gaphor.core.modeling.properties import (
    association,
    attribute,
    derived,
    derivedunion,
    enumeration,
    redefine,
    relation_many,
    relation_one,
)
class Element:
    pass


class SubClass(Element):
    name2: relation_many[C]
    concrete: relation_many[D]
    value: attribute[str]
    abstract: relation_many[C]
    name4: relation_many[D]  # type: ignore[assignment]


class C:
    attr: attribute[str]
    name1: relation_many[SubClass]
    base: relation_many[SubClass]


class D(C):
    subbase: relation_many[SubClass]
    name3: relation_many[SubClass]


# class 'ValSpec' has been stereotyped as 'SimpleAttribute'
# class 'ShouldNotShowUp' has been stereotyped as 'SimpleAttribute' too
C.attr = attribute('attr', str)
C.name1 = association('name1', SubClass, opposite='name2')
SubClass.name2 = association('name2', C, opposite='name1')
C.base = association('base', SubClass, opposite='abstract')
D.subbase = association('subbase', SubClass, opposite='concrete')
SubClass.concrete = association('concrete', D, opposite='subbase')
D.name3 = association('name3', SubClass, opposite='name4')
# 'SubClass.value' is a simple attribute
SubClass.value = attribute('value', str)
SubClass.abstract = derivedunion(SubClass, 'abstract', C, 0, '*', SubClass.concrete)
SubClass.name4 = redefine(SubClass, 'name4', D, '*', SubClass.name2)
"""


class OverridesFile:
    def __init__(self, lines):
        self.lines_iter = iter(lines)

    def readline(self):
        try:
            return next(self.lines_iter) + "\n"
        except StopIteration:
            return None


def test_overrides():
    pf = OverridesFile(["override Transition", "placeholder"])
    overrides = Overrides()
    overrides.read_overrides(pf)

    assert overrides.has_override("Transition"), overrides.overrides
    assert overrides.derives("Transition") == (), overrides.overrides
    assert overrides.get_type("Transition") == "Any", overrides.overrides


def test_overrides_with_derived_items():
    pf = OverridesFile(["override Transition(Foo, Bar)", "placeholder"])
    overrides = Overrides()
    overrides.read_overrides(pf)

    assert overrides.has_override("Transition"), overrides.overrides
    assert overrides.derives("Transition") == ("Foo", "Bar"), overrides.overrides
    assert overrides.get_type("Transition") == "Any", overrides.overrides


def test_overrides_of_features_with_derived_items():
    pf = OverridesFile(["override Transition.foo(Bar.baz)", "placeholder"])
    overrides = Overrides()
    overrides.read_overrides(pf)

    assert overrides.has_override("Transition.foo"), overrides.overrides
    assert overrides.derives("Transition.foo") == ("Bar.baz",), overrides.overrides
    assert overrides.get_type("Transition") == "Any", overrides.overrides


def test_overrides_with_type():
    pf = OverridesFile(["override Transition: Foo[str, str]", "placeholder"])
    overrides = Overrides()
    overrides.read_overrides(pf)

    assert overrides.has_override("Transition"), overrides.overrides
    assert overrides.derives("Transition") == (), overrides.overrides
    assert overrides.get_type("Transition") == "Foo[str, str]", overrides.overrides


def test_overrides_with_type_with_quotes():
    pf = OverridesFile(['override Transition: Foo["Type"]', "placeholder"])
    overrides = Overrides()
    overrides.read_overrides(pf)

    assert overrides.has_override("Transition"), overrides.overrides
    assert overrides.derives("Transition") == (), overrides.overrides
    assert overrides.get_type("Transition") == 'Foo["Type"]', overrides.overrides


def test_overrides_with_derived_items_and_type():
    pf = OverridesFile(["override Transition(Foo, Bar): Baz[str, str]", "placeholder"])
    overrides = Overrides()
    overrides.read_overrides(pf)

    assert overrides.has_override("Transition"), overrides.overrides
    assert overrides.derives("Transition") == ("Foo", "Bar"), overrides.overrides
    assert overrides.get_type("Transition") == "Baz[str, str]", overrides.overrides