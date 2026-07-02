//===----------------------------------------------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef _LIBCPP___TYPE_IS_ALLOCATOR_H
#define _LIBCPP___TYPE_IS_ALLOCATOR_H

#include <__config>
#include <__cstddef/size_t.h>
#include <__type_traits/integral_constant.h>
<<<<<<<< HEAD:system/lib/libcxx/include/__type_traits/is_nothrow_default_constructible.h
========
#include <__type_traits/void_t.h>
#include <__utility/declval.h>
>>>>>>>> 6.0.2:system/lib/libcxx/include/__type_traits/is_allocator.h

#if !defined(_LIBCPP_HAS_NO_PRAGMA_SYSTEM_HEADER)
#  pragma GCC system_header
#endif

_LIBCPP_BEGIN_NAMESPACE_STD

<<<<<<<< HEAD:system/lib/libcxx/include/__type_traits/is_nothrow_default_constructible.h
template <class _Tp>
struct _LIBCPP_TEMPLATE_VIS is_nothrow_default_constructible
    : public integral_constant<bool, __is_nothrow_constructible(_Tp)> {};

#if _LIBCPP_STD_VER >= 17
template <class _Tp>
inline constexpr bool is_nothrow_default_constructible_v = __is_nothrow_constructible(_Tp);
#endif
========
template <typename _Alloc, typename = void, typename = void>
struct __is_allocator : false_type {};

template <typename _Alloc>
struct __is_allocator<_Alloc,
                      __void_t<typename _Alloc::value_type>,
                      __void_t<decltype(std::declval<_Alloc&>().allocate(size_t(0)))> > : true_type {};
>>>>>>>> 6.0.2:system/lib/libcxx/include/__type_traits/is_allocator.h

_LIBCPP_END_NAMESPACE_STD

#endif // _LIBCPP___TYPE_IS_ALLOCATOR_H
