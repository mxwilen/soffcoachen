#!/bin/bash -v 
coverage run -m unittest discover -s tests
coverage html