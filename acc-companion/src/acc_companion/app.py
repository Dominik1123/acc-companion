"""
Useful tools for accelerator physics
"""

import importlib.resources
import json
import re

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from .beam import Beam
from .utils import Guard


with importlib.resources.path('acc_companion.resources', 'atomic_weights.json') as path:
    with open(path) as fh:
        ATOMIC_WEIGHTS_IN_GEV = {s: w/1e3 for s, w in json.load(fh).items()}


class ACCCompanion(toga.App):
    PARTICLE_SPECIES_PATTERN = re.compile(r'(\d+)([a-z]{2})(\d+)(?:\+)?', flags=re.I)
    FLOAT_PATTERN = re.compile(r'\d+(\.\d+)?')
    FLOAT_FORMAT = '{:.6f}'.format
    PER_NUCLEON = ('energy', 'pc')
    LABEL_PADDING = (10, 20)
    LABEL_STYLE = Pack(width=100, padding=LABEL_PADDING, alignment='right')
    INPUT_STYLE = Pack(width=120, padding=0)
    PARTICLE_SPECIES_FEEDBACK_VALID = '\N{Large Green Circle}'
    PARTICLE_SPECIES_FEEDBACK_INVALID = '\N{Large Red Circle}'

    def startup(self):
        self.number_of_nucleons = 1
        self.beam = Beam(mass=1, charge=1, energy=1)  # use some placeholder values

        self.particle_species_input = toga.TextInput(
            on_change=self.particle_species_changed,
            validators=[self.particle_species_validator],
            placeholder='e.g. 40Ar10+',
            style=self.INPUT_STYLE,
        )
        self.particle_species_status = toga.Label('', style=Pack(padding=self.LABEL_PADDING))
        particle_species_box = toga.Box(
            children=[
                toga.Label('Particle species:', style=self.LABEL_STYLE),
                self.particle_species_input,
                self.particle_species_status,
            ],
            style=Pack(direction=ROW),
        )

        self.energy_inputs = {
            label: toga.TextInput(
                on_change=self.energy_changed,
                validators=[self.float_validator],
                style=self.INPUT_STYLE,
                id=label,
            )
            for label in Beam.energy_definition_precedence
        }
        energy_box = toga.Box(
            children=[
                toga.Box(
                    children=[
                        toga.Label(f'{label.capitalize()}:', style=self.LABEL_STYLE),
                        input_field,
                        toga.Label(f'[{Beam.units[label]}]', style=Pack(padding=self.LABEL_PADDING)),
                    ],
                    style=Pack(direction=ROW),
                )
                for label, input_field in self.energy_inputs.items()
            ],
            style=Pack(direction=COLUMN),
        )

        main_box = toga.Box(
            children=[
                particle_species_box,
                energy_box,
            ],
            style=Pack(direction=COLUMN)
        )

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def particle_species_changed(self, field):
        if field.validate():
            number_of_nucleons, symbol, charge_state = \
                self.PARTICLE_SPECIES_PATTERN.fullmatch(field.value).groups()

            self.beam.mass = int(number_of_nucleons) * ATOMIC_WEIGHTS_IN_GEV[symbol]
            self.beam.charge = int(charge_state)
            self.number_of_nucleons = int(number_of_nucleons)
            self.particle_species_status.text = self.PARTICLE_SPECIES_FEEDBACK_VALID
            self.particle_species_status.refresh()  # required on Android
            # Use the following to trigger an udate of the energy fields; the value must actually change.
            if (current_value := self.energy_inputs['energy'].value):
                self.energy_inputs['energy'].value = f'{current_value}0'
                self.energy_inputs['energy'].value = current_value
        else:
            self.particle_species_status.text = self.PARTICLE_SPECIES_FEEDBACK_INVALID
            self.particle_species_status.refresh()  # required on Android

    @Guard.block_recursion
    def energy_changed(self, field):
        if field.validate():
            factor = self.number_of_nucleons if field.id in self.PER_NUCLEON else 1
            value = float(field.value)*factor
            if field.id == 'energy':
                value += self.beam.mass
            try:
                setattr(self.beam, field.id, value)
            except ValueError:
                pass
            else:
                properties = self.beam.to_dict()
                properties['energy'] -= self.beam.mass
                for label in self.PER_NUCLEON:
                    properties[label] /= self.number_of_nucleons

                for input_field in self.energy_inputs.values():
                    if input_field is not field:
                        input_field.value = self.FLOAT_FORMAT(properties[input_field.id])

    @classmethod
    def particle_species_validator(cls, value):
        match = cls.PARTICLE_SPECIES_PATTERN.fullmatch(value)
        if match is None:
            return 'use the format <nucleons><symbol><charge>'
        if match.group(2) not in ATOMIC_WEIGHTS_IN_GEV:
            return 'unknown symbol'
        return None

    @classmethod
    def float_validator(cls, value):
        match = cls.FLOAT_PATTERN.fullmatch(value)
        if match is None:
            return 'must be a positive float number'
        return None


def main():
    return ACCCompanion()
