# -*- coding: utf-8 -*-
"""novelWriter Test Config
"""

import pytest, shutil
from os import path, mkdir

@pytest.fixture(scope="session")
def nwTemp():
    testDir = path.dirname(__file__)
    tempDir = path.join(testDir,"temp")
    if path.isdir(tempDir):
        shutil.rmtree(tempDir)
    if not path.isdir(tempDir):
        mkdir(tempDir)
    return tempDir

@pytest.fixture(scope="session")
def nwTempProj(nwTemp):
    projDir = path.join(nwTemp,"proj")
    if not path.isdir(projDir):
        mkdir(projDir)
    return projDir

@pytest.fixture(scope="session")
def nwTempGUI(nwTemp):
    guiDir = path.join(nwTemp,"gui")
    if not path.isdir(guiDir):
        mkdir(guiDir)
    return guiDir

@pytest.fixture(scope="session")
def nwRef():
    testDir = path.dirname(__file__)
    refDir  = path.join(testDir,"reference")
    return refDir
