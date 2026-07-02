//===----------------------------------------------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

<<<<<<<< HEAD:system/lib/libcxx/src/new_helpers.cpp
#include <cstdlib>
#include <new>

namespace std { // purposefully not versioned

#ifndef __GLIBCXX__
const nothrow_t nothrow{};
#endif

#ifndef LIBSTDCXX

void __throw_bad_alloc() {
#  ifndef _LIBCPP_HAS_NO_EXCEPTIONS
  throw bad_alloc();
#  else
  std::abort();
#  endif
}

#endif // !LIBSTDCXX
========
export namespace std {

  // [any.bad.any.cast], class bad_any_cast
  using std::bad_any_cast;

  // [any.class], class any
  using std::any;

  // [any.nonmembers], non-member functions
  using std::any_cast;
  using std::make_any;
  using std::swap;
>>>>>>>> 6.0.2:system/lib/libcxx/modules/std/any.inc

} // namespace std
