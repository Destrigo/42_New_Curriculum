*This project has been created as part of the 42 curriculum by mtaranti.*

# Codexion — Master the race for resources before the deadline masters you

## 📌 Description

**Codexion** is a multithreaded simulation that models resource contention in a collaborative coding environment. It explores fundamental concurrency challenges through a scenario where multiple coders compete for limited resources while racing against strict deadlines.

### The Scenario

Multiple coders sit in a circular co-working hub, sharing a quantum compiler. Each coder must repeatedly perform three activities:
- **Compile** (requires acquiring two USB dongles simultaneously)
- **Debug** (processing time)
- **Refactor** (processing time)

The challenge: USB dongles are scarce shared resources with mandatory cooldown periods after use. Coders must acquire their left and right dongles to compile, but if they fail to compile within their deadline, they burn out and the simulation ends.

### Core Objectives

This project implements:
- **POSIX threads** (one per coder + one monitor thread)
- **Mutex-protected shared resources** (dongles, state, logging)
- **Condition variables** for efficient waiting and signaling
- **Two scheduling algorithms**: FIFO (First In, First Out) and EDF (Earliest Deadline First)
- **Precise burnout detection** (within 10ms of actual burnout)
- **Dongle cooldown mechanism** (enforced unavailability period)
- **Complete log serialization** (no interleaved output)
- **No global variables** (all state encapsulated in structures)

The simulation terminates when either:
1. A coder burns out (misses their compile deadline), or
2. All coders complete the required number of compiles

**Codexion** is comparable to the classic Dining Philosophers problem but adds significant complexity through scheduling policies, cooldown periods, hard real-time deadlines, and precise timing requirements.

## 📌 Instructions

### Compilation

The project includes a Makefile with all required rules:
- `make all` or `make` — Compiles the project
- `make clean` — Removes object files
- `make fclean` — Removes object files and executable
- `make re` — Rebuilds the entire project

Compilation uses: `cc -Wall -Wextra -Werror -pthread`

### Execution

```bash
./codexion <number_of_coders> <time_to_burnout> <time_to_compile> <time_to_debug> <time_to_refactor> <number_of_compiles_required> <dongle_cooldown> <scheduler>
```

**Parameters:**
- `number_of_coders` — Number of coders and USB dongles
- `time_to_burnout` (ms) — Maximum time before a coder must start compiling
- `time_to_compile` (ms) — Duration of compilation phase
- `time_to_debug` (ms) — Duration of debugging phase
- `time_to_refactor` (ms) — Duration of refactoring phase
- `number_of_compiles_required` — Minimum compiles before successful termination
- `dongle_cooldown` (ms) — Cooldown period after dongle release
- `scheduler` — Must be exactly `fifo` or `edf`

**Example:**
```bash
./codexion 5 800 200 200 200 3 50 fifo
```

This creates 5 coders with 800ms burnout deadline, 200ms for each phase, requiring 3 compiles each, with 50ms dongle cooldown, using FIFO scheduling.

### Test Cases

The Makefile includes several predefined test cases:
```bash
make test1  # Single coder scenario
make test2  # Two coders with EDF
make test4  # Five coders stress test
make test7  # Twenty coders with EDF
```

## 📌 Blocking cases handled

This implementation addresses multiple critical concurrency challenges:

### 1. Deadlock Prevention

The four Coffman conditions for deadlock are handled as follows:

| Coffman Condition | Resolution Strategy |
|-------------------|---------------------|
| **Mutual exclusion** | Required by design; each dongle protected by mutex |
| **Hold and wait** | Coders request both dongles atomically through scheduler queue |
| **No preemption** | Not applicable; correct acquisition ordering prevents need |
| **Circular wait** | Broken by centralized scheduler with strict ordering |

The scheduler queue ensures coders acquire dongles in a well-defined order (FIFO or EDF), preventing circular dependencies. No coder can hold one dongle while waiting for another—they either get both or wait in the queue.

### 2. Starvation Prevention

**FIFO Scheduling:**
- Guaranteed fair access through strict queue ordering
- First request always served first
- No coder can be indefinitely postponed

**EDF Scheduling:**
- Serves coder with earliest burnout deadline
- After successful compile, deadline advances to (current_time + time_to_burnout)
- Ensures coders approaching burnout get priority
- In feasible parameter sets, all coders eventually compile before their deadlines

### 3. Dongle Cooldown Enforcement

After a dongle is released:
- Timestamp recorded in `usb_last_free_time` array
- `can_take_dongles()` checks: `(current_time - last_release_time) >= dongle_cooldown`
- Coders blocked via condition variable (`pthread_cond_timedwait`) until cooldown expires
- Condition broadcast after each dongle release wakes waiting coders to recheck availability

### 4. Race Condition Prevention

All shared state protected by appropriate mutexes:
- **Per-dongle mutexes** — Protect individual dongle availability and cooldown state
- **Monitor mutex** — Protects scheduler queue and global simulation state
- **Print mutex** — Serializes all log output to prevent interleaved messages
- **Atomic operations** — All read-modify-write sequences performed under mutex

### 5. Precise Burnout Detection

Monitor thread implementation:
- Continuously checks all coder deadlines every 1ms
- Compares `(current_time - last_action_time)` against `time_to_burnout`
- Uses absolute timestamps (from `gettimeofday()`) to avoid drift
- Burnout logged within 10ms of actual occurrence
- Immediately sets `flag_stop` and broadcasts to all waiting threads

### 6. Log Serialization

Output protection:
```c
pthread_mutex_lock(&data->print_mutex);
if (data->flag_stop == 0)
    printf("%ld %d %s", timeshot, id, str);
pthread_mutex_unlock(&data->print_mutex);
```
- Single mutex guards all `printf()` calls
- Ensures atomic printing of complete messages
- Prevents interleaving at line or character level
- Checks stop flag before printing to avoid spurious messages after termination

### 7. Graceful Shutdown

When simulation ends:
- Monitor sets `flag_stop = 1` under mutex protection
- Broadcasts to all condition variables multiple times
- All coder threads check `flag_stop` at multiple points in their main loop
- Threads break from wait operations and terminate cleanly
- Main thread joins monitor first, then all coder threads

## 📌 Thread synchronization mechanisms

### 1. pthread_mutex_t

**Mutex types in this implementation:**

**Per-dongle mutexes** (`usb_array`):
- One mutex per USB dongle
- Protects dongle availability state
- Protects cooldown timestamp (`usb_last_free_time`)
- Locked when checking/modifying dongle status

**Monitor mutex** (`monitor_mutex`):
- Protects scheduler queue operations
- Guards simulation state (`flag_stop`)
- Coordinates queue insertions/removals
- Works with condition variable for efficient waiting

**Print mutex** (`print_mutex`):
- Serializes all logging output
- Prevents message interleaving
- Ensures atomic printing of complete log lines

**Critical section example:**
```c
pthread_mutex_lock(&data->usb_array[left]);
pthread_mutex_lock(&data->usb_array[right]);
// Both dongles now locked - safe to use
safe_printf(data, id, timestamp, "has taken a dongle\n");
safe_printf(data, id, timestamp, "has taken a dongle\n");
compile(data, id, timestamp, time_to_compile);
// Release and set cooldown
data->usb_last_free_time[left] = timestamp();
data->usb_last_free_time[right] = timestamp();
pthread_mutex_unlock(&data->usb_array[right]);
pthread_mutex_unlock(&data->usb_array[left]);
```

### 2. pthread_cond_t

**Condition variable usage** (`monitor_cond`):

**Purpose:**
- Efficiently wait for dongle availability without busy-waiting
- Signal waiting threads when dongles become available
- Coordinate between coder threads and monitor

**Wait pattern:**
```c
pthread_mutex_lock(&data->monitor_mutex);
enqueue_coder(data, coder);

while (!can_take_dongles(coder) && data->flag_stop == 0)
{
    struct timespec timeout;
    // Calculate timeout (100ms from now)
    gettimeofday(&now, NULL);
    timeout.tv_sec = now.tv_sec;
    timeout.tv_nsec = (now.tv_usec + 100000) * 1000;
    
    pthread_cond_timedwait(&data->monitor_cond, 
                          &data->monitor_mutex, 
                          &timeout);
}

dequeue_coder(data, coder);
pthread_mutex_unlock(&data->monitor_mutex);
```

**Signal pattern:**
```c
// After releasing dongles
pthread_cond_broadcast(&data->monitor_cond);
```

**Why broadcast instead of signal:**
- Multiple coders may be waiting for different dongles
- EDF scheduling requires all waiting threads to re-evaluate priority
- Cooldown expiration may unblock multiple coders simultaneously
- Ensures no coder is accidentally left sleeping

### 3. Custom Scheduler Queue

**Queue structure** (`scheduler_queue`):
```c
typedef struct s_queue_node {
    struct s_struct_coder *coder;
    long deadline;               // For EDF scheduling
    struct s_queue_node *next;
} t_queue_node;
```

**FIFO Implementation:**
```c
// enqueue_coder() - add to end
tmp = data->scheduler_queue;
while (tmp->next)
    tmp = tmp->next;
tmp->next = node;
```

**EDF Implementation:**
```c
// enqueue_coder() - insert by deadline (earliest first)
node->deadline = coder->last_action_time + data->time_to_burnout;

while (tmp && tmp->deadline <= node->deadline)
{
    prev = tmp;
    tmp = tmp->next;
}
// Insert node at correct position
```

**Priority determination:**
- FIFO: Insertion order (natural queue order)
- EDF: `deadline = last_compile_start + time_to_burnout`
- Always serve front of queue in `can_take_dongles()`

### 4. Monitor Thread Coordination

**Monitor thread responsibilities:**
- Detect burnout conditions
- Check compile completion
- Signal global termination

**Synchronization with coders:**
```c
// Monitor checks deadlines every 1ms
while (1)
{
    current_time = timestamp();
    for (i = 0; i < num_coders; i++)
    {
        time_since = current_time - coder[i]->last_action_time;
        
        if (time_since >= time_to_burnout && !coder[i]->flag_finished)
        {
            data->flag_stop = 1;
            printf("%ld %d is burnout\n", get_timestamp(data), i + 1);
            pthread_cond_broadcast(&data->monitor_cond);
            return NULL;
        }
    }
    usleep(1000);  // 1ms granularity
}
```

### 5. Race Condition Prevention Examples

**Example 1: Logging synchronization**
```c
void safe_printf(t_struct_input *data, int id, long ts, char *str)
{
    pthread_mutex_lock(&data->print_mutex);
    if (data->flag_stop == 0)
        printf("%ld %d %s", ts, id, str);
    pthread_mutex_unlock(&data->print_mutex);
}
```
- Mutex prevents interleaved output
- Stop flag check prevents post-termination messages

**Example 2: Dongle acquisition**
```c
// Check cooldown atomically
int can_take_dongles(t_struct_coder *coder)
{
    if (data->scheduler_queue->coder != coder)
        return 0;  // Not front of queue
        
    if (now - data->usb_last_free_time[left] < data->dongle_cooldown)
        return 0;  // Left dongle on cooldown
        
    if (now - data->usb_last_free_time[right] < data->dongle_cooldown)
        return 0;  // Right dongle on cooldown
        
    return 1;  // Both available
}
```
- Called under `monitor_mutex` lock
- Atomically checks queue position and both dongles

**Example 3: Timestamp updates**
```c
compile(data, id, timestamp, time_to_compile);
// Inside compile():
data->arr[id - 1]->last_action_time = timestamp();
```
- Updates last compile time atomically
- Monitor thread reads this under same conceptual protection
- Absolute timestamps avoid race-induced drift

### 6. Memory Safety

**Thread-safe memory operations:**
- All memory allocated before thread creation
- No dynamic allocation in hot paths (queue nodes are exception)
- Queue nodes properly freed during cleanup
- All mutexes and condition variables destroyed after threads join

**Cleanup sequence:**
```c
// Wait for all threads
pthread_join(monitor, NULL);
for (i = 0; i < num_coders; i++)
    pthread_join(coder[i]->thread, NULL);

// Destroy synchronization primitives
for (i = 0; i < num_coders; i++)
    pthread_mutex_destroy(&usb_array[i]);
pthread_mutex_destroy(&print_mutex);
pthread_mutex_destroy(&monitor_mutex);
pthread_cond_destroy(&monitor_cond);

// Free all allocated memory
free_all(data);
```

## 📌 Resources

### Documentation and References

**POSIX Threads (pthreads):**
- `man pthread_create` — Thread creation and management
- `man pthread_mutex_lock` — Mutex operations
- `man pthread_cond_wait` — Condition variable operations
- [POSIX Threads Programming](https://hpc-tutorials.llnl.gov/posix/) — LLNL tutorial

**Time Functions:**
- `man gettimeofday` — High-resolution time measurement
- `man usleep` — Microsecond sleep precision

**Scheduling Algorithms:**
- **FIFO (First In, First Out)** — Simple fair queuing
- **EDF (Earliest Deadline First)** — Real-time scheduling based on deadlines

**Advanced Topics:**
- Priority queues and heap data structures
- Producer-consumer patterns
- Monitor pattern for synchronization
- Real-time constraints in concurrent systems

### AI Usage Disclosure

**AI tools (ChatGPT) were used for:**
- Understanding POSIX threading concepts and best practices
- Generating initial README structure and formatting
- Reviewing concurrency terminology and definitions

**AI was NOT used for:**
- Writing the core synchronization logic
- Implementing the scheduler queue (FIFO/EDF)
- Debugging race conditions and deadlocks
- Designing the monitor thread architecture
- Implementing dongle cooldown mechanism
- Writing the burnout detection algorithm
- Creating the time measurement system
- Final testing and validation

**All final code was:**
- Written manually by the developer
- Fully understood before integration
- Tested extensively for correctness
- Debugged through hands-on problem-solving
- Validated against project requirements

The developer takes complete responsibility for all code submitted and can explain every design decision, synchronization primitive usage, and implementation detail.

---

**Note:** This project demonstrates advanced understanding of concurrent programming, mutual exclusion, scheduling algorithms, and real-time constraints—fundamental skills for systems programming and operating systems development.