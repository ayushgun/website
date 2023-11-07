# A Curious Container

> May 20, 2023

`std::tuple`, introduced in C++11, is one of the most interesting containers available in the STL.

Why? It doesn't adhere to the conventional traits of STL containers. It's a curious mix of being type agnostic, stack allocated, and distinctively different in its interface.

## What exactly is `std::tuple`?

Formally, `std::tuple` is a template class with an ability to encapsulate a collection of heterogeneous values, each potentially of a different type, fixed in size. It's particularly invaluable when there's a need to return multiple values from a function, or when dealing with complex data manipulations involving mixed types.

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

## A Closer Examination

So why is `std::tuple` so unique as a container? It's the byproduct of extensive template-meta programming, especially in regards to its type safety.

Template metaprogramming allows `std::tuple` to generate code that is tailored to handle these specific types, allowing for type safety and stack allocation. Functions like `std::get<I>`, which retrieve elements from a tuple, rely on template arguments to deduce the type and index of the element at compile time. Recursive template instantiations and specializations are often employed to navigate through the tuple's elements, making operations like accessing, modifying, and iterating over elements both type-safe, yet uniquely implemented.

Fundamentally, under the hood, `std::tuple` can be thought of being directly translated to a struct.

```cpp
std::tuple<int, std::string> t{1, "Hello World"};

// is roughly equivalent to...

struct Tuple {
    int element_1{1};
    std::string element_2{"Hello World"};
};
```

## Looking Under The Hood

To unravel the nuances and intricacies of `std::tuple`, let's delve deeper into a refined version of its implementation. This refined version has been written to be readable and comprehensible, thanks to auxiliary template structures and variadic templates.

We initiate our journey with helper templates. These helpers, though succinct, play a pivotal role in unraveling the complexity of `std::tuple`. Take, for instance, the `id` and `type_of` templates, instrumental for type manipulations, or the `sizes` template, used for generating sequences of numbers.

```cpp
template <typename T>
struct id { using type = T; };

template <typename T>
using type_of = typename T::type;

template <size_t... N>
struct sizes : id<sizes<N...>> {};
```

The `Choose` template enables the selection of the N-th element from a type list, while `Range` generates a sequence of numbers, a mechanism pivotal for indexing and accessing elements within our tuple.

```cpp
// Choose the N-th element in list <T...>
template <size_t N, typename... T>
struct Choose;

template <size_t N, typename H, typename... T>
struct Choose<N, H, T...> : Choose<N-1, T...> {};

template <typename H, typename... T>
struct Choose<0, H, T...> : id<H> {};

template <size_t N, typename... T>
using choose = type_of<Choose<N, T...>>;

// given L>=0, generate sequence <0, ..., L-1>
template <size_t L, size_t I = 0, typename S = sizes<> >
struct Range;

template <size_t L, size_t I, size_t... N>
struct Range<L, I, sizes<N...>> : Range<L, I+1, sizes<N..., I>> {};

template <size_t L, size_t... N>
struct Range<L, L, sizes<N...>> : sizes<N...> {};

template <size_t L>
using range = type_of<Range<L>>;
```

With the foundational templates at our disposal, constructing the tuple becomes elegant and efficient. The `TupleElem` class template ensures each element is encapsulated with its index, enabling direct access.

```cpp
// Represents a single tuple element
template <size_t N, typename T>
class TupleElem {
    T elem;
public:
    T& get() { return elem; }
    const T& get() const { return elem; }
};
```

The `TupleImpl` class template leverages multiple inheritance and variadic templates to encapsulate each element within the tuple, each uniquely accessible through its index, thanks to the `get` method.

```cpp
template <typename N, typename... T>
class TupleImpl;

template <size_t... N, typename... T>
class TupleImpl<sizes<N...>, T...> : public TupleElem<N, T...> {
    template <size_t M> using pick = choose<M, T...>;
    template <size_t M> using elem = TupleElem<M, pick<M>>;

public:
    template <size_t M>
    pick<M>& get() { return elem<M>::get(); }

    template <size_t M>
    const pick<M>& get() const { return elem<M>::get(); }
};

template <typename... T>
struct Tuple : TupleImpl<range<sizeof...(T)>, T...> {
    static constexpr std::size_t size() { return sizeof...(T); }
};
```

In essence, each element, encapsulated within its unique type, becomes directly accessible, ensuring type safety and efficiency. The implementation is elegant, forgoing the need for intricate specializations or static assertions.

## Resources

If you'd like to dive deeper, here are some resources I found interesting:

- <https://en.cppreference.com/w/cpp/utility/tuple>
- <https://en.cppreference.com/w/cpp/utility/tuple/get>
- <https://codereview.stackexchange.com/a/44832>
