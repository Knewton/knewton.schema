#!/usr/bin/env python
import os.path
import re
from setuptools import Command, find_packages, setup

def parse_requirements(file_name):
	"""Taken from http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy"""
	requirements = []
	for line in open(os.path.join(os.path.dirname(__file__), "config", file_name), "r"):
		line = line.strip()
		# comments and blank lines
		if re.match(r"(^#)|(^$)", line):
			continue
		requirements.append(line)
	return requirements

setup(
	name="knewton.schema",
	version="0.9.0",
	url = "https://github.com/Knewton/k.schema",
	author="Devon Jones",
	author_email="devon@knewton.com",
	license = "Apache",
	scripts = [],
	packages=find_packages(),
	package_data = {"config": ["requirements.txt"]},
	install_requires=parse_requirements("requirements.txt"),
	description = "Schema migration libary for python.",
	long_description = "\n" + open("README.md").read(),
)

