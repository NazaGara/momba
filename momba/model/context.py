# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020, Maximilian Köhl <mkoehl@cs.uni-saarland.de>

from __future__ import annotations

import typing as t

import dataclasses
import enum

from . import errors, expressions, types
from .action import Action
from .automata import Automaton
from .network import Network
from .properties import Property

from .. import kit

if t.TYPE_CHECKING:
    # XXX: stupid stuff to make mypy and the linter happy
    from . import effects  # noqa: F401


class ModelType(enum.Enum):
    LTS = "lts", "Labeled Transition System"
    DTMC = "dtmc", "Discrete-Time Markov Chain"
    CTMC = "ctmc", "Continuous-Time Markov Chain"
    MDP = "mdp", "Markov Decision Process"
    CTMDP = "ctmdp", "Continuous-Time Markov Decision Process"
    MA = "ma", "Markov Automaton"
    TA = "ta", "Timed Automaton"
    PTA = "pta", "Probabilistic Timed Automaton"
    STA = "sta", "Stochastic Timed Automaton"
    HA = "ha", "Hybrid Automaton"
    PHA = "pha", "Probabilistic Timed Automaton"
    SHA = "sha", "Stochastic Hybrid Automaton"

    abbreviation: str
    full_name: str

    def __init__(self, abbreviation: str, full_name: str):
        self.abbreviation = abbreviation
        self.full_name = full_name


TA_MODEL_TYPES = {
    ModelType.TA,
    ModelType.PTA,
    ModelType.STA,
    ModelType.HA,
    ModelType.PHA,
    ModelType.SHA,
}


Identifier = str

Typed = t.Union["expressions.Expression", "effects.Target"]


@dataclasses.dataclass(frozen=True)
class Declaration:
    identifier: Identifier
    typ: types.Type

    def validate(self, scope: Scope) -> None:
        # TODO: check whether type is bounded or basic
        pass

    def is_constant_in(self, scope: Scope) -> bool:
        return False


@dataclasses.dataclass(frozen=True)
class VariableDeclaration(Declaration):
    is_transient: t.Optional[bool] = None
    initial_value: t.Optional[expressions.Expression] = None

    def validate(self, scope: Scope) -> None:
        if self.initial_value is not None:
            if not self.typ.is_assignable_from(scope.get_type(self.initial_value)):
                raise errors.InvalidTypeError(
                    f"type of initial value is not assignable to variable type"
                )
            if not self.initial_value.is_constant_in(scope):
                raise errors.NotAConstantError(f"initial value must be a constant")


@dataclasses.dataclass(frozen=True)
class ConstantDeclaration(Declaration):
    """ Constants without values are parameters. """

    value: t.Optional[expressions.Expression] = None

    def validate(self, scope: Scope) -> None:
        if self.value is not None:
            if not self.value.is_constant_in(scope):
                raise errors.NotAConstantError(
                    f"value {self.value} of constant declaration is not a constant"
                )
            if not self.typ.is_assignable_from(scope.get_type(self.value)):
                raise errors.InvalidTypeError(
                    f"constant expression is not assignable to constant type"
                )

    def is_constant_in(self, scope: Scope) -> bool:
        return True


class PropertyDefinition:
    _name: t.Optional[str]
    _prop: Property

    def __init__(self, prop: Property, *, name: t.Optional[str] = None) -> None:
        self._name = name
        self._prop = prop

    @property
    def name(self) -> t.Optional[str]:
        return self._name

    @property
    def prop(self) -> Property:
        return self._prop


class Scope:
    ctx: Context
    parent: t.Optional[Scope]

    _declarations: t.Dict[Identifier, Declaration]
    _types: t.Dict[Typed, types.Type]

    def __init__(self, ctx: Context, parent: t.Optional[Scope] = None):
        self.ctx = ctx
        self.parent = parent
        self._declarations = {}
        self._types = {}

    @property
    def declarations(self) -> t.AbstractSet[Declaration]:
        return frozenset(self._declarations.values())

    @property
    def variable_declarations(self) -> t.AbstractSet[VariableDeclaration]:
        return frozenset(
            decl
            for decl in self._declarations.values()
            if isinstance(decl, VariableDeclaration)
        )

    @property
    def constant_declarations(self) -> t.AbstractSet[ConstantDeclaration]:
        return frozenset(
            decl
            for decl in self._declarations.values()
            if isinstance(decl, ConstantDeclaration)
        )

    @property
    def clock_declarations(self) -> t.AbstractSet[VariableDeclaration]:
        """
        Returns the set of declarations for clock variables.
        """
        return frozenset(
            decl
            for decl in self._declarations.values()
            if isinstance(decl, VariableDeclaration) and decl.typ == types.CLOCK
        )

    def new_child_scope(self) -> Scope:
        return Scope(self.ctx, parent=self)

    def get_type(self, typed: Typed) -> types.Type:
        if typed not in self._types:
            inferred_type = typed.infer_type(self)
            inferred_type.validate_in(self)
            self._types[typed] = inferred_type
        return self._types[typed]

    def is_constant(self, expression: expressions.Expression) -> bool:
        return expression.is_constant_in(self)

    def lookup(self, identifier: Identifier) -> Declaration:
        try:
            return self._declarations[identifier]
        except KeyError:
            if self.parent is None:
                raise errors.UnboundIdentifierError(
                    f"identifier {identifier} is unbound in scope {self}"
                )
            return self.parent.lookup(identifier)

    def declare(self, declaration: Declaration) -> None:
        if declaration.identifier in self._declarations:
            raise errors.InvalidDeclarationError(
                f"identifier `{declaration.identifier} has already been declared"
            )
        declaration.validate(self)
        self._declarations[declaration.identifier] = declaration

    def declare_variable(
        self,
        identifier: Identifier,
        typ: types.Type,
        *,
        is_transient: t.Optional[bool] = None,
        initial_value: t.Optional[expressions.Expression] = None,
    ) -> None:
        self.declare(
            VariableDeclaration(
                identifier, typ, is_transient=is_transient, initial_value=initial_value
            )
        )

    def declare_constant(
        self,
        identifier: Identifier,
        typ: types.Type,
        value: t.Optional[expressions.MaybeExpression] = None,
    ) -> None:
        if value is None:
            self.declare(ConstantDeclaration(identifier, typ, value))
        else:
            self.declare(
                ConstantDeclaration(identifier, typ, expressions.convert(value))
            )

    def get_dbm(self, expression: expressions.Expression) -> kit.DBM:
        """
        Returns a DBM for the given expression.

        The expression musst be a conjunction of clock constraints.
        """
        raise NotImplementedError()


class Context:
    model_type: ModelType
    global_scope: Scope

    _actions: t.Set[Action]
    _automata: t.Set[Automaton]
    _networks: t.Set[Network]
    _properties: t.Set[PropertyDefinition]

    def __init__(self, model_type: ModelType = ModelType.SHA) -> None:
        self.model_type = model_type
        self.global_scope = Scope(self)
        self._automata = set()
        self._networks = set()
        self._properties = set()

    @property
    def automata(self) -> t.AbstractSet[Automaton]:
        return self._automata

    @property
    def networks(self) -> t.AbstractSet[Network]:
        return self._networks

    @property
    def properties(self) -> t.AbstractSet[PropertyDefinition]:
        return self._properties

    def new_scope(self) -> Scope:
        return self.global_scope.new_child_scope()

    def get_automaton_by_name(self, name: str) -> Automaton:
        for automaton in self._automata:
            if automaton.name == name:
                return automaton
        raise Exception(f"there is no automaton with name {name}")

    def create_action(self, name: str) -> Action:
        action = Action(self, name)
        self._actions.add(action)
        return action

    def create_automaton(self, *, name: t.Optional[str] = None) -> Automaton:
        automaton = Automaton(self, name=name)
        self._automata.add(automaton)
        return automaton

    def create_network(self, *, name: t.Optional[str] = None) -> Network:
        network = Network(self, name=name)
        self._networks.add(network)
        return network

    def define_property(
        self, prop: Property, *, name: t.Optional[str] = None
    ) -> PropertyDefinition:
        property_definition = PropertyDefinition(name=name, prop=prop)
        self._properties.add(property_definition)
        return property_definition
