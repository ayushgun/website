# Compile-Time Bounds Checking

> March 26, 2024

When working with random access containers in C++, such as `std::vector`, it's common to use bounds-checked interfaces like the `at()` member function to ensure safety from undefined behavior or undesirable side effects. However, these interfaces come with a trade-off: they introduce a run-time penalty due to the necessity of checking bounds at run-time. Moreover, they rely on exceptions to signal out-of-bounds access, further adding overhead.

## Current Bounds Checking

What if we could perform bounds checking at compile-time instead? Compilers can statically prove that a bounds check will always pass, allowing them to omit the checking code entirely. For example, consider the following code:

```cpp
void foo(const std::array<int, 10>& array) {
    std::cout << array.at(0) << '\n';
}
```

In this case, the compiler knows that the array always has ten elements, and we're asking for the element at index zero. Therefore, it knows that it can remove the bounds check and unconditionally return the first element of the array.

Similarly, when the bounds check is certain to fail, the compiler can generate code that [unconditionally throws an exception](https://godbolt.org/z/94K457E7x):

```cpp
void bar(const std::array<int, 10>& array) {
  std::cout << array.at(10) << '\n';  // std::out_of_range(...)
}
```

What if we could similarly leverage this compile-time information to turn these run-time exceptions into compile-time errors?

## Implementing Compile-Time Bounds Checking

To achieve compile-time bounds checking, we can exploit the GCC compiler extension `__builtin_constant_p`, which returns whether the compiler knows an (potentially run-time) expression to be a constant at compile-time. We can use this to check if a given `index` and `limit` are known at compile-time and trigger a compile-time error if a bounds violation is detected.

But how can we intentionally trigger a compilation error? We can't use `static_assert` or similar constructs, as they would always fail unconditionally. Since we're not working with expressions that C++ regards as compile-time constants, such as template parameters or `constexpr` variables, where we could apply `static_assert` or `if constexpr`. Instead, we're dealing with expressions considered by the language to be run-time values — even though the optimizer might have additional information about them.


The solution is to utilize another compiler extension, the `gcc::error` attribute. If we enable optimizations, compilation will fail if the `failed_bounds_check` call is not optimized out. The cherry on top is that, at least with GCC, we get a compiler backtrace that precisely identifies the location of the original problematic code, even through a lengthy series of inlined functions.

Here's what it looks like:
```cpp
template <typename IndexType>
void bounds_check(IndexType index, IndexType limit) {
  if (__builtin_constant_p(index) && __builtin_constant_p(limit)) {
    if (index < IndexType{0} || index >= limit) {
      [[gnu::error("out-of-bounds")]] void failed_bounds_check();
      failed_bounds_check();  // Trigger the compile-time error if the call is
                              // not optimized away
    }
  }
}
```

## Generic Interfaces

If we use concepts, we can generalize our compile-time bounds checked interface to any [random access container](https://en.cppreference.com/w/cpp/named_req/RandomAccessIterator):

```cpp
template <typename Container>
concept IndexedContainer = requires(Container container, std::size_t index) {
  container[index];
  { container.size() } -> std::same_as<std::size_t>;
};

template <IndexedContainer Container>
decltype(auto) get(Container&& container, std::size_t index) {
  bounds_check(index, container.size());
  return std::forward<Container>(container)[index];
}
```

This allows us to use the `get` function with any container that satisfies the `IndexedContainer` concept:

```cpp
std::string msg = "Hello";
std::cout << get(msg, 9);  // error: call to ‘failed_bounds_check’ declared
                           // with attribute error: out-of-bounds
```

## Known Limitations

Of course, this approach has its limitations. Aside from requiring compiler extensions to be enabled, it needs `-O1` (or higher) optimizations to be enabled so the `failed_bounds_check` call can potentially be optimized away.

## Resources

- [GCC built-in documentation](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)
- [Tristan Brindle's `flux` library](https://github.com/tcbrindle/flux) uses a similar technique, which served as the inspiration for the idea of generalized static bounds-checked interfaces
