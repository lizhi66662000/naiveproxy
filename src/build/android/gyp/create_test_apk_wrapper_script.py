#!/usr/bin/env python3
# Copyright 2022 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Create a wrapper script to run a test apk using apk_operations.py."""

import argparse
import os
import string
import sys

from util import build_utils

SCRIPT_TEMPLATE = string.Template("""\
#!/usr/bin/env python3
#
# This file was generated by build/android/gyp/create_test_apk_wrapper_script.py

import os
import sys

def main():
  script_directory = os.path.dirname(__file__)
  resolve = lambda p: p if p is None else os.path.abspath(os.path.join(
      script_directory, p))
  sys.path.append(resolve(${WRAPPED_SCRIPT_DIR}))
  import apk_operations

  additional_apk_paths = [resolve(p) for p in ${ADDITIONAL_APKS}]
  apk_operations.RunForTestApk(
      output_directory=resolve(${OUTPUT_DIR}),
      package_name=${PACKAGE_NAME},
      test_apk_path=resolve(${TEST_APK}),
      test_apk_json=resolve(${TEST_APK_JSON}),
      proguard_mapping_path=resolve(${MAPPING_PATH}),
      additional_apk_paths=additional_apk_paths)

if __name__ == '__main__':
  sys.exit(main())
""")


def main(args):
  args = build_utils.ExpandFileArgs(args)
  parser = argparse.ArgumentParser()
  parser.add_argument('--script-output-path',
                      required=True,
                      help='Output path for executable script.')
  parser.add_argument('--package-name', required=True)
  parser.add_argument('--test-apk')
  parser.add_argument('--test-apk-incremental-install-json')
  parser.add_argument('--proguard-mapping-path')
  parser.add_argument('--additional-apk',
                      action='append',
                      dest='additional_apks',
                      default=[],
                      help='Paths to APKs to be installed prior to --apk-path.')
  args = parser.parse_args(args)

  def relativize(path):
    """Returns the path relative to the output script directory."""
    if path is None:
      return path
    return os.path.relpath(path, os.path.dirname(args.script_output_path))

  wrapped_script_dir = os.path.join(os.path.dirname(__file__), os.path.pardir)
  wrapped_script_dir = relativize(wrapped_script_dir)
  with open(args.script_output_path, 'w') as script:
    script_dict = {
        'WRAPPED_SCRIPT_DIR': repr(wrapped_script_dir),
        'OUTPUT_DIR': repr(relativize('.')),
        'PACKAGE_NAME': repr(args.package_name),
        'TEST_APK': repr(relativize(args.test_apk)),
        'TEST_APK_JSON':
        repr(relativize(args.test_apk_incremental_install_json)),
        'MAPPING_PATH': repr(relativize(args.proguard_mapping_path)),
        'ADDITIONAL_APKS': [relativize(p) for p in args.additional_apks],
    }
    script.write(SCRIPT_TEMPLATE.substitute(script_dict))
  os.chmod(args.script_output_path, 0o750)
  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))