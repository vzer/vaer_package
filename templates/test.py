#!/usr/bin/env python
#coding=utf-8
__author__ = 'vzer'

import time
import datetime

for k in xrange(30):
    now=datetime.datetime.now().strftime("%Y-%m-%d")
    print "当前时间是：%s"%now