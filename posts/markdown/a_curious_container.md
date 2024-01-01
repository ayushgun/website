# A Curious Container

> May 20, 2023

`std::tuple`, introduced in C++11, is one of the most interesting containers available in the standard library.

Why? `std::tuple` defies traditional STL container characteristics with its unique features like being type-flexible, stack-allocated, and having a distinct interface.

## What exactly is `std::tuple`?

Formally, `std::tuple` is a templated class that encapsulates a fixed-size collection of heterogeneous values, each potentially of a different type. It shines in scenarios requiring multiple return values from a function or in complex data operations involving varied types.

Contrasting with contiguous containers like `std::vector` or `std::array`, `std::tuple` lacks a subscript operator for index-based access. Instead, its type-flexible nature demands element access via `std::get<I>`, which uses a template argument to specify the element's index.

```cpp
#include <iostream>
#include <tuple>
#include <string>

int main() {
    std::tuple<int, double, std::string> t{1, 4.5, "Hello World"};
    std::cout << std::get<0>(t) << '\n'; // prints 1 to stdout
}
```

## A Closer Examination

So why is `std::tuple` so unique as a container?

`std::tuple` stands out due to its extensive use of template metaprogramming, which in this case, improves type safety and enables stack allocation. Functions like `std::get<I>` utilize compile-time type and index deduction. Recursive template instantiation and specialization facilitate safe and unique operations on the tuple's elements.

Internally, `std::tuple` can be analogized to a struct.

```cpp
std::tuple<int, std::string> t{1, "Hello World"};

// is roughly equivalent to...

struct Tuple {
    int element_1{1};
    std::string element_2{"Hello World"};
};
```

## Looking Under The Hood

Let's examine a simplified `std::tuple` implementation.

We start with foundational templates, which are crucial for type manipulations and sequence generation.

```cpp
template <typename Type>
struct Identifier { using type = Type; };

template <typename Type>
using TypeOf = typename Type::type;

template <size_t... Indices>
struct IndexSequence : Identifier<IndexSequence<Indices...>> {};
```

The `ElementSelector` template selects the N-th element from a type list, while `SequenceGenerator` creates numerical sequences, essential for indexing and accessing tuple elements.

```cpp
// Select the N-th element in list <Types...>
template <size_t Index, typename... Types>
struct ElementSelector;

template <size_t Index, typename Head, typename... Tail>
struct ElementSelector<Index, Head, Tail...> : ElementSelector<Index-1, Tail...> {};

template <typename Head, typename... Tail>
struct ElementSelector<0, Head, Tail...> : Identifier<Head> {};

template <size_t Index, typename... Types>
using SelectElement = TypeOf<ElementSelector<Index, Types...>>;

// Generate sequence <0, ..., Length - 1>
template <size_t Length, size_t Current = 0, typename Sequence = IndexSequence<> >
struct SequenceGenerator;

template <size_t Length, size_t Current, size_t... Numbers>
struct SequenceGenerator<Length, Current, IndexSequence<Numbers...>> : SequenceGenerator<Length, Current+1, IndexSequence<Numbers..., Current>> {};

template <size_t Length, size_t... Numbers>
struct SequenceGenerator<Length, Length, IndexSequence<Numbers...>> : IndexSequence<Numbers...> {};

template <size_t Length>
using GenerateSequence = TypeOf<SequenceGenerator<Length>>;
```

The `TupleElement` class template encapsulates each tuple element with its index, allowing direct access.

```cpp
// Represents an individual tuple element
template <size_t Index, typename Element>
class TupleElement {
    Element value;
public:
    Element& getValue() { return value; }
    const Element& getValue() const { return value; }
};
```

The `TupleImplementation` class template uses multiple inheritance and variadic templates to compose the tuple, with elements uniquely accessible via their index.

```cpp
template <typename Indices, typename... Elements>
class TupleImplementation;

template <size_t... Indices, typename... Elements>
class TupleImplementation<IndexSequence<Indices...>, Elements...> : public TupleElement<Indices, Elements>... {
    template <size_t Index> using PickElement = SelectElement<Index, Elements...>;
    template <size_t Index> using Element = TupleElement<Index, PickElement<Index>>;

public:
    template <size_t Index>
    PickElement<Index>& getElement() { return Element<Index>::getValue(); }

    template <size_t Index>
    const PickElement<Index>& getElement() const { return Element<Index>::getValue(); }
};

template <typename... Elements>
struct Tuple : TupleImplementation<GenerateSequence<sizeof...(Elements)>, Elements...> {
    static constexpr std::size_t size() { return sizeof...(Elements); }
};
```

This implementation encapsulates each element in its unique type, ensuring type safety and efficiency, elegantly bypassing the need for complex specializations.

## Resources

If you'd like to learn more about `std::tuple`, here are some resources I found informative:

- <https://en.cppreference.com/w/cpp/utility/tuple>
- <https://en.cppreference.com/w/cpp/utility/tuple/get>
- <https://codereview.stackexchange.com/a/44832>
