# Parallel Programming Models

> April 5, 2025

Yesterday, I spoke at the [Programming Languages Club at Georgia Tech](https://dtyped.netlify.app) about exposing models for parallelism in programming languages. You can find the slides [here](https://cdn.discordapp.com/attachments/1345041727899176980/1357803322240798830/Parallel_Programming_Models.pdf?ex=67f2d9e2&is=67f18862&hm=c9cdad2eafb1d22665ed424a99d117c9f59208354c68d713c0499b24cc81d28c&). This post is a synopsis of the content I went over in my talk.

## Motivation for Parallelism

In the early days of computing, improving performance was straightforward: make the processor faster. During the 1990s, chip manufacturers simply shrank transistors with each generation, as described by Moore's Law (transistor density doubling roughly every two years). Smaller transistors meant more of them could fit in the same area and signals had shorter distances to travel, yielding higher clock speeds and lower power per operation. For a while, clock speeds and transistor counts increased hand-in-hand, making programs run faster without any changes to software.

However, this approach hit physical limits. As transistors got denser, chips ran into problems with heat dissipation and manufacturing complexity (e.g. the challenges of 3nm and smaller process nodes). Chip designers reached a point of diminishing returns: simply adding more transistors or upping the clock rate began to yield less improvement, while generating more heat and cost. You can't indefinitely get more juice by squeezing the same lemon.

The industry's response in the mid-2000s was to scale out horizontally by adding multiple processing cores on a single chip. Instead of one super-fast core, you get several moderately fast cores working in parallel. For example, an Apple M1 Pro has 8 cores, and high-end server processors (like Intel Xeon) have up to 144 cores. Each core can run tasks in parallel independently, so an application can *potentially* run N times faster with N cores (if the work can be evenly divided).

### Different Forms of Parallelism

- Data Parallelism: performing the same operation on different pieces of data simultaneously (e.g. adding two arrays element-wise in parallel).
- Task Parallelism: running independent tasks or functions in parallel, which may be doing different things (e.g. a web server handling multiple requests on different threads).
- Device Parallelism: spreading work across multiple physical devices (like using multiple servers, or offloading some tasks to a GPU or TPU). This can be seen as a coarse-grained form of task parallelism across machines or specialized processors.

Modern high-performance computing often combines these forms. In this post, we'll mostly concentrate on data parallelism – making an algorithm execute faster by applying it in parallel on many data elements.


## SIMD

Adding more cores isn't the only way to speed up computation; we can also make each core itself do more work in parallel. Modern CPUs already exploit a lot of internal parallelism with techniques like instruction pipelining, out-of-order execution, and speculative execution. Pipelining, for instance, splits the execution of an instruction into stages (fetch, decode, execute, etc.) so that multiple instructions are in progress concurrently (like an assembly line).

SIMD is a form of internal data parallelism at the instruction level. The CPU has special vector registers that are, say, 128, 256, or 512 bits wide, which can be viewed as containing multiple lanes (chunks) of smaller data elements. A single SIMD instruction operates on all lanes in one go. For example, with 128-bit NEON registers on an ARM processor, each register can hold four 32-bit integers (4 * 32 = 128 bits). One SIMD add instruction can then add four pairs of integers at once (as opposed to four separate scalar add instructions).

Under the hood, using SIMD means utilizing these wide registers and the corresponding instruction set extensions (SSE, AVX on x86, NEON on ARM, etc.). High-level languages usually expose SIMD through intrinsics – special macros that map directly to SIMD instructions. For instance, here's a simple example using ARM NEON intrinsics to add two vectors of integers:
```cpp
#include <arm_neon.h>

// 128-bit NEON registers: can hold 4 int32 values each
int32x4_t a = {1, 2, 3, 4};
int32x4_t b = {10, 20, 30, 40};

// Use a NEON intrinsic to add all four lanes in one instruction
int32x4_t result = vaddq_s32(a, b);
```

Here, `vaddq_s32` is a SIMD addition that processes four 32-bit integers per register in one instruction. The `_q` in the name indicates a 128-bit quadword operation (four lanes in this case).

Real-world data rarely fits perfectly into one SIMD register, so programmers use vector chunking (or strip-mining) to handle arbitrarily large arrays with SIMD. The idea is to break the data into chunks the size of the vector registers, process those chunks in a vectorized loop, and then handle any leftover elements with a scalar loop. For example:
```cpp
int a[1030], b[1030], result[1030];

std::size_t i = 0;

for (; i + 4 <= 1030; i += 4) {
  int32x4_t va = vld1q_s32(&a[i]);      // Load 4 elements from `a` into a SIMD vector
  int32x4_t vb = vld1q_s32(&b[i]);      // Load 4 elements from `b` into a SIMD vector
  int32x4_t vr = vaddq_s32(va, vb);     // Element-wise addition on both vectors
  vst1q_s32(&result[i], vr);            // Store contents of output vector to `result`
}

// Scalar spillover loop for the remaining elements
for (; i < 1030; i++) {
  result[i] = a[i] + b[i];
}
```

You might wonder if compilers can do this for you automatically — the answer is yes, sometimes. Modern compilers can auto-vectorize simple loops, replacing scalar operations with SIMD instructions when it's safe to do so. See [this Godbolt example](https://godbolt.org/z/efebMs1f4), where both a scalar loop and an explicitly vectorized version compile down to the same `vpslld` instruction — a packed shift-left that multiplies four 32-bit integers in parallel.

However, compilers are not omniscient. Auto-vectorization might fail if the code is too complex or if there are potential data dependencies the compiler can't prove won't overlap. In performance-critical code, developers still often resort to using intrinsics or inline assembly to explicitly vectorize algorithms when the compiler can't do it automatically.

## Parallelism on CPU

To leverage multiple CPU cores, we use threads. A thread is the smallest unit of execution that can run concurrently with other threads while sharing the same memory space. Most languages offer an API for spawning threads (OS-managed threads) and some have higher-level abstractions (like thread pools or "green" user-space threads). The operating system's scheduler distributes time slices on CPU cores for each thread in a process. In a multi-core system, threads can potentially run in parallel (on different cores) – not just interleaved by time slicing.

Creating a new OS thread is relatively expensive (it generally involves a system call and allocations), so you don't want to spawn threads frivolously. For example, suppose we want to multiply every element in a large array by 2 using an 8-core CPU. One naive approach would be to create a new thread for each element in the array:
```cpp
std::array<int, 160000> data = {0, 1, 2, /*...*/};

for (std::size_t i = 0; i < data.size(); ++i) {
  // Spawn a thread to double `a[i]`
  std::thread([&data, i] { data[i] *= 2; }).detach();
}
```

This is a terrible idea – it would launch 160,000 threads! The overhead of creating and scheduling that many threads would overwhelm any gain from parallelism. In fact, it would likely run slower than just doing the loop in one thread, due to context switch overhead and contention. Modern CPUs also feature Hyper-Threading (Intel) or similar simultaneous multithreading, where each core can run two hardware threads, but those still share the core's execution units. Hyper-threading can improve throughput for workloads that often wait on memory, but it doesn't double performance and can hurt latency-sensitive tasks. In general, you want at most one thread per physical core for heavy compute work.

A smarter strategy for the example above is to use a fixed number of threads equal to the core count, and divide the array into chunks. For 160,000 elements on 8 cores, each thread can handle 20,000 elements:
```cpp
std::array<int, 160000> data = {0, 1, 2, /*...*/};
std::size_t core_count = 8;
std::size_t chunk_size = data.size() / core_count;

for (std::size_t i = 0; i < core_count; ++i) {
  std::size_t start = i * chunk_size;
  std::size_t end = start + chunk_size;

  // Launch thread to double all elements in assigned chunk
  threads.emplace_back([&data, start, end] {
    for (std::size_t j = start; j < end; ++j) { data[j] *= 2; }
  });
}
```

This way, only 8 threads are created, each doing a hefty chunk of work. There is negligible scheduling overhead beyond those 8 threads. A nice bonus: a good compiler will also auto-vectorize the inner loop for each thread. In this case, GCC will emit a vector instruction (`vpslld` on x86) to multiply 4 integers at a time by 2.

### False Sharing

One pitfall when parallelizing on CPUs is false sharing, which stems from how caches work. Each core in a modern system has its own caches, and memory is cached in blocks of e.g. 64 bytes called cache lines. When one core writes to a memory address, any other core that has that address cached must be alerted (cache coherence protocols will invalidate or update the line in other cores' caches). False sharing occurs when two threads on different cores are modifying independent variables that happen to reside on the same cache line. Each update ping-pongs the cache line between cores, causing stalls, even though the threads aren't actually sharing data in a logical sense.

Consider this contrived example:
```cpp
struct {
  std::atomic<int> x{0};
  std::atomic<int> y{0};
} foo;

std::thread t1([&] { for (std::size_t i = 0; i < 1'000'000; ++i) { ++foo.x; } });
std::thread t2([&] { for (std::size_t i = 0; i < 1'000'000; ++i) { ++foo.y; } });
```

Here two threads are incrementing different members of the same struct `foo`. Here, `x` and `y` will be on the same cache line. This will trigger continuous cache invalidation traffic between the two cores as they each modify their part of `foo` – thrashing the cache line back and forth.

To address false sharing, we can pad or separate data so that concurrently modified variables reside on different cache lines. For example, we can insert padding bytes between `x` and `y`:
```cpp
constexpr std::size_t cacheline_size = std::hardware_destructive_interference_size;

struct {
  alignas(cacheline_size) std::atomic<int> x{0};
  alignas(cacheline_size) std::atomic<int> y{0};
} foo;

std::thread t1([&] { for (std::size_t i = 0; i < 1'000'000; ++i) { ++foo.x; } });
std::thread t2([&] { for (std::size_t i = 0; i < 1'000'000; ++i) { ++foo.y; } });
```

Most hardware uses 64-byte cache lines, and C++17 provides the compile-time constant `std::hardware_destructive_interference_size` to query the cache line size on an architecture. With this change, `x` and `y` will be aligned on different cache lines, so each thread mostly stays in its own cache without constantly invalidating the other. A simple microbenchmark on my machine shows the difference: without padding, the two-thread test took ~34×10^6 ns; with padding, ~7.1×10^6 ns. That's about a 4.8× speedup gained solely by eliminating false sharing.

## Parallelism on GPU

While CPUs have a handful of cores optimized for sequential performance, GPUs have thousands of smaller cores designed for massive data parallelism. A GPU is essentially a compute fabric for running the same operation on a huge number of data elements in parallel. NVIDIA's CUDA framework (and similar models like OpenCL) let programmers launch a kernel (a function to execute on the GPU) across a grid of threads. The GPU hardware groups threads into blocks and warps for scheduling:
- A block is a group of threads that execute on the same multiprocessor (SM in NVIDIA terms) and can cooperate via fast shared memory.
- A grid is the collection of all blocks launched for a given kernel invocation. You might launch, say, 1000 blocks of 256 threads each, for a total of 256,000 threads executing your kernel in parallel.

Importantly, GPU threads follow a different execution model known as SIMT (Single Instruction, Multiple Threads). Threads are executed in warps (e.g. 32 threads in NVIDIA GPUs) that proceed in lockstep on the same instruction. In effect, a warp is like a 32-wide SIMD unit – all threads run the same instruction at a time. They can have different data and even take different control paths, but when a warp diverges (e.g. an if/else where half the threads take the if-branch and half take else), the GPU will execute one branch first on those threads while the others are inactive, then the other branch. This means divergent branching within a warp incurs a serial execution of the divergent paths (affecting performance). To get best performance on GPUs, you want threads in a warp to execute the same path as much as possible. Unlike CPU threads, which are fully independent, GPU threads in a warp must execute in lockstep (at least at the granularity of warp instructions).

Another key difference is memory: the CPU (host) and GPU (device) have separate memory spaces. Data must be transferred over relatively slow PCIe or NVLink buses to get to/from GPU memory. Within the GPU, memory access is optimized through a hierarchy: each thread has registers, each thread block has fast shared memory (like a user-managed L1 cache scratchpad), and there is large global memory (device VRAM) accessible to all threads. Effective GPU programming involves structuring computations to maximize use of fast shared memory and coalesced access to global memory.

### Triton Kernels

Writing CUDA C++ directly can be verbose and non-portable. Triton is a newer approach: it's a domain-specific language embedded in Python that aims to simplify GPU programming while remaining close to hardware. Triton provides a JIT compiler that lowers your Pythonic kernel code through multiple stages (Triton -> Triton IR -> MLIR -> PTX or other backend). Under the hood it generates code similar to what you'd write in CUDA, but you get to work in Python with auto-parallelization over a grid of threads.

Below is a simple Triton kernel that multiplies every element of an array by 2 (mirroring our earlier CPU example). We define the kernel with a special `@triton.jit` decorator and launch it on the GPU:
```py
@triton.jit
def mul_kernel(data_ptr, n: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(axis=0)
    block_start = pid * BLOCK_SIZE                    # Starting index for data block
    offsets = block_start + tl.arange(0, BLOCK_SIZE)  # Indices that block processes
    mask = offsets < n                                # Exclude out-of-bounds items
    x = tl.load(data_ptr + offsets, mask=mask)        # Load items from global memory
    x = x * 2
    tl.store(data_ptr + offsets, x, mask=mask)        # Store result to global memory


# Create array of 160,000 elements and launch kernel
data = torch.arange(160000, device=torch.device("cuda:0"), dtype=torch.int32)
grid = lambda meta: (triton.cdiv(data.numel(), meta['BLOCK_SIZE']),)
mul_kernel[grid](data, data.numel(), BLOCK_SIZE=1024)
```

Here Triton handles the boilerplate of launching a grid of thread blocks. We specify a block size of 1024 threads. The `pid = tl.program_id(axis=0)` gives the block index, and then we compute a vector of 1024 offsets for that block. The `tl.arange(0, BLOCK_SIZE)` construct is like getting a SIMD lane ID for each thread in the block, and `tl.load`/`tl.store` operate on all those lanes in parallel with proper masking for out-of-bounds. Essentially, each Triton block processes 1024 elements at a time, and Triton figures out how many blocks to launch to cover all 160,000 elements.

Triton's goal is to be portable across GPU vendors (and potentially other accelerators), not just NVIDIA. This is why it leans on MLIR to eventually target various backends. The downside is that achieving peak performance on every new hardware requires a lot of compiler intelligence. It's difficult to encode all the low-level architectural quirks in a portable compiler, so hand-tuned vendor-specific libraries can still have an edge. In practice, Triton often gets close-to-native performance but not absolute maximum. For example, optimized Triton kernels have achieved around 75% of the throughput of equivalent cuDNN (NVIDIA's highly optimized library) kernels. In one benchmark on transformer-layer operations, Triton implementations were typically within 1.2–1.5× of CUDA's performance (some nearly equal). This is a great trade-off for many cases: you write far less low-level code and still get most of the performance.

## First-class Parallelism

Almost.

One observation about the state of parallel programming: we've been bolting parallelism onto fundamentally single-threaded languages. Threads, vector intrinsics, CUDA kernels – these are usually provided via libraries, extensions, or compiler tricks layered on top of a base language model that is sequential. As a result, developers have to constantly switch mental models between "normal" serial code and parallel constructs (which often feel foreign to the language). Wouldn't it be nice if parallelism were a native feature of the language itself?

Mojo is a new language (in development) that attempts to do exactly that. Created by Chris Lattner (known for LLVM, Clang, Swift, and MLIR), Mojo is built with parallel programming as a first-class concern. It uses the MLIR infrastructure under the hood to enable portable, high-performance compilation to various targets (similar in spirit to what Triton does, but in the context of a full language). Mojo aims to unify concepts of CPU parallelism (threads, SIMD) and GPU programming in a single programming model. Some highlights of Mojo's design:
- It has built-in SIMD vector types and an API to explicitly vectorize code (for example, a vectorize function can apply a given operation in SIMD across a specified width).
- The type system differentiates between data in host memory and device (accelerator) memory, catching mistakes at compile time and easing portability.
- In general, many parallel and asynchronous constructs are part of the core language syntax, not ad-hoc add-ons.

To illustrate Mojo's approach, consider again the task of doubling each element in an array. In plain Python, you'd write a simple loop:
```py
def mul_py(data: list[int]):
    for i in range(len(data)):
        data[i] *= 2
```

If you run this in CPython, it's scalar and single-threaded (the interpreter will not use SIMD or multiple cores). Mojo, by contrast, can JIT compile a similar looking loop but auto-vectorize it and use compiler optimizations transparently. The Mojo version might look like:
```py
fn mul_mojo(mut data: List[Int32]):
    for item in data:
        item[] *= 2
```

In Mojo, `fn` declares a function, and the loop over `data` is auto-vectorized—`item[]` performs an explicit dereference. Unlike Python, this yields a deterministic ~15× speedup by guaranteeing SIMD execution without relying on pseudo-indeterministic compiler heuristics or manual intrinsics.

Mojo is still a work in progress (as of 2025, the GPU programming API is highly unstable and not publicly available yet). However, it's a promising direction. The plan is that you will be able to write portable GPU kernels in Mojo, and the compiler will handle mapping them to the hardware efficiently, just like it does for CPU SIMD. Mojo is an example of treating parallelism as a foundational feature of the programming model rather than an afterthought.

Another emerging project in this vein is Bend/HVM, a functional heterogeneous programming language.

## Resources

[0] Introduction to High Performance Scientific Computing – Victor Eijkhout

[1] <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

[2] <https://www.kapilsharma.dev/posts/deep-dive-into-triton-internals/>

[3] <https://docs.modular.com/mojo/manual/>
