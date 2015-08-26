#!/usr/bin/env python
from fabric.api import env, run

env.hosts = [ '10.0.72.82' ]

def uptime():
  run('uptime')
