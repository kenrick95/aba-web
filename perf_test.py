#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import listdir
from os.path import isfile, join, splitext
import logging
import time
from aba.aba_parser import ABA_Parser

logging.basicConfig(filename='PerfTest.log',level=logging.INFO)
logging.info("Start performance test")
global_wall_time_start = time.perf_counter()
global_cpu_time_start = time.process_time()

path = "perf_test_data"
test_files = [f for f in listdir(path) if isfile(join(path, f)) and splitext(f)[1] == ".txt"]

for file in test_files:
    with open(join(path, file), 'r') as f:
        source_code = f.read()
        logging.info("Start running %s", file)
        wall_time_start = time.perf_counter()
        cpu_time_start = time.process_time()

        parser = ABA_Parser(source_code)
        parse_errors = parser.parse()

        if len(parse_errors) > 0:
            logging.info("Parse error: %s", ', '.join(parse_errors))
        else:
            try:
                parser.construct_aba()
            except Exception as exp:
                logging.info("Runtime error: %s", str(exp))

        wall_time_end = time.perf_counter()
        cpu_time_end = time.process_time()
        wall_time = wall_time_end - wall_time_start
        cpu_time = cpu_time_end - cpu_time_start
        logging.info("End running %s", file)
        logging.info("   cpu_time is: \t %s seconds", cpu_time)
        logging.info("   wall_time is: \t %s seconds", wall_time)



global_wall_time_end = time.perf_counter()
global_cpu_time_end = time.process_time()
global_wall_time = global_wall_time_end - global_wall_time_start
global_cpu_time = global_cpu_time_end - global_cpu_time_start
logging.info("End performance test")
logging.info("   global_cpu_time is: \t %s seconds", global_cpu_time)
logging.info("   global_wall_time is: \t %s seconds", global_wall_time)