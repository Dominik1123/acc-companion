"""Contains the physics formulas for beam energy parameters."""

import math
from typing import get_type_hints


SPEED_OF_LIGHT = 299792458.0  # [m/s]


class Beam:
    """Beam particle and energy definition.

    The energy must be specified by one of `energy, pc, gamma, beta, brho` and is considered in that order
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
    pc : float, optional
        Particle momentum times the speed of light in units of [GeV].
    gamma : float, optional
        Relativistic gamma factor of the particles.
    beta : float, optional
        Relativistic beta factor of the particles.
    brho : float, optional
        Magnetic rigidity of the particles in units of [T*m].

    Raises
    ------
    ValueError
        If the energy specification is incomplete.
    """
    mass : float
    charge : int
    energy : float
    pc : float
    gamma : float
    beta : float
    brho : float

    energy_definition_precedence = ('energy', 'pc', 'gamma', 'beta', 'brho')
    units = dict(mass='GeV/c^2', charge='e', energy='GeV', pc='GeV/c', gamma='1', beta='1', brho='T*m')

    def __init__(self,
        mass: float = None,
        charge: int = None,
        energy: float = None,
        pc: float = None,
        gamma: float = None,
        beta: float = None,
        brho: float = None,
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
    def pc(self) -> float:
        return math.sqrt(self.energy**2 - self.mass**2)

    @pc.setter
    def pc(self, pc: float) -> None:
        self.energy = math.sqrt(pc**2 + self.mass**2)

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
    def brho(self) -> float:
        return self.pc / (abs(self.charge) * SPEED_OF_LIGHT * 1e-9)

    @brho.setter
    def brho(self, brho: float) -> None:
        self.pc = brho * abs(self.charge) * SPEED_OF_LIGHT * 1e-9

    def to_dict(self) -> dict:
        return {attr: getattr(self, attr) for attr in get_type_hints(type(self))}
