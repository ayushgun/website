# A Curious Container

> May 20, 2023

`std::tuple`, introduced in C++11, is one of the most interesting containers available in the STL.

Why? It doesn't adhere to the conventional traits of STL containers. It’s a curious mix of being type agnostic, stack allocated, and distinctively different in its interface.

## What exactly is `std::tuple`?

Formally, `std::tuple` is a template class with an ability to encapsulate a collection of heterogeneous values, each potentially of a different type, fixed in size. It’s particularly invaluable when there’s a need to return multiple values from a function, or when dealing with complex data manipulations involving mixed types.

Unlike other contiguous containers, like `std::vector` or `std::array`, `std::tuple` doesn't define a subscript operator for accessing elements by index. Instead, because of its type agnostic nature, elements in a `std::tuple` are individually accessible using the `std::get<I>` function, which takes the index of the desired element as a template argument.

```cpp
#include <iostream>
#include <tuple>
#include <string>

int main() {
    std::tuple<int, double, std::string> t{1, 4.5, "Hello World"};
    std::cout << std::get<0>(t) << '\n';
}
```

## Looking Under the Hood

So why is `std::tuple` so unique as a container? It's the byproduct of extensive template-meta programming, especially in regards to its type safety.

Template metaprogramming allows `std::tuple` to generate code that is tailored to handle these specific types, allowing for type safety and stack allocation. Functions like `std::get<I>`, which retrieve elements from a tuple, rely on template arguments to deduce the type and index of the element at compile time. Recursive template instantiations and specializations are often employed to navigate through the tuple's elements, making operations like accessing, modifying, and iterating over elements both type-safe, yet uniquely implemented.

Fundamentally, under the hood, `std::tuple` can be thought of being directly translated to a struct.

```cpp
std::tuple<int, std::string> t{1, "Hello World"};

// is equivalent to...

struct tuple {
    int element_1{1};
    std::string element_2{"Hello World"};
};
```
