"""
Curated DSA Taxonomy — canonical patterns and their parent topics.
This is the core intellectual data of LeetLens.

Structure: list of (parent_topic, pattern_name, description)
"""
from typing import NamedTuple


class TaxonomyEntry(NamedTuple):
    parent: str          # parent topic slug
    pattern: str         # pattern display name
    description: str


TOPICS = [
    ("array", "Array", "Problems involving ordered sequences of elements"),
    ("string", "String", "Problems involving character sequences"),
    ("hash-table", "Hash Table", "Problems using hash maps and hash sets for O(1) lookups"),
    ("dynamic-programming", "Dynamic Programming", "Problems solved by breaking into overlapping subproblems"),
    ("math", "Math", "Problems requiring mathematical insight and number theory"),
    ("sorting", "Sorting", "Sort-based techniques, custom comparators, and order statistics"),
    ("greedy", "Greedy", "Problems solved by locally optimal choices at each stage"),
    ("depth-first-search", "Depth-First Search", "Exhaustive recursive and stack-based tree and graph traversal"),
    ("binary-search", "Binary Search", "Divide search space in half each step on sorted data or answer ranges"),
    ("matrix", "Matrix", "2D grid traversals, transformations, and coordinate algorithms"),
    ("tree", "Tree", "Hierarchical tree data structures and recursive processing"),
    ("breadth-first-search", "Breadth-First Search", "Queue-based level-order and shortest path graph traversals"),
    ("bit-manipulation", "Bit Manipulation", "Binary bit operations, masks, and bitwise tricks"),
    ("two-pointers", "Two Pointers", "Two index iteration converging inward or sliding in parallel"),
    ("prefix-sum", "Prefix Sum", "Cumulative precomputations for constant-time range sum queries"),
    ("heap", "Heap (Priority Queue)", "Min/max binary heaps for streaming extrema and Top-K queries"),
    ("binary-tree", "Binary Tree", "Binary tree structures, traversals, and divide-and-conquer"),
    ("simulation", "Simulation", "Direct step-by-step emulation of rules, machines, and states"),
    ("stack", "Stack", "LIFO data structures, monotonic stacks, and parentheses parsing"),
    ("graph", "Graph", "Vertices, edges, cycles, and connectivity algorithms"),
    ("sliding-window", "Sliding Window", "Subarray/substring window maintenance with two pointers"),
    ("design", "Design", "System and custom data structure architecture (LRU, LFU, Trie)"),
    ("enumeration", "Enumeration", "Exhaustive generation and validation of candidates"),
    ("backtracking", "Backtracking", "Constraint satisfaction via recursive trial and backtrack rollback"),
    ("union-find", "Union-Find", "Disjoint set union for dynamic connectivity"),
    ("linked-list", "Linked List", "Node-pointer data structures and pointer manipulation"),
    ("monotonic-stack", "Monotonic Stack", "Stack maintaining monotonic order for next greater/smaller queries"),
    ("ordered-set", "Ordered Set", "Self-balancing BST sets supporting range and rank queries"),
    ("recursion", "Recursion", "Self-referential function calls for divide-and-conquer"),
    ("divide-and-conquer", "Divide and Conquer", "Breaking problems into independent subproblems"),
    ("trie", "Trie", "Prefix tree data structures for string dictionary lookups"),
    ("queue", "Queue", "FIFO data structures, task scheduling, and buffering"),
    ("monotonic-queue", "Monotonic Queue", "Deque maintaining extrema for sliding window queries"),
    ("game-theory", "Game Theory", "Minimax and state determination in mathematical games"),
    ("quickselect", "Quickselect", "Linear time selection algorithm for k-th order statistics"),
    ("rolling-hash", "Rolling Hash", "Rabin-Karp polynomial rolling hash for pattern matching"),
    ("shortest-path", "Shortest Path", "Dijkstra, Bellman-Ford, and BFS shortest path algorithms"),
    ("data-stream", "Data Stream", "Online algorithms processing sequential continuous inputs"),
    ("randomized", "Randomized", "Algorithms utilizing pseudo-random number generation"),
    ("combinatorics", "Combinatorics", "Counting, permutations, combinations, and permutations"),
]

TAXONOMY: list[TaxonomyEntry] = [
    # ARRAY
    TaxonomyEntry("array", "Two Pointers", "Use two indices to scan/converge from different positions"),
    TaxonomyEntry("array", "Sliding Window", "Maintain a window over a subarray/substring"),
    TaxonomyEntry("array", "Prefix Sum", "Precompute cumulative sums for range queries"),
    TaxonomyEntry("array", "Difference Array", "Use differences for range update queries"),
    TaxonomyEntry("array", "Kadane's Algorithm", "Maximum subarray sum via dynamic programming"),
    TaxonomyEntry("array", "Intervals", "Merge, insert, or query overlapping intervals"),
    TaxonomyEntry("array", "Binary Search", "Divide search space in half each step"),
    TaxonomyEntry("array", "Sorting", "Sort-based problem solving approaches"),
    TaxonomyEntry("array", "Monotonic Array", "Exploit monotonically increasing/decreasing properties"),

    # STRING
    TaxonomyEntry("string", "String Sliding Window", "Sliding window applied to substrings"),
    TaxonomyEntry("string", "String Two Pointers", "Two pointers on character arrays"),
    TaxonomyEntry("string", "Frequency Counting", "Count character/element frequencies"),
    TaxonomyEntry("string", "String Matching", "Pattern matching algorithms (KMP, Rabin-Karp)"),
    TaxonomyEntry("string", "Palindrome Patterns", "Exploit palindrome properties"),

    # HASH TABLE / HASHING
    TaxonomyEntry("hash-table", "Frequency Map", "Map elements to their counts"),
    TaxonomyEntry("hash-table", "Set Lookup", "Use sets for O(1) membership queries"),
    TaxonomyEntry("hash-table", "Prefix-State Hashing", "Hash prefix states for subarray/substring problems"),
    TaxonomyEntry("hash-table", "Grouping", "Group elements by computed key"),

    # LINKED LIST
    TaxonomyEntry("linked-list", "Fast/Slow Pointers", "Two pointers moving at different speeds"),
    TaxonomyEntry("linked-list", "List Reversal", "Reverse a linked list or portion of it"),
    TaxonomyEntry("linked-list", "Cycle Detection", "Detect cycles using Floyd's algorithm"),
    TaxonomyEntry("linked-list", "List Merge", "Merge sorted linked lists"),
    TaxonomyEntry("linked-list", "List Intersection", "Find where two lists intersect"),

    # STACK
    TaxonomyEntry("stack", "Monotonic Stack", "Stack maintaining monotonic order for next/prev greater/smaller"),
    TaxonomyEntry("stack", "Parentheses", "Balance and validate bracket sequences"),
    TaxonomyEntry("stack", "Expression Parsing", "Evaluate or parse arithmetic expressions"),
    TaxonomyEntry("stack", "Next Greater Element", "Find next larger element for each position"),

    # TREE
    TaxonomyEntry("tree", "Tree DFS", "Depth-first traversal of trees"),
    TaxonomyEntry("tree", "Tree BFS", "Level-order (breadth-first) traversal of trees"),
    TaxonomyEntry("tree", "Tree Traversal", "In/pre/post-order traversal strategies"),
    TaxonomyEntry("tree", "BST", "Binary Search Tree properties and operations"),
    TaxonomyEntry("tree", "LCA", "Lowest Common Ancestor algorithms"),
    TaxonomyEntry("tree", "Tree DP", "Dynamic programming on trees"),
    TaxonomyEntry("tree", "Tree Serialization", "Serialize/deserialize tree structures"),

    # GRAPH
    TaxonomyEntry("graph", "Graph BFS", "Breadth-first search on graphs"),
    TaxonomyEntry("graph", "Graph DFS", "Depth-first search on graphs"),
    TaxonomyEntry("graph", "Topological Sort", "Order nodes respecting directed dependencies"),
    TaxonomyEntry("graph", "Union Find", "Disjoint set union for connectivity"),
    TaxonomyEntry("graph", "Dijkstra", "Shortest path in weighted graphs"),
    TaxonomyEntry("graph", "Bellman-Ford", "Shortest path handling negative weights"),
    TaxonomyEntry("graph", "Floyd-Warshall", "All-pairs shortest paths"),
    TaxonomyEntry("graph", "MST", "Minimum Spanning Tree (Prim's/Kruskal's)"),

    # DYNAMIC PROGRAMMING
    TaxonomyEntry("dynamic-programming", "1D DP", "One-dimensional dynamic programming"),
    TaxonomyEntry("dynamic-programming", "2D DP", "Two-dimensional dynamic programming"),
    TaxonomyEntry("dynamic-programming", "Knapsack", "0/1 and unbounded knapsack variants"),
    TaxonomyEntry("dynamic-programming", "Subsequence DP", "Longest common/increasing subsequence"),
    TaxonomyEntry("dynamic-programming", "Grid DP", "DP on 2D grids"),
    TaxonomyEntry("dynamic-programming", "Interval DP", "DP on intervals (matrix chain, balloon burst)"),
    TaxonomyEntry("dynamic-programming", "State Machine DP", "DP with finite state machines"),
    TaxonomyEntry("dynamic-programming", "Bitmask DP", "DP with bitmask state representation"),

    # GREEDY
    TaxonomyEntry("greedy", "Interval Greedy", "Greedy interval scheduling/assignment"),
    TaxonomyEntry("greedy", "Sorting + Greedy", "Sort then apply greedy logic"),
    TaxonomyEntry("greedy", "Local Choice", "Make locally optimal choice at each step"),

    # BACKTRACKING
    TaxonomyEntry("backtracking", "Subsets", "Generate all subsets"),
    TaxonomyEntry("backtracking", "Permutations", "Generate all permutations"),
    TaxonomyEntry("backtracking", "Combinations", "Generate combinations with/without repetition"),
    TaxonomyEntry("backtracking", "Constraint Search", "Backtracking with constraint propagation"),

    # HEAP
    TaxonomyEntry("heap", "Top-K", "Find top K elements using a heap"),
    TaxonomyEntry("heap", "K-Way Merge", "Merge K sorted sequences"),
    TaxonomyEntry("heap", "Two Heaps", "Use min+max heaps for median or partition"),
    TaxonomyEntry("heap", "Scheduling", "Task/event scheduling with priority queues"),

    # TRIE
    TaxonomyEntry("trie", "Prefix Search", "Insert/search strings in a trie"),
    TaxonomyEntry("trie", "Word Search", "Word grid search using trie"),
    TaxonomyEntry("trie", "Bitwise Trie", "Trie on bit representations for XOR/max"),

    # BIT MANIPULATION
    TaxonomyEntry("bit-manipulation", "XOR", "XOR tricks for parity/uniqueness"),
    TaxonomyEntry("bit-manipulation", "Bit Counting", "Count set bits"),
    TaxonomyEntry("bit-manipulation", "Bitmask", "Bitmask operations for subset enumeration"),
    TaxonomyEntry("bit-manipulation", "State Compression", "Compress state into bitmasks for DP"),

    # MATH
    TaxonomyEntry("math", "Number Theory", "GCD, LCM, primes, modular arithmetic"),
    TaxonomyEntry("math", "Combinatorics", "Counting, permutations, combinations"),

    # DESIGN
    TaxonomyEntry("design", "Data Structure Design", "Design custom data structures (LRU, LFU, etc.)"),

    # MATRIX
    TaxonomyEntry("matrix", "Matrix Traversal", "Row, column, and spiral traversal across 2D grids"),
    TaxonomyEntry("matrix", "In-Place Matrix Transformation", "Matrix rotation, reflection, and state markers"),
    TaxonomyEntry("matrix", "2D Grid Search", "BFS/DFS exploration of grid cells and connected components"),

    # SIMULATION
    TaxonomyEntry("simulation", "Direct State Simulation", "Step-by-step game, clock, and machine simulation"),
    TaxonomyEntry("simulation", "Rule-Based Grid Walking", "Simulation of moving entities or state automata"),

    # SORTING
    TaxonomyEntry("sorting", "Custom Comparator Sorting", "Custom ordering, multi-key sort, and coordinate compression"),
    TaxonomyEntry("sorting", "In-Place & Bucket Sort", "Dutch national flag, count sort, and cyclic sort"),

    # BINARY TREE
    TaxonomyEntry("binary-tree", "Tree DFS Traversal", "Preorder, Inorder, and Postorder recursive traversal"),
    TaxonomyEntry("binary-tree", "Tree Level-Order BFS", "Level-by-level queue traversal and views"),
    TaxonomyEntry("binary-tree", "Binary Tree Properties", "Diameter, height balance, and symmetry checks"),

    # TWO POINTERS
    TaxonomyEntry("two-pointers", "Opposite-Direction Two Pointers", "Left/right pointers converging inward"),
    TaxonomyEntry("two-pointers", "Same-Direction Fast & Slow", "Sliding read/write pointers and duplicate removal"),

    # SLIDING WINDOW
    TaxonomyEntry("sliding-window", "Fixed-Size Sliding Window", "Maintain metrics across a fixed subarray length"),
    TaxonomyEntry("sliding-window", "Variable-Size Sliding Window", "Expand right and contract left to satisfy constraints"),

    # BINARY SEARCH
    TaxonomyEntry("binary-search", "Direct Binary Search", "Search on sorted arrays or rotated segments"),
    TaxonomyEntry("binary-search", "Binary Search on Answer Range", "Monotonic predicate search on result space"),

    # RECURSION
    TaxonomyEntry("recursion", "Divide & Subproblem Recursion", "Break problem into self-similar sub-computations"),
    TaxonomyEntry("recursion", "Backtracking Recursion", "State exploration with explicit backtrack rollback"),

    # DIVIDE AND CONQUER
    TaxonomyEntry("divide-and-conquer", "Binary Divide & Conquer", "Divide input in half, conquer subproblems, combine"),
    TaxonomyEntry("divide-and-conquer", "Expression & Tree Partition", "Evaluate all split points recursively"),

    # DEPTH FIRST SEARCH
    TaxonomyEntry("depth-first-search", "Graph & Tree DFS", "Exhaustive depth-first path exploration"),
    TaxonomyEntry("depth-first-search", "Backtracking DFS", "State space search with pruning"),

    # BREADTH FIRST SEARCH
    TaxonomyEntry("breadth-first-search", "Shortest Path BFS", "Unweighted shortest distance and layer-by-layer exploration"),
    TaxonomyEntry("breadth-first-search", "Multi-Source BFS", "Simultaneous propagation from multiple start points"),

    # UNION FIND
    TaxonomyEntry("union-find", "Disjoint Set Connectivity", "Path compression and union by rank for graph components"),
    TaxonomyEntry("union-find", "Dynamic Equivalence", "Component tracking and cycle detection"),

    # MONOTONIC STACK
    TaxonomyEntry("monotonic-stack", "Next Greater Element", "Find next/previous greater or smaller elements in linear time"),
    TaxonomyEntry("monotonic-stack", "Histogram Area Optimization", "Span-based rectangle optimization"),

    # MONOTONIC QUEUE
    TaxonomyEntry("monotonic-queue", "Sliding Window Extrema", "Monotonic deque to query window max/min in O(1)"),

    # QUICKSELECT
    TaxonomyEntry("quickselect", "K-th Order Statistic", "Hoare partition selection in O(N) average time"),

    # GAME THEORY
    TaxonomyEntry("game-theory", "Minimax & Nim Game", "Optimal play, stone removal, and parity game states"),

    # ENUMERATION
    TaxonomyEntry("enumeration", "Exhaustive State Enumeration", "Check all combinations, ranges, or bit states"),

    # ROLLING HASH
    TaxonomyEntry("rolling-hash", "Rabin-Karp String Hashing", "O(1) polynomial hash rolling for substring match"),

    # ORDERED SET
    TaxonomyEntry("ordered-set", "Balanced BST & MultiSet", "Rank, range, and floor/ceiling lookups in O(log N)"),

    # SHORTEST PATH
    TaxonomyEntry("shortest-path", "Dijkstra & Weighted Paths", "Priority queue shortest path in weighted directed graphs"),

    # DATA STREAM
    TaxonomyEntry("data-stream", "Online Stream Processing", "Process elements sequentially with bounded memory"),

    # RANDOMIZED
    TaxonomyEntry("randomized", "Reservoir Sampling & Shuffle", "Uniform random selection and Fisher-Yates shuffle"),
]


# Problem → Pattern mappings (curated, verified)
# (leetcode_id, pattern_name, confidence)
PROBLEM_PATTERNS: list[tuple[int, str, float]] = [
    # Two Sum (#1)
    (1, "Frequency Map", 1.0),
    (1, "Set Lookup", 1.0),
    # Add Two Numbers (#2)
    (2, "List Merge", 0.9),
    # Longest Substring Without Repeating Characters (#3)
    (3, "Sliding Window", 1.0),
    (3, "Frequency Map", 1.0),
    (3, "Set Lookup", 0.9),
    # Median of Two Sorted Arrays (#4)
    (4, "Binary Search", 1.0),
    # Longest Palindromic Substring (#5)
    (5, "Palindrome Patterns", 1.0),
    (5, "2D DP", 0.9),
    # Zigzag Conversion (#6)
    (6, "Sorting", 0.6),
    # Reverse Integer (#7)
    (7, "Number Theory", 0.8),
    # String to Integer (atoi) (#8)
    (8, "String Two Pointers", 0.7),
    # Palindrome Number (#9)
    (9, "Palindrome Patterns", 1.0),
    # Regular Expression Matching (#10)
    (10, "2D DP", 1.0),
    # Container With Most Water (#11)
    (11, "Two Pointers", 1.0),
    # Integer to Roman (#12)
    (12, "Greedy", 0.8),
    # Roman to Integer (#13)
    (13, "Frequency Map", 0.8),
    # Longest Common Prefix (#14)
    (14, "String Matching", 0.9),
    # 3Sum (#15)
    (15, "Two Pointers", 1.0),
    (15, "Sorting", 1.0),
    # 3Sum Closest (#16)
    (16, "Two Pointers", 1.0),
    (16, "Sorting", 1.0),
    # Letter Combinations of a Phone Number (#17)
    (17, "Backtracking", 1.0),
    # 4Sum (#18)
    (18, "Two Pointers", 1.0),
    (18, "Sorting", 1.0),
    # Remove Nth Node From End of List (#19)
    (19, "Fast/Slow Pointers", 1.0),
    # Valid Parentheses (#20)
    (20, "Parentheses", 1.0),
    # Merge Two Sorted Lists (#21)
    (21, "List Merge", 1.0),
    # Generate Parentheses (#22)
    (22, "Backtracking", 1.0),
    # Merge K Sorted Lists (#23)
    (23, "K-Way Merge", 1.0),
    (23, "Top-K", 0.8),
    # Swap Nodes in Pairs (#24)
    (24, "List Reversal", 0.9),
    # Reverse Nodes in k-Group (#25)
    (25, "List Reversal", 1.0),
    # Remove Duplicates from Sorted Array (#26)
    (26, "Two Pointers", 1.0),
    # Remove Element (#27)
    (27, "Two Pointers", 1.0),
    # Find the Index of the First Occurrence (#28)
    (28, "String Matching", 1.0),
    # Search Insert Position (#35)
    (35, "Binary Search", 1.0),
    # Maximum Subarray (#53)
    (53, "Kadane's Algorithm", 1.0),
    (53, "1D DP", 0.9),
    # Jump Game (#55)
    (55, "Greedy", 1.0),
    (55, "1D DP", 0.8),
    # Merge Intervals (#56)
    (56, "Intervals", 1.0),
    (56, "Sorting", 1.0),
    # Insert Interval (#57)
    (57, "Intervals", 1.0),
    # Length of Last Word (#58)
    (58, "String Two Pointers", 0.8),
    # Plus One (#66)
    (66, "Number Theory", 0.7),
    # Sqrt(x) (#69)
    (69, "Binary Search", 1.0),
    # Climbing Stairs (#70)
    (70, "1D DP", 1.0),
    # Binary Tree Inorder Traversal (#94)
    (94, "Tree Traversal", 1.0),
    (94, "Tree DFS", 1.0),
    # Same Tree (#100)
    (100, "Tree DFS", 1.0),
    # Symmetric Tree (#101)
    (101, "Tree DFS", 1.0),
    (101, "Tree BFS", 0.9),
    # Binary Tree Level Order Traversal (#102)
    (102, "Tree BFS", 1.0),
    # Maximum Depth of Binary Tree (#104)
    (104, "Tree DFS", 1.0),
    (104, "Tree BFS", 0.9),
    # Construct Binary Tree from Preorder and Inorder (#105)
    (105, "Tree DFS", 1.0),
    # Binary Tree Zigzag Level Order Traversal (#103)
    (103, "Tree BFS", 1.0),
    # Best Time to Buy and Sell Stock (#121)
    (121, "Sliding Window", 0.9),
    (121, "Kadane's Algorithm", 0.8),
    # Valid Palindrome (#125)
    (125, "Two Pointers", 1.0),
    (125, "Palindrome Patterns", 1.0),
    # Word Ladder (#127)
    (127, "Graph BFS", 1.0),
    # Longest Consecutive Sequence (#128)
    (128, "Set Lookup", 1.0),
    (128, "Union Find", 0.7),
    # Word Search (#79)
    (79, "Backtracking", 1.0),
    (79, "Graph DFS", 0.9),
    # Subsets (#78)
    (78, "Backtracking", 1.0),
    (78, "Subsets", 1.0),
    # Binary Tree Maximum Path Sum (#124)
    (124, "Tree DFS", 1.0),
    (124, "Tree DP", 1.0),
    # Copy List with Random Pointer (#138)
    (138, "Frequency Map", 0.8),
    # Reorder List (#143)
    (143, "Fast/Slow Pointers", 1.0),
    (143, "List Reversal", 1.0),
    # LRU Cache (#146)
    (146, "Data Structure Design", 1.0),
    (146, "Frequency Map", 0.8),
    # Number of Islands (#200)
    (200, "Graph DFS", 1.0),
    (200, "Graph BFS", 0.9),
    (200, "Union Find", 0.8),
    # Reverse Linked List (#206)
    (206, "List Reversal", 1.0),
    # Course Schedule (#207)
    (207, "Topological Sort", 1.0),
    (207, "Graph DFS", 0.9),
    # Implement Trie (#208)
    (208, "Prefix Search", 1.0),
    # Minimum Size Subarray Sum (#209)
    (209, "Sliding Window", 1.0),
    (209, "Two Pointers", 0.9),
    (209, "Prefix Sum", 0.7),
    # Course Schedule II (#210)
    (210, "Topological Sort", 1.0),
    # Find Peak Element (#162)
    (162, "Binary Search", 1.0),
    # Rotate Array (#189)
    (189, "Two Pointers", 0.9),
    # Contains Duplicate (#217)
    (217, "Set Lookup", 1.0),
    # Product of Array Except Self (#238)
    (238, "Prefix Sum", 1.0),
    # Majority Element (#169)
    (169, "Frequency Map", 1.0),
    # Search a 2D Matrix (#74)
    (74, "Binary Search", 1.0),
    # Find Minimum in Rotated Sorted Array (#153)
    (153, "Binary Search", 1.0),
    # Search in Rotated Sorted Array (#33)
    (33, "Binary Search", 1.0),
    # Kth Largest Element in an Array (#215)
    (215, "Top-K", 1.0),
    (215, "Sorting", 0.8),
    # Maximum Product Subarray (#152)
    (152, "Kadane's Algorithm", 1.0),
    (152, "1D DP", 0.8),
    # Min Stack (#155)
    (155, "Stack", 1.0),
    (155, "Data Structure Design", 0.9),
    # Find All Anagrams in a String (#438)
    (438, "Sliding Window", 1.0),
    (438, "Frequency Map", 1.0),
    # Minimum Window Substring (#76)
    (76, "Sliding Window", 1.0),
    (76, "Two Pointers", 0.9),
    (76, "Frequency Map", 0.9),
    # Trapping Rain Water (#42)
    (42, "Two Pointers", 1.0),
    (42, "Monotonic Stack", 0.9),
    (42, "Prefix Sum", 0.8),
    # Jump Game II (#45)
    (45, "Greedy", 1.0),
    # Unique Paths (#62)
    (62, "Grid DP", 1.0),
    (62, "Combinatorics", 0.8),
    # Coin Change (#322)
    (322, "1D DP", 1.0),
    (322, "Knapsack", 0.9),
    # Longest Increasing Subsequence (#300)
    (300, "Subsequence DP", 1.0),
    (300, "Binary Search", 0.8),
    # Word Break (#139)
    (139, "1D DP", 1.0),
    (139, "Set Lookup", 0.8),
    # Decode Ways (#91)
    (91, "1D DP", 1.0),
    # House Robber (#198)
    (198, "1D DP", 1.0),
    # House Robber II (#213)
    (213, "1D DP", 1.0),
    # Combination Sum (#39)
    (39, "Backtracking", 1.0),
    (39, "Combinations", 1.0),
    # Permutations (#46)
    (46, "Backtracking", 1.0),
    (46, "Permutations", 1.0),
    # Subsets II (#90)
    (90, "Backtracking", 1.0),
    (90, "Subsets", 1.0),
    # N-Queens (#51)
    (51, "Backtracking", 1.0),
    (51, "Constraint Search", 1.0),
    # Valid Sudoku (#36)
    (36, "Frequency Map", 1.0),
    (36, "Set Lookup", 0.9),
    # Diameter of Binary Tree (#543)
    (543, "Tree DFS", 1.0),
    # Balanced Binary Tree (#110)
    (110, "Tree DFS", 1.0),
    # Path Sum (#112)
    (112, "Tree DFS", 1.0),
    # Binary Tree Right Side View (#199)
    (199, "Tree BFS", 1.0),
    (199, "Tree DFS", 0.8),
    # Lowest Common Ancestor (#236)
    (236, "LCA", 1.0),
    (236, "Tree DFS", 0.9),
    # Validate Binary Search Tree (#98)
    (98, "BST", 1.0),
    (98, "Tree DFS", 0.9),
    # Kth Smallest in BST (#230)
    (230, "BST", 1.0),
    (230, "Tree DFS", 0.9),
    # Serialize/Deserialize Binary Tree (#297)
    (297, "Tree Serialization", 1.0),
    (297, "Tree BFS", 0.9),
    # Median from Data Stream (#295)
    (295, "Two Heaps", 1.0),
    # Find Median from Data Stream (#295) already above
    # Top K Frequent Elements (#347)
    (347, "Top-K", 1.0),
    (347, "Frequency Map", 1.0),
    # Meeting Rooms II (#253) — not free but important
    # Daily Temperatures (#739)
    (739, "Monotonic Stack", 1.0),
    (739, "Next Greater Element", 1.0),
    # Next Greater Element I (#496)
    (496, "Monotonic Stack", 1.0),
    (496, "Next Greater Element", 1.0),
    # Largest Rectangle in Histogram (#84)
    (84, "Monotonic Stack", 1.0),
    # Gas Station (#134)
    (134, "Greedy", 1.0),
    # Task Scheduler (#621)
    (621, "Frequency Map", 1.0),
    (621, "Greedy", 0.9),
    (621, "Scheduling", 0.8),
    # Alien Dictionary (#269) — not free
    # Pacific Atlantic Water Flow (#417)
    (417, "Graph DFS", 1.0),
    (417, "Graph BFS", 0.9),
    # Clone Graph (#133)
    (133, "Graph DFS", 1.0),
    (133, "Graph BFS", 0.9),
    # Rotting Oranges (#994)
    (994, "Graph BFS", 1.0),
    # Walls and Gates (#286) — not free
    # Network Delay Time (#743)
    (743, "Dijkstra", 1.0),
    # Cheapest Flights Within K Stops (#787)
    (787, "Bellman-Ford", 1.0),
    (787, "Dijkstra", 0.8),
    # Redundant Connection (#684)
    (684, "Union Find", 1.0),
    # Graph Valid Tree (#261) — not free
    # Number of Connected Components (#323) — not free
    # Edit Distance (#72)
    (72, "2D DP", 1.0),
    (72, "Subsequence DP", 0.9),
    # Longest Common Subsequence (#1143)
    (1143, "Subsequence DP", 1.0),
    (1143, "2D DP", 1.0),
    # Regular Expression Matching — already above
    # Burst Balloons (#312)
    (312, "Interval DP", 1.0),
    # Partition Equal Subset Sum (#416)
    (416, "Knapsack", 1.0),
    (416, "1D DP", 0.9),
    # Target Sum (#494)
    (494, "Knapsack", 1.0),
    (494, "1D DP", 0.9),
    # Counting Bits (#338)
    (338, "Bit Counting", 1.0),
    (338, "1D DP", 0.8),
    # Number of 1 Bits (#191)
    (191, "Bit Counting", 1.0),
    # Reverse Bits (#190)
    (190, "Bit Manipulation", 1.0),
    # Missing Number (#268)
    (268, "XOR", 1.0),
    (268, "Bit Manipulation", 0.9),
    # Single Number (#136)
    (136, "XOR", 1.0),
    # Single Number II (#137)
    (137, "Bit Counting", 1.0),
    (137, "State Compression", 0.8),
    # Sum of Two Integers (#371)
    (371, "Bit Manipulation", 1.0),
    # Palindrome Partitioning (#131)
    (131, "Backtracking", 1.0),
    (131, "Palindrome Patterns", 0.9),
    # Letter Case Permutation (#784)
    (784, "Backtracking", 1.0),
    # Implement Queue using Stacks (#232)
    (232, "Data Structure Design", 1.0),
    (232, "Stack", 0.9),
    # Implement Stack using Queues (#225)
    (225, "Data Structure Design", 1.0),
    # Design HashMap (#706)
    (706, "Data Structure Design", 1.0),
    (706, "Frequency Map", 0.7),
    # Range Sum Query (#303)
    (303, "Prefix Sum", 1.0),
    # Range Sum Query 2D (#304)
    (304, "Prefix Sum", 1.0),
    # Subarray Sum Equals K (#560)
    (560, "Prefix-State Hashing", 1.0),
    (560, "Prefix Sum", 1.0),
    # Contiguous Array (#525)
    (525, "Prefix-State Hashing", 1.0),
    # Longest Subarray with Sum K (using hash)
    # Find Pivot Index (#724)
    (724, "Prefix Sum", 1.0),
    # Running Sum of 1D Array (#1480)
    (1480, "Prefix Sum", 1.0),
    # Two Sum II (#167)
    (167, "Two Pointers", 1.0),
    (167, "Binary Search", 0.8),
    # Valid Mountain Array (#941)
    (941, "Two Pointers", 0.9),
    # Move Zeroes (#283)
    (283, "Two Pointers", 1.0),
    # Squares of a Sorted Array (#977)
    (977, "Two Pointers", 1.0),
    # Longest Repeating Character Replacement (#424)
    (424, "Sliding Window", 1.0),
    (424, "Frequency Map", 0.9),
    # Permutation in String (#567)
    (567, "Sliding Window", 1.0),
    (567, "Frequency Map", 1.0),
    # Word Search II (#212)
    (212, "Backtracking", 1.0),
    (212, "Word Search", 1.0),
    # Implement Trie (Prefix Tree) II (#1804) (same as 208)
    # Add and Search Word (#211)
    (211, "Prefix Search", 1.0),
    (211, "Backtracking", 0.8),
    # Design Add and Search Words Data Structure — same as 211
    # Max Area of Island (#695)
    (695, "Graph DFS", 1.0),
    (695, "Graph BFS", 0.8),
    # Surrounded Regions (#130)
    (130, "Graph DFS", 1.0),
    (130, "Union Find", 0.8),
    # Is Graph Bipartite (#785)
    (785, "Graph BFS", 1.0),
    (785, "Graph DFS", 0.9),
    # Find the Town Judge (#997)
    (997, "Graph DFS", 0.7),
    # Course Schedule III (#630)
    (630, "Greedy", 1.0),
    (630, "Scheduling", 0.9),
    # Non-overlapping Intervals (#435)
    (435, "Interval Greedy", 1.0),
    (435, "Sorting", 1.0),
    # Meeting Rooms (#252) — not free but common
    # Minimum Number of Arrows (#452)
    (452, "Interval Greedy", 1.0),
    (452, "Sorting", 1.0),
    # Insert Delete GetRandom O(1) (#380)
    (380, "Data Structure Design", 1.0),
    (380, "Frequency Map", 0.8),
    # LFU Cache (#460)
    (460, "Data Structure Design", 1.0),
    # Kth Largest Element in a Stream (#703)
    (703, "Top-K", 1.0),
    # Find K Closest Elements (#658)
    (658, "Binary Search", 0.9),
    (658, "Two Pointers", 0.8),
    # Ugly Number II (#264)
    (264, "K-Way Merge", 0.9),
    (264, "1D DP", 0.8),
    # Reverse Words in a String (#151)
    (151, "Two Pointers", 0.9),
    (151, "String Two Pointers", 0.9),
    # Spiral Matrix (#54)
    (54, "Two Pointers", 0.8),
    # Rotate Image (#48)
    (48, "Two Pointers", 0.8),
    # Set Matrix Zeroes (#73)
    (73, "Frequency Map", 0.7),
    # Pascal's Triangle (#118)
    (118, "2D DP", 0.8),
    (118, "Combinatorics", 0.9),
    # Pascal's Triangle II (#119)
    (119, "1D DP", 0.8),
    (119, "Combinatorics", 0.9),
    # Best Time to Buy and Sell Stock II (#122)
    (122, "Greedy", 1.0),
    # Best Time to Buy and Sell Stock III (#123)
    (123, "State Machine DP", 1.0),
    # Best Time to Buy and Sell Stock IV (#188)
    (188, "State Machine DP", 1.0),
    # Best Time to Buy and Sell Stock with Cooldown (#309)
    (309, "State Machine DP", 1.0),
    # Minimum Path Sum (#64)
    (64, "Grid DP", 1.0),
    # Dungeon Game (#174)
    (174, "Grid DP", 1.0),
    # Triangle (#120)
    (120, "1D DP", 1.0),
    # Maximal Square (#221)
    (221, "2D DP", 1.0),
    # Maximal Rectangle (#85)
    (85, "Monotonic Stack", 1.0),
    (85, "2D DP", 0.8),
    # Stone Game (#877)
    (877, "Interval DP", 1.0),
    # Strange Printer (#664)
    (664, "Interval DP", 1.0),
    # Distinct Subsequences (#115)
    (115, "Subsequence DP", 1.0),
    (115, "2D DP", 1.0),
    # Interleaving String (#97)
    (97, "2D DP", 1.0),
    # Number of Digit One (#233)
    (233, "Number Theory", 1.0),
    # Count Primes (#204)
    (204, "Number Theory", 1.0),
    # Power(x, n) (#50)
    (50, "Number Theory", 1.0),
    (50, "Binary Search", 0.7),
    # Happy Number (#202)
    (202, "Cycle Detection", 0.9),
    (202, "Set Lookup", 0.8),
    # Linked List Cycle (#141)
    (141, "Fast/Slow Pointers", 1.0),
    (141, "Cycle Detection", 1.0),
    # Linked List Cycle II (#142)
    (142, "Fast/Slow Pointers", 1.0),
    (142, "Cycle Detection", 1.0),
    # Middle of the Linked List (#876)
    (876, "Fast/Slow Pointers", 1.0),
    # Palindrome Linked List (#234)
    (234, "Fast/Slow Pointers", 1.0),
    (234, "List Reversal", 0.9),
    # Odd Even Linked List (#328)
    (328, "List Reversal", 0.8),
    # Flatten a Multilevel Doubly Linked List (#430)
    (430, "Tree DFS", 0.8),
    # Sort List (#148)
    (148, "Fast/Slow Pointers", 0.9),
    (148, "K-Way Merge", 0.7),
    # Find Duplicate Number (#287)
    (287, "Fast/Slow Pointers", 1.0),
    (287, "Cycle Detection", 1.0),
    # First Bad Version (#278)
    (278, "Binary Search", 1.0),
    # Guess Number Higher or Lower (#374)
    (374, "Binary Search", 1.0),
    # Count Complete Tree Nodes (#222)
    (222, "Binary Search", 0.9),
    (222, "Tree BFS", 0.8),
    # Inorder Successor in BST (#285) — not free
    # Kth Smallest in BST (#230) already above
    # Convert Sorted Array to BST (#108)
    (108, "BST", 1.0),
    (108, "Binary Search", 0.8),
    # Recover Binary Search Tree (#99)
    (99, "BST", 1.0),
    (99, "Tree DFS", 0.9),
    # Sum Root to Leaf Numbers (#129)
    (129, "Tree DFS", 1.0),
    # Path Sum II (#113)
    (113, "Tree DFS", 1.0),
    (113, "Backtracking", 0.8),
    # Flatten Binary Tree to Linked List (#114)
    (114, "Tree DFS", 1.0),
    # Populating Next Right Pointers (#116)
    (116, "Tree BFS", 1.0),
    # Populating Next Right Pointers II (#117)
    (117, "Tree BFS", 1.0),
    # Maximum Width of Binary Tree (#662)
    (662, "Tree BFS", 1.0),
    # Vertical Order Traversal (#987)
    (987, "Tree BFS", 1.0),
    (987, "Sorting", 0.8),
    # Check Completeness of a Binary Tree (#958)
    (958, "Tree BFS", 1.0),
]
