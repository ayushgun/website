# Parent-Child Relationships in Multithreaded Programming

> June 17, 2023

In multithreaded programming, a process can spawn multiple threads to perform concurrent operations. The thread that creates (or spawns) a new thread is referred to as the parent thread, while the newly spawned thread is the child thread. It's crucial to note that these terms, parent and child, are primarily conceptual; in reality, all threads within a process share equal status and have access to the process's memory space. The parent-child relationship is a way to describe the initiation sequence of threads, not their hierarchal structure.

For instance, in C++, we use the `std::thread` library to create threads. Consider the following simple code:

```cpp
#include <iostream>
#include <thread>

void child_task() {
    std::cout << "Hello from Child!\n";
}

int main() {
    std::thread child_thread(child_task);
    std::cout << "Hello from Parent!\n";

    child_thread.join();
    return 0;
}
```

In the code above, the `main` function's thread (the parent) spawns `childThread` (the child) which runs concurrently with the parent thread.

## Inter-thread Communication and Synchronization

Given that all threads within a process share the same memory space, they can communicate by reading and writing to shared variables. However, this leads to the necessity of thread synchronization to avoid data races and inconsistencies.

The most common form of synchronization is achieved using locks or mutexes. Here's an example of shared data access with synchronization:

```cpp
#include <iostream>
#include <thread>
#include <mutex>

std::mutex mtx;
int shared_var = 0;

void child_task() {
    std::lock_guard<std::mutex> guard(mtx);
    shared_var++;
    std::cout << "Child incremented shared_var to "
              << shared_var
              << '\n';
}

int main() {
    std::thread child_thread(child_task);
    {
        std::lock_guard<std::mutex> guard(mtx);
        shared_var++;
        std::cout << "Parent incremented shared_var to "
                  << shared_var
                  << '\n';
    }
    child_thread.join();
    return 0;
}
```

In this example, both the parent and child threads increment a shared variable, `sharedVar`. The mutex `mtx` ensures that only one thread at a time can increment the variable, preventing data races.

## Potential Issues in Parent-Child Thread Management

Without proper management, parent-child thread relationships can run into several issues, including deadlocks, data races, and premature termination of child threads if the parent finishes executing first.

Consider the scenario where the parent thread doesn't wait for the child thread to finish its execution, as shown below:

```cpp
#include <iostream>
#include <thread>

void child_task() {
    for(int i = 0; i < 5; i++)
        std::cout << "Child says hello "
                  << i
                  << " times.\n";
}

int main() {
    // Example where parent doesn't wait
    // for child to finish, causing undefined
    // behavior
    std::thread child_thread(child_task);
    std::cout << "Parent says goodbye.\n";
    return 0;
}
```

In the above scenario, if the parent thread finishes executing before the child, it might lead to the termination of the child thread before its completion, resulting in undefined behavior.

To resolve this, C++ provides `join()` and `detach()` functions. The `join()` function makes the parent thread wait for the child thread to finish its execution, ensuring that the child thread's resources are safely reclaimed. The `detach()` function allows the child thread to execute independently of the parent, ensuring that the child thread's resources will be automatically reclaimed once it finishes execution.

## Example in Action

In my personal experience, I recently applied parent-child thread relationships while working with websocket listeners; that very scenario, in fact, inspired me to write this post.

While building a real-time research tool built on an in-house limit order book implementation, I needed to use two websocket listeners to get trade detail data and order book data from a cryptocurrency exchange. Each listener had two integral components, both required to run in parallel.

Therefore, I created a parent-child relationship between the listeners and their respective components. The setup was achieved by conceptualizing each listener as a parent thread, with its two components as child threads. This allowed each listener to function independently, with their two respective components operating concurrently.

[![](https://mermaid.ink/img/pako:eNqNUstOwzAQ_JWVpRCQWiHSWw5ICYVeqHpIoRKYw6peWquNXTnOoUT5d5xHrQZRxC3ZzMzuTKZiay2IxSwIKqmkjaEK7ZZyCmMIBZpdCDXUQcAVVxuDhy0sU64AVtndO2cLI8ikWu_gWRaWFBlYbg2h4OwDxmM4R0zRImdueg-LtEMNFDyxl_-Dn006cHNCNumZ0FNP4h3_5SDQUuEXn6_sCV6tY2RWG09oXTYT3BBcJ6vMoW_8jZH7OHcZkb3of2lQ0G1KhYVUCkAlICkGZhKF-2MhCx_JE6EtDc26tIepRP9VPZmKBhFFvdBwZ6fZzr6886S5xJyfcgUP2SvMGpdopVY_4ot-iy-6FB8bsZxMjlK47lWNDmdt7ziL3WPTPM64qh0OS6uzo1qz2JqSRqxsf-lUoutjzuJP3Bd--iik2-aH1L7Ou4a3RR-xA6o3rU_E-hvZnfQI?type=png)](https://mermaid.live/edit#pako:eNqNUstOwzAQ_JWVpRCQWiHSWw5ICYVeqHpIoRKYw6peWquNXTnOoUT5d5xHrQZRxC3ZzMzuTKZiay2IxSwIKqmkjaEK7ZZyCmMIBZpdCDXUQcAVVxuDhy0sU64AVtndO2cLI8ikWu_gWRaWFBlYbg2h4OwDxmM4R0zRImdueg-LtEMNFDyxl_-Dn006cHNCNumZ0FNP4h3_5SDQUuEXn6_sCV6tY2RWG09oXTYT3BBcJ6vMoW_8jZH7OHcZkb3of2lQ0G1KhYVUCkAlICkGZhKF-2MhCx_JE6EtDc26tIepRP9VPZmKBhFFvdBwZ6fZzr6886S5xJyfcgUP2SvMGpdopVY_4ot-iy-6FB8bsZxMjlK47lWNDmdt7ziL3WPTPM64qh0OS6uzo1qz2JqSRqxsf-lUoutjzuJP3Bd--iik2-aH1L7Ou4a3RR-xA6o3rU_E-hvZnfQI)

## Conclusion

Parent-child relationships can improve code organization and structure, while synchronization mechanisms like mutexes allow safe shared data access. However, improper thread management can lead to data races, deadlocks, or premature termination. Thus, using appropriate synchronization and management techniques is essential in C++ multithreaded programming.
