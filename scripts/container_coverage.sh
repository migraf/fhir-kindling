#!/bin/bash

coverage run -m pytest /opt/tests
coverage xml -o /opt/coverage/coverage.xml