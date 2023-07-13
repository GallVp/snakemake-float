#!/usr/bin/env python3

import sys
import subprocess

import math

from snakemake.utils import read_job_properties

from float_config import FloatConfig


class FloatSubmit:
    def __init__(self):
        self._config = FloatConfig()

    def submit_job(self, job_file):
        cfg = self._config
        cmd = 'float submit'

        config_parameters = cfg.parameters()
        for key, value in config_parameters.items():
            if key != cfg.SUBMIT_EXTRA:
                cmd += f" --{key} {value}"

        job_properties = read_job_properties(jobscript)
        if 'cpu' not in config_parameters:
            cpu = job_properties.get('threads', 2)
            cmd += f" --cpu {cpu}"

        if 'mem' not in config_parameters:
            mem_MiB = job_properties.get('resources', {}).get('mem_mib', 4096)
            mem_GiB = math.ceil(mem_MiB / 1024)
            cmd += f" --mem {mem_GiB}"

        cmd += f" --job {job_file}"
        cmd += f" {config_parameters.get(cfg.SUBMIT_EXTRA, '')}"

        output = subprocess.check_output(cmd, shell=True).decode()
        jobid = output[len('id: '): output.index('\n')]
        return jobid

    def mount_point(self):
        cfg = self._config
        config_parameters = cfg.parameters()

        dv = config_parameters['dataVolume']
        start = dv.index('//')
        colon = dv.index(':', start)

        if colon == -1:
            raise ValueError('Please specify dataVolume mount point')

        return dv[colon + 1:]


if __name__ == '__main__':
    jobscript = sys.argv[1]

    float_submit = FloatSubmit()

    with open(jobscript, 'r') as js:
        script_lines = js.readlines()

    script_lines.insert(3, f"cd {float_submit.mount_point()}\n")

    # Hack to allow --use-conda
    exec_job_cmd = script_lines[-1]
    if '--use-conda' in exec_job_cmd:
        conda_prefix = '/memverge/.snakemake'
        script_lines[3: 3] = [
            f"mkdir -p {conda_prefix}/conda\n",
            f"mkdir -p {conda_prefix}/conda-archive\n"
        ]

        part = list(exec_job_cmd.partition(' --use-conda'))
        part[1] += f" --conda-prefix '{conda_prefix}'"
        script_lines[-1] = ''.join(part)

    with open(jobscript, 'w') as js:
        js.writelines(script_lines)

    jobid = float_submit.submit_job(jobscript)
    print(jobid)
