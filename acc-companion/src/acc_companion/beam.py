"""Contains the physics formulas for beam energy parameters."""

import math
from typing import get_type_hints


SPEED_OF_LIGHT = 299792458.0  # [m/s]


class Beam:
    """Beam particle and energy definition.

    The energy must be specified by one of `energy, momentum, gamma, beta, rigidity` and is considered in that order
    of precedence.

    Attributes
    ----------
    mass : float
        Rest mass in units of [GeV].
    charge : int
        Charge state in units of the elementary charge.
    energy : float, optional
        Total energy in units of [GeV]. The order of precedence for beam energy definition is the same as
        attributes are listed here.
    momentum : float, optional
        Particle momentum in units of [GeV/c].
    gamma : float, optional
        Relativistic gamma factor of the particles.
    beta : float, optional
        Relativistic beta factor of the particles.
    rigidity : float, optional
        Magnetic rigidity of the particles in units of [T*m].

    Raises
    ------
    ValueError
        If the energy specification is incomplete.
    """
    mass : float
    charge : int
    energy : float
    momentum : float
    gamma : float
    beta : float
    rigidity : float

    energy_definition_precedence = ('energy', 'momentum', 'gamma', 'beta', 'rigidity')
    units = dict(mass='GeV/c^2', charge='e', energy='GeV', momentum='GeV/c', gamma='1', beta='1', rigidity='T*m')

    def __init__(self,
        mass: float = None,
        charge: int = None,
        energy: float = None,
        momentum: float = None,
        gamma: float = None,
        beta: float = None,
        rigidity: float = None,
        **kwargs
    ):
        self.mass = mass
        self.charge = charge
        try:
            args = locals()
            setattr(self, *next((x, args[x]) for x in self.energy_definition_precedence if args[x] is not None))
        except StopIteration:
            raise ValueError(f'Beam energy must be specified via one of {self.energy_definition_precedence}') from None

    @property
    def momentum(self) -> float:
        return math.sqrt(self.energy**2 - self.mass**2)

    @momentum.setter
    def momentum(self, momentum: float) -> None:
        self.energy = math.sqrt(momentum**2 + self.mass**2)

    @property
    def gamma(self) -> float:
        return self.energy / self.mass

    @gamma.setter
    def gamma(self, gamma: float) -> None:
        if gamma < 1:
            raise ValueError('gamma must be >= 1')
        self.energy = gamma * self.mass

    @property
    def beta(self) -> float:
        return math.sqrt(1. - 1./self.gamma**2)

    @beta.setter
    def beta(self, beta: float) -> None:
        self.energy = self.mass / math.sqrt(1. - beta**2)

    @property
    def rigidity(self) -> float:
        return self.momentum / (abs(self.charge) * SPEED_OF_LIGHT * 1e-9)

    @rigidity.setter
    def rigidity(self, rigidity: float) -> None:
        self.momentum = rigidity * abs(self.charge) * SPEED_OF_LIGHT * 1e-9

    def to_dict(self) -> dict:
        return {attr: getattr(self, attr) for attr in get_type_hints(type(self))}
