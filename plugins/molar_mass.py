"""Example plugin: molar mass from a chemical formula. Copy this file to add your own."""
import re

MASS = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "Na": 22.990, "Mg": 24.305, "Al": 26.982,
        "P": 30.974, "S": 32.06, "Cl": 35.45, "K": 39.098, "Ca": 40.078, "Fe": 55.845, "Cu": 63.546, "Zn": 65.38}


def molar_mass(formula: str) -> float:
    stack = [{}]
    for el, num, op, cl, mult in re.findall(r"([A-Z][a-z]?)(\d*)|(\()|(\))(\d*)", formula):
        if op:
            stack.append({})
        elif cl:
            top = stack.pop()
            for k, v in top.items():
                stack[-1][k] = stack[-1].get(k, 0) + v * int(mult or 1)
        else:
            stack[-1][el] = stack[-1].get(el, 0) + int(num or 1)
    return sum(MASS[e] * n for e, n in stack[0].items())


def register(tool):
    @tool("molar_mass", "Compute molar mass in g/mol from a formula like Ca(OH)2.", {"formula": "Chemical formula"})
    def _run(formula):
        try:
            return f"{formula}: {molar_mass(formula):.3f} g/mol"
        except KeyError as e:
            return f"Unknown element {e}."
