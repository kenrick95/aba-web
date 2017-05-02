#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import time

class ABA_Perf_Logger():
    def __init__(self, identifier):
        self.__wall_time_start = 0
        self.__cpu_time_start = 0
        self.__wall_time_end = 0
        self.__cpu_time_end = 0
        self.wall_time = 0
        self.cpu_time = 0
        self.identifier = identifier

    def start(self):
        self.__wall_time_start = time.perf_counter()
        self.__cpu_time_start = time.process_time()

    def end(self):
        self.__wall_time_end = time.perf_counter()
        self.__cpu_time_end = time.process_time()

        self.wall_time = self.__wall_time_end - self.__wall_time_start
        self.cpu_time = self.__cpu_time_end - self.__cpu_time_start

        logging.info("[%s] wall_time: %s; cpu_time: %s", self.identifier, self.wall_time, self.cpu_time)
