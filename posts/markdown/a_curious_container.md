# A Curious Container

> May 20, 2023

`std::tuple`, introduced in C++11, is a distinctive container in the standard library. Unlike traditional STL containers, it is type-flexible, stack-allocated, and has a notably unique interface.

## Tuple Overview

Formally, `std::tuple` is a templated class that encapsulates a fixed-size collection of heterogeneous values, each potentially of a different type [0]. It is particularly useful for generic operations, such as returning multiple values from a function or storing function arguments for delayed execution.

Contrasting with contiguous containers like `std::vector` or `std::array`, `std::tuple` lacks a subscript operator for index-based access. Instead, it overloads `std::get` to expose tuple elements by requiring the caller to provide an element's index via a template argument [0].

For example, to access the first element in a tuple:

```cpp
std::tuple<int, double, std::string> t = {1, 4.25, "Hello World"};
std::cout << std::get<0>(t) << std::endl;
```

## Closer Examination

So why is `std::tuple` so unique as a container?

`std::tuple` stands out due to its extensive use of template metaprogramming to store heterogeneous types. Informally, `std::tuple` can be analogized to a struct:

```cpp
std::tuple<int, std::string, ...> t;

// is roughly equal to:

struct tuple {
  int value_1;
  std::string value_2;
  ...
};
```

## Looking Under The Hood

Let's examine a C++ tuple implementation. For simplicity's sake, this implementation will only hold unique types (i.e., two objects of the same type are not allowed) and will not consider move semantics.

We begin with a minimal wrapper around an object of type `T`:

```cpp
template <typename T>
struct leaf {
  T value;
};
```

We then implement our core template class, which inherits from a `leaf<T>` for every `T` in a variadic template argument pack `Ts`:

```cpp
template <typename... Ts>
struct unique_tuple : public leaf<Ts>... {
  unique_tuple(const Ts&... values) : leaf<Ts>(values)... {}
};
```

From this, we can implement a `std::get`-esque `get` template function which returns the object held in the tuple for a specified type `T`:

```cpp
// Const overload:
template <typename T, typename... Ts>
constexpr auto get(const unique_tuple<Ts...>& tuple) -> const T& {
  return static_cast<const leaf<T>&>(tuple).value;
}

// Non-const overload:
template <typename T, typename... Ts>
constexpr auto get(unique_tuple<Ts...>& tuple) -> T& {
  return static_cast<leaf<T>&>(tuple).value;
}
```

The punchline is that, since `unique_tuple` inherits from a `leaf<T>` for all `T` in `Ts`, we are allowed to cast a `unique_tuple` object into a respective `leaf<T>` object for a specified type `T`. We can then access the object stored in that `leaf<T>` via its public `value` member.

```cpp
unique_tuple<int, char> t = {1, 'a'};
std::cout << get<int>(t) << std::endl;
```

## Resources

[0] <https://en.cppreference.com/w/cpp/utility/tuple>

[1] <https://codereview.stackexchange.com/a/44832>
