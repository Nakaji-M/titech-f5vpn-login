from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import re
from bs4 import BeautifulSoup, Tag

@dataclass
class HTMLInput:
    name: str
    type: str
    value: str

@dataclass
class HTMLSelect:
    name: str
    values: List[str]
    selected_value: Optional[str] = None
    
    def select(self, value: str):
        if value in self.values:
            self.selected_value = value

class TitechPortalMatrix(Enum):
    A1 = "a1"
    A2 = "a2"
    A3 = "a3"
    A4 = "a4"
    A5 = "a5"
    A6 = "a6"
    A7 = "a7"
    B1 = "b1"
    B2 = "b2"
    B3 = "b3"
    B4 = "b4"
    B5 = "b5"
    B6 = "b6"
    B7 = "b7"
    C1 = "c1"
    C2 = "c2"
    C3 = "c3"
    C4 = "c4"
    C5 = "c5"
    C6 = "c6"
    C7 = "c7"
    D1 = "d1"
    D2 = "d2"
    D3 = "d3"
    D4 = "d4"
    D5 = "d5"
    D6 = "d6"
    D7 = "d7"
    E1 = "e1"
    E2 = "e2"
    E3 = "e3"
    E4 = "e4"
    E5 = "e5"
    E6 = "e6"
    E7 = "e7"
    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    F6 = "f6"
    F7 = "f7"
    G1 = "g1"
    G2 = "g2"
    G3 = "g3"
    G4 = "g4"
    G5 = "g5"
    G6 = "g6"
    G7 = "g7"
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"
    H7 = "h7"
    I1 = "i1"
    I2 = "i2"
    I3 = "i3"
    I4 = "i4"
    I5 = "i5"
    I6 = "i6"
    I7 = "i7"
    J1 = "j1"
    J2 = "j2"
    J3 = "j3"
    J4 = "j4"
    J5 = "j5"
    J6 = "j6"
    J7 = "j7"

def parse_html_input(html: str) -> List[HTMLInput]:
    soup = BeautifulSoup(html, 'html.parser')
    inputs = []
    for tag in soup.find_all('input'):
        inputs.append(HTMLInput(
            name=tag.get('name', ''),
            type=tag.get('type', 'text'),
            value=tag.get('value', '')
        ))
    return inputs

def parse_html_select(html: str) -> List[HTMLSelect]:
    soup = BeautifulSoup(html, 'html.parser')
    selects = []
    for tag in soup.find_all('select'):
        name = tag.get('name', '')
        options = [opt.get('value', '') for opt in tag.find_all('option')]
        selects.append(HTMLSelect(
            name=name,
            values=options,
            selected_value=None
        ))
    return selects

def parse_current_matrices(html: str) -> List[TitechPortalMatrix]:
    matches = re.findall(r"\[([A-J]{1}),([1-7]{1})\]", html)
    
    result = []
    for col, row in matches:
        key = f"{col.lower()}{row}"
        try:
            result.append(TitechPortalMatrix(key))
        except ValueError:
            continue
    return result
