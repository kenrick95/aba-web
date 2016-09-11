#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
from subprocess import Popen, PIPE, STDOUT
from aba.aba_perf_logger import ABA_Perf_Logger

logging.basicConfig(filename=os.path.join('logs','ProxddPerfTest.log'),level=logging.DEBUG,format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

path_to_sictus = "C:\\Program Files (x86)\\SICStus Prolog VC14 4.3.3\\bin\\sicstus-4.3.3"
path_to_proxdd = "D:/Cloud/SCE/FYP-proxdd/proxdd/code/proxdd.pl"
path_to_exp_file = "D:\\Cloud\\SCE\\FYP-randomaf\\frameworks"

runonly = []
with open("perf_test_runonly.txt", "r") as f:
    runonly = f.readlines()
runonly = [x.strip() for x in runonly]

logging.info("Start proxdd performance test")
global_perf_logger = ABA_Perf_Logger("Overall proxdd performance test")
global_perf_logger.start()

for file in runonly:
    perf_logger = ABA_Perf_Logger("%s" % file)
    perf_logger.start()

    p = Popen(path_to_sictus, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=path_to_exp_file)
    cmd = "compile('" + path_to_proxdd + "').\nloadf(" + file + ").\nsxdd(s1, X)."
    res = p.communicate(bytes(cmd, 'UTF-8'))

    for line in res:
        if line:
            logging.debug(line.decode('UTF-8'))

    perf_logger.end()

global_perf_logger.end()