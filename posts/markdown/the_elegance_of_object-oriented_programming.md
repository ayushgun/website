# The Elegance of Object-Oriented Paradigms

> June 29, 2023

Last summer, I was building a learning management system for my non-profit tutoring startup, [LearnForsyth](https://learnforsyth.org). Initially, the project was small and, like many lazy developers, I thought it would be fine to take a procedural approach. However, as the codebase grew, I faced difficulties in managing the relationships between workspaces, students, and tutors. When I decided to channel my inner [CS 2340](https://gt-student-wiki.org/mediawiki/index.php/CS_2340) and follow the OOP paradigm by refactoring the code into classes and objects, the structure became much clearer and the codebase more maintainable, which was a game-changer for the project.

Before delving into why I prefer OOP, let's briefly touch upon Functional Programming (FP). FP is a paradigm where the process of computation is treated as the evaluation of mathematical functions and avoids changing state and mutable data. Here's an example in Haskell, a purely functional language:

```haskell
factorial :: Integer -> Integer
factorial 0 = 1
factorial n = n * factorial (n - 1)
```

This function computes the factorial of a number using recursion, a common technique in FP.

## The Intuitive Nature of Object-Oriented Programming

In my experience, OOP is inherently intuitive, as it mirrors real-world entities and their interactions. The encapsulation principle, a cornerstone of OOP, allows for bundling data and methods that operate on that data within a single unit, known as a class. For instance, consider a simple `Car` class in C++:

```cpp
class Car {
private:
    std::string make;
    std::string model;
    int year;

public:
    Car(std::string make, std::string model, int year) : make(make), model(model), year(year) {}

    void honk() {
        std::cout << "Honk!\n";
    }
};
```

This class encapsulates the properties of a car and provides a method to honk. The encapsulation principle in OOP is akin to how real-world objects have states and behaviors.

## The Power of Polymorphism

Polymorphism is another pillar of OOP that allows objects of different classes to be treated as objects of a common superclass. This feature is particularly powerful when designing extensible systems. In C++, polymorphism is achieved through inheritance and virtual functions. Consider an example where different types of shapes need to be drawn:

```cpp
class Shape {
public:
    virtual void draw() const = 0; // Pure virtual function
};

class Circle : public Shape {
public:
    void draw() const override {
        std::cout << "Drawing a circle.\n";
    }
};

class Square : public Shape {
public:
    void draw() const override {
        std::cout << "Drawing a square.\n";
    }
};
```

With polymorphism, you can create a collection of `Shape` pointers and call the appropriate `draw` method without knowing the actual derived class:

```cpp
std::vector<Shape*> shapes = {new Circle(), new Square()};
for (Shape* shape : shapes) {
    shape->draw();
}
```

## The Robustness of Abstraction and Information Hiding

Abstraction and information hiding are essential for creating robust systems. In OOP, classes serve as blueprints, and objects are instances of these classes. By using private and protected access specifiers, OOP allows for hiding the internal state and requiring interaction through well-defined interfaces. This encapsulation ensures that objects maintain valid states even in complex systems.

In functional programming, while it's possible to achieve abstraction using closures and modules, the declarative nature of functional programming sometimes leads to a lack of clarity regarding the flow of data and state changes, especially in large codebases.

## The Expressiveness of Design Patterns

OOP is known for its rich set of design patterns, which are reusable solutions to common programming problems. Patterns like Singleton, Factory, and Observer are widely used in software engineering. These patterns are not just code snippets but involve class structures, inheritance, and interfaces.

For example, the Observer pattern in C++:

```cpp
class Observer {
public:
    virtual void update(int data) = 0;
};

class ConcreteObserver : public Observer {
private:
    int observerState;
public:
    void update(int data) override {
        observerState = data;
        std::cout << "Observer state updated to " << observerState << '\n';
    }
};

class Subject {
private:
    std::vector<Observer*> observers;
    int state;
public:
    void attach(Observer* observer) {
        observers.push_back(observer);
    }

    void setState(int newState) {
        state = newState;
        notifyObservers();
    }

    void notifyObservers() {
        for (Observer* observer : observers) {
            observer->update(state);
        }
    }
};
```

In this example, the Observer pattern allows objects to observe changes in another object's state. This pattern is expressive and aligns well with OOP principles.

Functional programming, on the other hand, tends to rely on function composition and recursion. While functional programming has its own set of patterns, they are often less expressive when it comes to modeling complex interactions between objects. For instance, in Haskell, you might use higher-order functions to achieve similar behavior:

```haskell
type Observer = Int -> IO ()

notifyObservers :: [Observer] -> Int -> IO ()
notifyObservers observers state = mapM_ (\observer -> observer state) observers
```

While this functional approach is concise, it lacks the expressiveness and structure provided by the OOP approach.

# Conclusion

While functional programming has its merits, especially in concurrency and stateless computation, the intuitive nature, polymorphism, robust abstraction, and expressive design patterns of Object-Oriented Programming make it a more appealing choice for many software engineering tasks. The ability to model real-world entities and their interactions in an intuitive and modular way is where OOP shines, and this is why I personally prefer OOP paradigms over functional programming paradigms.
