#!/usr/bin/env python
# This file is part of SMOC
# Copyright (C) 2018  Miguel Fernandes
#
# SMOC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMOC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""SMOC server entry point"""

from __future__ import print_function

import argparse
import json
import os
import sys
from subprocess import call


def main():
    """SMOC server main function."""
    description = 'SMOC - A Stochastic Multi-objective Optimizer for Cadence Virtuoso'
    parser = argparse.ArgumentParser(description=description, prog='smoc')

    parser.add_argument(
        'config_file', metavar='FILE', help='file with the SMOC server parameters')

    config_file = parser.parse_args().config_file

    # Check if config_file exists
    if not os.path.isfile(config_file):
        print("[ERROR] Invalid CONFIG file. Exiting the program...")
        return 1

    # Load config file
    with open(config_file) as f:
        config = json.load(f)

    project_cfg = config['project_cfg']
    client_cfg = config['client_cfg']

    # Directories
    project_dir = project_cfg['project_path'] + '/' + project_cfg['project_name']
    script_dir = project_dir + '/' + project_cfg['script_path']

    # Check if directories exist
    directories = [project_dir, script_dir]
    for directory in directories:
        if not os.path.exists(directory):
            print("[ERROR] The directory {0} does not exist! Exiting SMOC...".format(directory))
            return 2

    # Files
    load_simulator_file = script_dir + '/' + project_cfg['loadSimulator_file']
    set_simulations_file = script_dir + '/' + project_cfg['setSimulations_file']
    template_simulations_file = script_dir + '/' + project_cfg['templateSimulations_file']
    run_simulation_file = script_dir + '/' + project_cfg['runSimulation_fie']
    variables_file = script_dir + '/' + project_cfg['variables_file']
    results_file = project_dir + '/' + project_cfg['results_file']

    # Check if files exist
    files = [load_simulator_file, template_simulations_file, run_simulation_file,
             variables_file]
    for file in files:
        if not os.path.isfile(file):
            print("[ERROR] The file {0} does not exist! Exiting SMOC...".format(file))
            return 3

    # Create results file
    open(results_file, 'a').close()

    # Create required environment variables
    # Project
    os.environ['SMOC_ROOT_DIR'] = project_dir
    os.environ['SMOC_LOAD_FILE'] = load_simulator_file
    os.environ['SMOC_SET_SIM_FILE'] = set_simulations_file
    os.environ['SMOC_TEMPLATE_FILE'] = template_simulations_file
    os.environ['SMOC_RUN_FILE'] = run_simulation_file
    os.environ['SMOC_VARS_FILE'] = variables_file
    os.environ['SMOC_RESULTS_FILE'] = results_file
    # Server
    os.environ['SMOC_CLIENT_ADDR'] = client_cfg['host']
    os.environ['SMOC_CLIENT_PORT'] = str(client_cfg['port'])

    # Print license
    print("\nSMOC  Copyright (C) 2018  Miguel Fernandes")
    print("This program comes with ABSOLUTELY NO WARRANTY.")
    print("This is free software, and you are welcome to redistribute it under the terms")
    print("of the GNU General Public License as published by the Free Software Foundation,")
    print("either version 3 of the License, or (at your option) any later version.")
    print("For more information, see <http://www.gnu.org/licenses/>\n")

    # Print logs
    print("********************************************************************************")
    print("****** SMOC - A Stochastic Multi-objective Optimizer for Cadence Virtuoso ******")
    print("***************************************************************************")
    print("* Project name:", project_cfg['project_name'])
    print("* Project path:", project_dir)
    print("* Script path:", script_dir)
    print("* Load simulator file (script folder):", project_cfg['loadSimulator_file'])
    print("* Set simulations file (script folder):", project_cfg['setSimulations_file'])
    print("* Simulations template file (script folder):", project_cfg['templateSimulations_file'])
    print("* Run simulation file (script folder):", project_cfg['runSimulation_fie'])
    print("* Variables file (script folder):", project_cfg['variables_file'])
    print("* Results file (project folder):", project_cfg['results_file'])
    print("****************************** Client Parameters *******************************")
    print("* Host:", client_cfg['host'])
    print("* Port:", client_cfg['port'])
    print("***************************************************************************\n")

    # Run Cadence
    call(['virtuoso', '-nograph', '-restore', 'cadence.il'])

    return 0


if __name__ == "__main__":
    sys.exit(main())
