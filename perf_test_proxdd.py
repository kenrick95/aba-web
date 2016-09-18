#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
from aba.aba_perf_logger import ABA_Perf_Logger
import psutil

logging.basicConfig(filename=os.path.join('logs','ProxddPerfTest.log'),level=logging.DEBUG,format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

path_to_sictus = "C:\\Program Files (x86)\\SICStus Prolog VC14 4.3.3\\bin\\sicstus-4.3.3"
path_to_proxdd = "D:/Cloud/SCE/FYP-proxdd/proxdd/code/proxdd.pl"
path_to_exp_file = "D:\\Cloud\\SCE\\FYP-randomaf\\frameworks"
timeout = 120 # seconds

# http://stackoverflow.com/a/25134985/917957
def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for sub_proc in process.children(recursive=True):
        sub_proc.kill()
    process.kill()

runonly = []
with open("perf_test_proxdd_setup.txt", "r") as f:
    runonly = f.readlines()
runonly = [x.strip() for x in runonly]

logging.info("Start proxdd performance test")
global_perf_logger = ABA_Perf_Logger("Overall proxdd performance test")
global_perf_logger.start()

for x in runonly:
    y = x.split(',')
    test_symbol = y[0]
    file = y[1]

    perf_logger = ABA_Perf_Logger("%s, testing symbol %s" % (file, test_symbol))
    perf_logger.start()

    stdout_data, stderr_data = None, None
    proc = Popen(path_to_sictus, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=path_to_exp_file)
    cmd = "compile('%s').\nloadf(%s).\nsxdd(%s, X)." % (path_to_proxdd, file, test_symbol)
    try:
        stdout_data, stderr_data = proc.communicate(input=bytes(cmd, 'UTF-8'), timeout=timeout)
    except TimeoutExpired:
        kill(proc.pid)
        logging.error("Timeout error")

    if stdout_data:
        logging.debug(stdout_data.decode('UTF-8'))
    if stderr_data:
        logging.error(stderr_data.decode('UTF-8'))

    perf_logger.end()

global_perf_logger.end()