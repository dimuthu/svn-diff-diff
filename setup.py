from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', base=base)
]

setup(name='SVN Diff Diff',
      version = '1.0.1',
      description = 'A small tool to export file structure of a SVN diff of two revisions.',
      options = dict(build_exe = buildOptions),
      executables = executables)
