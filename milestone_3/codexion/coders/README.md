This project has been created as part of the 42 curriculum by <your_login>.

Codexion — Master the race for resources before the deadline masters you
📌 Description

Codexion is a multithreaded simulation inspired by real-world concurrency problems in shared work environments.

Multiple coders sit in a circular co-working hub. Each coder must repeatedly compile, debug, and refactor.
However, compiling requires two USB dongles, and dongles are scarce shared resources with cooldown time. Coders compete to acquire their left and right dongles while avoiding burnout (failing to compile before their deadline).

The goal is to orchestrate:

POSIX threads (one per coder + one monitor)

Mutex-protected shared dongles

Condition variables for smart waiting

A mandatory scheduler (FIFO or EDF)

A separate monitor thread detecting burnout precisely

No starvation under feasible conditions

Full log serialization

No global variables (all shared state is contained in structures)

The simulation ends when:

A coder burns out (misses their compile deadline), or

All coders complete the required number of compiles.

Codexion is a high-precision resource-synchronization challenge comparable to the Dining Philosophers problem — but significantly more complex, with scheduling, cooldowns, and hard deadlines.

📌 Instructions
The Makefile provides the required rules:

-all
-$(NAME)
-clean
-fclean
-re

It compiles using:

cc -Wall -Wextra -Werror -pthread

Execution Example:

./codexion 5 800 200 200 200 3 50 fifo

📌 Blocking cases handled

This simulation must satisfy strong correctness guarantees.
Here are the blocking cases that were explicitly handled:

1. Deadlock prevention

Classic deadlock conditions (Coffman) are addressed:

Condition	Resolution
Mutual exclusion	Required by design; dongles are mutex-protected
Hold & wait	Coders request left and right dongles in scheduler order
No preemption	Not allowed, but resolved by correct ordering
Circular wait	Broken by consistent arbitration mechanism

FIFO and EDF scheduling ensures well-defined order and no circular dependency.

2. Starvation prevention

FIFO: guaranteed by strict queue order.

EDF: guaranteed by always serving earliest deadline; deadlines continuously increase after successful compiles; feasible systems never starve.

3. Cooldown handling

After a dongle is released:

A timestamp is set.

The dongle becomes unavailable for dongle_cooldown milliseconds.

Threads correctly block via condition variables until cooldown expires.

4. Race condition prevention

All access to:

Dongles

Shared simulation state

Compile counters

Deadline timestamps

Logging

is protected using mutexes.

5. Precise burnout detection

A dedicated monitor thread:

Continuously checks all coders' deadlines.

Logs burnout no later than 10 ms after it occurs.

Stops the simulation safely via a shared stop flag.

6. Log serialization

Every log message is printed under a single dedicated mutex, ensuring:

No interleaved messages

Strict chronological printing

📌 Thread synchronization mechanisms

Codexion uses POSIX primitives to safely coordinate threads:

1. pthread_mutex_t

Used to protect:

Each dongle (individual locks)

Shared state (compile counts, stop flag)

Logging (single print mutex)

Every shared variable is behind at least one mutex.

2. pthread_cond_t

Used to:

Block coders waiting for a dongle

Wake coders when a dongle finishes cooldown

Implement both FIFO and EDF queue dispatching

Notify waiting coders after dongle release

Waiting uses:

pthread_cond_wait

pthread_cond_timedwait for timeout-sensitive operations (e.g., EDF)

3. Custom event system

To make scheduling possible:

Each dongle maintains a request queue (min-heap or FIFO array)

EDF scheduling uses deadlines stored in the event structure

FIFO scheduling uses a monotonic request sequence ID

The mutex+cond combination forms a safe monitor pattern per dongle.

4. Monitor thread coordination

The monitor thread synchronizes with coders through:

A shared stop flag, mutex-protected

A condition broadcast to wake all coders when simulation ends

Timestamp checks via gettimeofday

5. Preventing race conditions

Examples:

Example: logging synchronization
pthread_mutex_lock(&sim->log_mutex);
printf("%ld %d is compiling\n", now_ms(), id);
pthread_mutex_unlock(&sim->log_mutex);

Example: dongle acquisition
pthread_mutex_lock(&dongle->mutex);
push_request(&dongle->queue, coder);
while (!can_access_dongle(dongle, coder))
    pthread_cond_wait(&dongle->cond, &dongle->mutex);
take_dongle(dongle, coder);
pthread_mutex_unlock(&dongle->mutex);

Example: burnout detection
pthread_mutex_lock(&sim->state_mutex);
if (now_ms() - coder->last_compile >= sim->time_to_burnout)
{
    log_burnout(coder->id);
    sim->stop = 1;
}
pthread_mutex_unlock(&sim->state_mutex);

📌 Resources
Documentation

POSIX Threads (pthreads):

pthread_create, pthread_join

pthread_mutex_*

pthread_cond_*

gettimeofday() usage and timing precision

Dining Philosophers problem (classic concurrency pattern)

Priority queues (binary heap implementation)

AI usage disclosure

AI tools (ChatGPT/GPT) were used only for:

Summarizing the project description

Generating boilerplate text for this README

Helping reason about concurrency patterns

Double-checking FIFO/EDF scheduling explanations

All final code, logic, debugging, data structures, and synchronization were written manually and fully understood before submission.