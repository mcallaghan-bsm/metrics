# -*- coding: utf-8 -*-
"""Compute McCabe's Cyclomatic Metric. (Averages)

    This routine computes McCabe's AVERAGE Cyclomatic metric for the whole file
    and breaks down per function/method definition.

"""
from __future__ import unicode_literals, print_function
from collections import OrderedDict

from .metricbase import MetricBase


# TODO: why can't I import `mccabe` and re-use it?
mccabe_keywords = [
    'assert',
    'break',
    'continue',
    'elif',
    'else',
    'for',
    'if',
    'while']


class McCabeAvgMetric(MetricBase):
    """Compute McCabe's Cyclomatic Metric for the whole source file."""

    def __init__(self, context):
        self.name = 'mccabe_avg'
        self.context = context
        self.reset()

    def reset(self):
        """Reset ourself."""
        self.current_function = 'dummy'
        self.total_functions = 0
        self._metrics = OrderedDict(mccabe_avg=0, mccabe_dummy=0)

    def process_token(self, tok):
        """Count the number of decision points in entire file and per function."""

        token_type = tok[0]
        token_value = tok[1]

        # TODO: uncertain how to denote "end of function" (the lex tokens do not have it, and we would have to track
        # all of the "Token.Puntuation" until closure of the one immediately following the initial definition.
        # This results in the following state of reality for **complexity per function/method**:
        # 1. Any complexity previous to method or function definitions will be ignored.
        # 2. Any complexity in between these (bad practice) would be falsely attributed to the most recently defined function.
        # 3. Any complexity at the end of a file (bad practice) would be falsely attributed to the last definition.
        # This _should_ be acceptable and good enough, though noting the known inaccuracy anyway for brevity.

        # TODO: (does a "Method" token exist?)
        #print('mcallaghan:DEBUG:', tok, current_function, self._metrics)
        # It is possible for `Name` token types to not have a 3rd entry, we're trying to find: 'Token.Name.Function'
        if (token_type[0] == 'Name' and len(token_type) > 1 and token_type[1] == 'Function'):
            print('mcallaghan:DEBUG: found a function ', token_value)
            # if we are transitioning to a new function/method, save the previous information of a previous one
            # (nothing required?? 'cause we're storing uniquely in a dictionary per function I think)

            # bump to next function as a key, and track total
            self.current_function = token_value
            self.total_functions += 1
            self._metrics.update({'mccabe_' + self.current_function: 0})

        if (token_type[0] == 'Keyword') and token_value in mccabe_keywords:
            # (we should never get in here unless we're in a detected function ?)
            print('mcallaghan:DEBUG: WE ARE IN COMPLEXITY +1', tok)
            current_function_mccabe = self._metrics.get('mccabe_' + self.current_function)
            self._metrics.update({'mccabe_' + self.current_function: current_function_mccabe+1})

    def display_header(self):
        """Display header for McCabe Cyclomatic Complexity """
        print('McCabeAvg', end=' ')

    def display_separator(self):
        """Display separator for McCabe Cyclomatic Complexity """
        print('---------', end=' ')

    def display_metrics(self, metrics):
        """Display McCabe Cyclomatic Complexity (AVG)"""
        print('%6d' % self.calc_mccabe_avg(metrics), end=' ')

    def get_metrics(self):
        return self._metrics

    def calc_mccabe_avg(self, metrics):
        """Get the current McCabe average complexity per function for the entire file"""
        # process token couldn't do this live, we can only calculate average complexity across all functions
        # AFTER we've finished processing ...
        mccabe_total_per_function = 0
        for metric, value in self._metrics.items():
            if metric != 'mccabe_avg' and metric != 'mccabe_dummy':
                mccabe_total_per_function += value

        return mccabe_total_per_function / self.total_functions

    metrics = property(get_metrics)
