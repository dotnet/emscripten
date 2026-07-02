//===----------------------------------------------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef _LIBCPP___TYPE_TRAITS_IS_CHAR_LIKE_TYPE_H
#define _LIBCPP___TYPE_TRAITS_IS_CHAR_LIKE_TYPE_H

#include <__config>
<<<<<<<< HEAD:system/lib/libcxx/include/__type_traits/is_trivially_default_constructible.h
#include <__type_traits/integral_constant.h>
========
#include <__type_traits/conjunction.h>
#include <__type_traits/is_standard_layout.h>
#include <__type_traits/is_trivially_constructible.h>
#include <__type_traits/is_trivially_copyable.h>
>>>>>>>> 6.0.2:system/lib/libcxx/include/__type_traits/is_char_like_type.h

#if !defined(_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER)
#  pragma GCC system_header
#endif

_LIBCPP_BEGIN_NAMESPACE_STD

<<<<<<<< HEAD:system/lib/libcxx/include/__type_traits/is_trivially_default_constructible.h
template <class _Tp>
struct _LIBCPP_TEMPLATE_VIS is_trivially_default_constructible
    : public integral_constant<bool, __is_trivially_constructible(_Tp)> {};

#if _LIBCPP_STD_VER >= 17
template <class _Tp>
inline constexpr bool is_trivially_default_constructible_v = __is_trivially_constructible(_Tp);
#endif
========
template <class _CharT>
using _IsCharLikeType _LIBCPP_NODEBUG =
    _And<is_standard_layout<_CharT>, is_trivially_default_constructible<_CharT>, is_trivially_copyable<_CharT> >;
>>>>>>>> 6.0.2:system/lib/libcxx/include/__type_traits/is_char_like_type.h

_LIBCPP_END_NAMESPACE_STD

#endif // _LIBCPP___TYPE_TRAITS_IS_CHAR_LIKE_TYPE_H
