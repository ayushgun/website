# Compile-Time Bounds Checking

> March 26, 2024

When working with random access containers in C++, such as `std::vector`, using bounds-checked interfaces like the `at()` member function ensures safety from undefined behavior. However, these interfaces introduce a run-time penalty due to the necessity of checking bounds at run-time and relying on exceptions to signal out-of-bounds access.

## Current Bounds Checking

What if we could perform bounds checking at compile-time instead? Compilers can statically prove that a bounds check will always pass, allowing them to omit the checking code entirely. Consider the following code:

```cpp
void foo(const std::array<int, 10>& array) {
  std::cout << array.at(0) << '\n';
}
```

Here, the compiler knows the array always has ten elements and can remove the bounds check, returning the first element unconditionally.

Similarly, when the bounds check is certain to fail, the compiler can generate code that [unconditionally throws an exception](https://godbolt.org/z/94K457E7x):

```cpp
void bar(const std::array<int, 10>& array) {
  std::cout << array.at(10) << '\n';  // throws std::out_of_range
}
```

What if we could leverage this compile-time information to turn these run-time exceptions into compile-time errors?

## Implementing Compile-Time Bounds Checking

We can exploit the GCC compiler extension `__builtin_constant_p`, which returns whether the compiler knows a run-time expression to be a constant at compile-time. We can use this to check if a given `index` and `limit` are known at compile-time and trigger a compile-time error if a bounds violation is detected.

To intentionally trigger a compilation error, we utilize the `gcc::error` attribute. With optimizations enabled, compilation will fail if the `failed_bounds_check` call is not optimized away and provide a compiler backtrace that identifies the location of the original problematic code.

Here's what it looks like:

```cpp
template <typename IndexType>
void bounds_check(IndexType index, IndexType limit) {
  if (__builtin_constant_p(index) && __builtin_constant_p(limit)) {
    if (index < IndexType{0} || index >= limit) {
 [[gnu::error("out-of-bounds")]] void failed_bounds_check();
      failed_bounds_check();  // Triggers the compile-time error if the call is not optimized away
    }
  }
}
```

## Generic Interface

Using concepts, we can generalize our compile-time bounds-checked interface to any random access container:

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

This allows us to use the `get` template function with any container that satisfies the `IndexedContainer` concept:

```cpp
std::string msg = "Hello";
std::cout << get(msg, 9);  // error: call to ‘failed_bounds_check’ declared with attribute error: out-of-bounds
```

## Known Limitations

This approach requires compiler extensions to be enabled and optimizations (`-O1` or higher) so the `failed_bounds_check` call can potentially be optimized away.

## Resources

- [GCC built-in documentation](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)
- [Tristan Brindle's `flux` library](https://github.com/tcbrindle/flux) uses a similar technique and served as the inspiration for generalized static bounds-checked interfaces.
