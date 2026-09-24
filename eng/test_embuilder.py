# Copyright .NET Foundation and Contributors.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import contextlib
import fnmatch
import io
import os
import sys
import unittest
from unittest import mock

import embuilder
from tools import system_libs
from tools.settings import settings


class EmbuilderTests(unittest.TestCase):
  def setUp(self):
    old_settings = settings.dict().copy()
    self.addCleanup(settings.dict().update, old_settings)
    self.patch(embuilder, 'MINIMAL_TASKS', embuilder.MINIMAL_TASKS[:])
    self.patch(embuilder, 'MINIMAL_PIC_TASKS', embuilder.MINIMAL_PIC_TASKS[:])
    self.patch(embuilder, 'PORTS', embuilder.PORTS[:])
    self.patch(embuilder, 'USE_NINJA', False)
    self.patch(embuilder.cache, 'setup')
    self.patch(embuilder.shared, 'check_sanity')
    self.patch(embuilder.shared, 'PRINT_SUBPROCS', False)
    self.build = self.patch(system_libs.Library, 'build', autospec=True)
    self.erase = self.patch(system_libs.Library, 'erase', autospec=True)
    self.generate = self.patch(system_libs.Library, 'generate', autospec=True)
    self.deferred = self.patch(system_libs, 'build_deferred')
    self.sysroot = self.patch(system_libs, 'ensure_sysroot')
    self.erase_file = self.patch(embuilder.cache, 'erase_file')
    self.build_port = self.patch(embuilder, 'build_port')
    self.clear_port = self.patch(embuilder, 'clear_port')
    environment = mock.patch.dict(os.environ)
    environment.start()
    self.addCleanup(environment.stop)

  def patch(self, obj, name, *args, **kwargs):
    patcher = mock.patch.object(obj, name, *args, **kwargs)
    value = patcher.start()
    self.addCleanup(patcher.stop)
    return value

  def run_builder(self, *args):
    output = io.StringIO()
    with mock.patch.object(sys, 'argv', ['embuilder', *args]), contextlib.redirect_stdout(output):
      result = embuilder.main()
    return result, output.getvalue()

  def called_targets(self, method):
    return [call.args[0].get_base_name() for call in method.call_args_list]

  def test_dotnet_archive_filenames(self):
    filenames = {
      'pthread': 'libc-mt.a',
      'worker_api': 'libwasm_workers-mt.a',
      'sanitizer': 'libclang_rt.asan.a',
      'sanitizer_mt': 'libclang_rt.asan-mt.a',
      'asan_debug': 'libc-asan-debug.a',
      'asan_optz': 'libc_optz-asan.a',
      'startup': 'crt1.o',
      'name-ww': 'libretained.a',
      'worker': 'libc-ww.a',
      'worker_debug': 'libc-ww-debug.a',
      'asan': 'libc-asan.a',
      'asan_mt': 'libc-mt-asan.a',
      'printf_asan': 'libprintf_long_double-asan.a',
      'printf_asan_mt': 'libprintf_long_double-mt-asan.a',
    }
    libraries = {
      name: mock.Mock(get_filename=mock.Mock(return_value=filename))
      for name, filename in filenames.items()
    }
    embuilder.MINIMAL_TASKS = list(libraries)
    self.assertEqual(embuilder.get_dotnet_tasks(libraries), [
      'pthread', 'worker_api', 'sanitizer', 'sanitizer_mt', 'asan_debug',
      'asan_optz', 'startup', 'name-ww',
    ])

  def test_dotnet_native_inventory(self):
    libraries, _ = embuilder.get_system_tasks()
    tasks = embuilder.get_dotnet_tasks(libraries)
    excluded = {
      name for name, library in libraries.items()
      if fnmatch.fnmatchcase(library.get_filename(), 'lib*-ww.a')
      or fnmatch.fnmatchcase(library.get_filename(), 'lib*-ww-*.a')
      or library.get_filename() in {
        'libc-asan.a', 'libc-mt-asan.a',
        'libprintf_long_double-asan.a', 'libprintf_long_double-mt-asan.a',
      }
    }
    self.assertTrue(excluded)
    self.assertEqual(set(tasks) & libraries.keys(), libraries.keys() - excluded)
    self.assertEqual(len(tasks), len(set(tasks)))
    for name in ('libc-mt', 'libwasm_workers-mt', 'libclang_rt.asan',
                 'libclang_rt.asan-mt', 'libclang_rt.ubsan', 'libc-asan-debug',
                 'libc_optz-asan', 'libmimalloc', 'libmimalloc-mt'):
      self.assertIn(name, tasks)
    result, output = self.run_builder('build', 'DOTNET')
    self.assertEqual(result, 0)
    self.assertEqual(self.called_targets(self.build), [t for t in tasks if t in libraries])
    self.assertIn('Building targets: ' + ' '.join(tasks), output)

  def test_dotnet_non_system_minimal(self):
    libraries, _ = embuilder.get_system_tasks()
    expected = embuilder.get_dotnet_tasks(libraries)
    embuilder.MINIMAL_TASKS += ['zlib', 'sysroot', 'zlib']
    self.assertEqual(embuilder.get_dotnet_tasks(libraries), [*expected, 'zlib', 'sysroot'])
    result, _ = self.run_builder('build', 'DOTNET', 'DOTNET')
    self.assertEqual(result, 0)
    self.assertEqual(self.called_targets(self.build), [t for t in expected if t in libraries])
    self.build_port.assert_called_once_with('zlib')
    self.sysroot.assert_called_once_with()
    result, _ = self.run_builder('clear', 'DOTNET')
    self.assertEqual(result, 0)
    self.clear_port.assert_called_once_with('zlib')
    self.erase_file.assert_called_once_with('sysroot_install.stamp')

  def test_dotnet_build_and_clear(self):
    libraries, _ = embuilder.get_system_tasks()
    expected = [t for t in embuilder.get_dotnet_tasks(libraries) if t in libraries]
    for operation, flags, builds, clears in (
      ('build', [], True, False),
      ('clear', [], False, True),
      ('build', ['--force'], True, True),
    ):
      with self.subTest(operation=operation, flags=flags):
        self.build.reset_mock()
        self.erase.reset_mock()
        result, _ = self.run_builder(operation, 'DOTNET', *flags)
        self.assertEqual(result, 0)
        self.assertEqual(self.called_targets(self.build), expected if builds else [])
        self.assertEqual(self.called_targets(self.erase), expected if clears else [])
        self.generate.assert_not_called()
        self.deferred.assert_not_called()

  def test_dotnet_ninja(self):
    embuilder.USE_NINJA = True
    libraries, _ = embuilder.get_system_tasks()
    expected = [t for t in embuilder.get_dotnet_tasks(libraries) if t in libraries]
    for operation in ('build', 'rebuild', 'clear'):
      with self.subTest(operation=operation):
        self.generate.reset_mock()
        self.erase.reset_mock()
        self.deferred.reset_mock()
        result, _ = self.run_builder(operation, 'DOTNET')
        self.assertEqual(result, 0)
        self.assertEqual(self.called_targets(self.generate), expected if operation == 'build' else [])
        self.assertEqual(self.called_targets(self.erase), expected if operation == 'clear' else [])
        self.assertEqual(self.deferred.call_count, int(operation != 'clear'))
        self.assertEqual(os.environ['EMBUILDER_PORT_BUILD_DEFERRED'], '1')
        self.build.assert_not_called()

  def test_existing_presets(self):
    _, system_tasks = embuilder.get_system_tasks()
    for name, expected in (
      ('SYSTEM', system_tasks),
      ('MINIMAL', embuilder.MINIMAL_TASKS),
      ('MINIMAL_PIC', embuilder.MINIMAL_PIC_TASKS),
      ('USER', embuilder.PORTS),
      ('ALL', system_tasks + embuilder.PORTS),
    ):
      with self.subTest(preset=name):
        self.build.reset_mock()
        self.build_port.reset_mock()
        result, output = self.run_builder('build', name)
        targets = [t for t in expected if t != 'cocos2d']
        self.assertEqual(result, 0)
        self.assertIn('Building targets: ' + ' '.join(targets), output)
        self.assertEqual(self.called_targets(self.build), [t for t in targets if t in system_tasks])
        self.assertEqual(self.build_port.call_args_list,
                         [mock.call(t) for t in targets if t in embuilder.PORTS])

  def test_dotnet_build_options(self):
    for option in ('--pic', '--lto', '--lto=thin', '--wasm64'):
      with self.subTest(option=option):
        old_settings = settings.dict().copy()
        self.build.reset_mock()
        result, _ = self.run_builder('build', 'DOTNET', option)
        self.assertEqual(result, 0)
        libraries, _ = embuilder.get_system_tasks()
        self.assertEqual(self.called_targets(self.build),
                         [t for t in embuilder.get_dotnet_tasks(libraries) if t in libraries])
        if option == '--pic':
          self.assertEqual(settings.MAIN_MODULE, 1)
        elif option == '--wasm64':
          self.assertEqual(settings.MEMORY64, 1)
        else:
          self.assertEqual(settings.LTO, 'thin' if option == '--lto=thin' else 'full')
        settings.dict().update(old_settings)

  def test_explicit_and_wildcard_targets(self):
    result, _ = self.run_builder('build', 'libc-asan', 'libwasm_workers*')
    self.assertEqual(result, 0)
    self.assertEqual(self.called_targets(self.build),
                     ['libc-asan', *fnmatch.filter(embuilder.get_all_tasks(), 'libwasm_workers*')])

  def test_dotnet_with_explicit_target(self):
    libraries, _ = embuilder.get_system_tasks()
    expected = [t for t in embuilder.get_dotnet_tasks(libraries) if t in libraries]
    self.assertNotIn('libc-asan', expected)
    result, _ = self.run_builder('build', 'DOTNET', 'libc-asan')
    self.assertEqual(result, 0)
    self.assertEqual(self.called_targets(self.build), [*expected, 'libc-asan'])

  def test_help(self):
    output = io.StringIO()
    with mock.patch.object(sys, 'argv', ['embuilder', '--help']), \
         contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as error:
      embuilder.main()
    self.assertEqual(error.exception.code, 0)
    self.assertIn('DOTNET', output.getvalue())
    self.assertIn('SYSTEM', output.getvalue())
    self.assertIn('MINIMAL', output.getvalue())
    self.build.assert_not_called()

  def test_invalid_target(self):
    with self.assertLogs('embuilder', level='ERROR') as log:
      result, _ = self.run_builder('build', 'DOTNET_typo')
    self.assertEqual(result, 1)
    self.assertIn('unfamiliar build target: DOTNET_typo', log.output[0])
    self.build.assert_not_called()

  def test_invalid_non_system_minimal(self):
    embuilder.MINIMAL_TASKS += ['invalid_minimal_target']
    with self.assertLogs('embuilder', level='ERROR') as log:
      result, _ = self.run_builder('build', 'DOTNET')
    self.assertEqual(result, 1)
    self.assertIn('unfamiliar build target: invalid_minimal_target', log.output[0])

  def test_rebuild_requires_ninja(self):
    error = io.StringIO()
    with contextlib.redirect_stderr(error), self.assertRaises(SystemExit):
      self.run_builder('rebuild', 'DOTNET')
    self.assertIn('"rebuild" operation is only valid when using Ninja', error.getvalue())
    self.build.assert_not_called()


if __name__ == '__main__':
  unittest.main()
