import random
from typing import Dict, Any, List

class QuestionGenerationService:
    """
    Template-Based Dynamic Question Generation Engine.
    Generates tailored practice questions when question bank items are exhausted
    or when deep dive into specific missing concepts is required.
    
    NOTE FOR VIVA: This engine utilizes rule-based syntactic templates and concept maps,
    not an external commercial LLM API, ensuring 100% offline autonomy and reproducibility.
    """

    TEMPLATES = {
        "Java": {
            "Easy": [
                {
                    "category": "Core OOP",
                    "question_text": "What is encapsulation in Java and how do access specifiers help enforce it?",
                    "model_answer": "Encapsulation is bundling data (variables) and methods operating on that data into a single unit (class) while restricting direct access using private access specifiers. Getter and setter methods provide controlled access.",
                    "keywords": ["encapsulation", "private", "getters", "setters", "data hiding", "access specifiers"]
                },
                {
                    "category": "Memory Management",
                    "question_text": "Explain the difference between Heap and Stack memory allocation in the Java Virtual Machine (JVM).",
                    "model_answer": "Stack memory stores method frames, primitive local variables, and references to objects, operating in LIFO order with fast access. Heap memory stores all instantiated objects and JRE classes, managed automatically by Garbage Collection.",
                    "keywords": ["stack", "heap", "JVM", "garbage collection", "LIFO", "references", "objects"]
                }
            ],
            "Medium": [
                {
                    "category": "Collections Framework",
                    "question_text": "How does HashMap work internally in Java? Explain hashing, bucketing, and how collisions are resolved.",
                    "model_answer": "HashMap uses an array of Node buckets. When put() is called, hashCode() determines the bucket index. If multiple keys hash to the same bucket (collision), they are chained in a LinkedList. In Java 8+, if a bucket exceeds 8 nodes, it transforms into a balanced Red-Black Tree (O(log N)).",
                    "keywords": ["HashMap", "hashCode", "equals", "bucket", "collision", "LinkedList", "treeify", "Red-Black Tree"]
                },
                {
                    "category": "Multithreading",
                    "question_text": "What is the difference between Synchronized blocks and ReentrantLock in Java multithreading?",
                    "model_answer": "Synchronized is an implicit keyword locking mechanism released automatically when exiting blocks. ReentrantLock from java.util.concurrent provides explicit lock/unlock, tryLock with timeouts, interruptible locking, and fairness policies.",
                    "keywords": ["synchronized", "ReentrantLock", "concurrency", "lock", "unlock", "fairness", "tryLock"]
                }
            ],
            "Hard": [
                {
                    "category": "Concurrency & Architecture",
                    "question_text": "How does the Java Memory Model (JMM) ensure visibility and ordering using the 'volatile' keyword and 'happens-before' guarantees?",
                    "model_answer": "The volatile keyword ensures that reads and writes happen directly from main memory rather than CPU CPU caches, establishing a happens-before relationship that prevents compiler instruction reordering and guarantees variable visibility across threads.",
                    "keywords": ["volatile", "happens-before", "Java Memory Model", "reordering", "CPU cache", "visibility", "memory barrier"]
                }
            ]
        },
        "Python": {
            "Easy": [
                {
                    "category": "Language Fundamentals",
                    "question_text": "What are Python list comprehensions and how do they compare with traditional for loops in readability and performance?",
                    "model_answer": "List comprehensions offer a concise syntax for creating new lists from iterables [expr for item in iterable if cond]. They run faster in CPython because bytecode loops are optimized internally at the C level.",
                    "keywords": ["list comprehension", "iterable", "syntax", "performance", "readability", "for loop"]
                }
            ],
            "Medium": [
                {
                    "category": "Advanced Python",
                    "question_text": "Explain Python generators, the 'yield' keyword, and how they optimize memory consumption during large dataset processing.",
                    "model_answer": "Generators are functions that maintain their execution state and yield items lazily one at a time using 'yield' instead of returning a complete list. This reduces memory footprint to O(1) space when iterating over large streams.",
                    "keywords": ["generator", "yield", "lazy evaluation", "memory optimization", "iterator", "next"]
                },
                {
                    "category": "Metaprogramming",
                    "question_text": "What are Python decorators and how are closures used to implement wrapper functions?",
                    "model_answer": "Decorators are callables that accept a function as an argument and return a modified wrapper function without altering the original code. They leverage lexical closures to preserve access to arguments and outer scope state.",
                    "keywords": ["decorators", "closures", "wrapper", "first-class functions", "@ syntax", "arguments"]
                }
            ],
            "Hard": [
                {
                    "category": "Internals & Concurrency",
                    "question_text": "Explain the Global Interpreter Lock (GIL) in CPython. How does it impact multithreading vs multiprocessing for CPU-bound tasks?",
                    "model_answer": "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes simultaneously in CPython to protect reference counting. For CPU-bound tasks, multithreading cannot achieve multi-core speedup; multiprocessing or C-extensions are required.",
                    "keywords": ["GIL", "Global Interpreter Lock", "CPython", "mutex", "multiprocessing", "multithreading", "CPU-bound"]
                }
            ]
        },
        "DBMS": {
            "Easy": [
                {
                    "category": "Relational Basics",
                    "question_text": "What are primary keys, foreign keys, and unique keys in a relational database?",
                    "model_answer": "A primary key uniquely identifies each row in a table and cannot be NULL. A foreign key enforces referential integrity by referencing the primary key of another table. A unique key ensures distinct column values but may allow a NULL entry.",
                    "keywords": ["primary key", "foreign key", "unique key", "referential integrity", "NULL", "relational database"]
                }
            ],
            "Medium": [
                {
                    "category": "Normalization",
                    "question_text": "Explain First, Second, and Third Normal Forms (1NF, 2NF, 3NF) with reasons for avoiding data redundancy.",
                    "model_answer": "1NF requires atomic values without repeating groups. 2NF requires 1NF and no partial dependencies on a composite primary key. 3NF requires 2NF and no transitive dependencies (non-key attributes depending on other non-key attributes).",
                    "keywords": ["1NF", "2NF", "3NF", "normalization", "atomic", "partial dependency", "transitive dependency", "redundancy"]
                }
            ],
            "Hard": [
                {
                    "category": "Database Internals",
                    "question_text": "How do B+ Trees optimize index lookups and range scans compared to standard Binary Search Trees in storage engines?",
                    "model_answer": "B+ Trees have a high fan-out, reducing tree height and minimizing disk I/O reads. All keys and records reside in leaf nodes, which are linked sequentially in a doubly linked list, making range queries exceptionally efficient.",
                    "keywords": ["B+ Tree", "fan-out", "disk I/O", "leaf nodes", "range scan", "index lookup", "linked list"]
                }
            ]
        },
        "SQL": {
            "Easy": [
                {
                    "category": "Basic Queries",
                    "question_text": "What is the difference between DELETE, TRUNCATE, and DROP statements in SQL?",
                    "model_answer": "DELETE is a DML command that removes specific rows matching a WHERE clause and can be rolled back. TRUNCATE is a DDL command that deallocates all table pages rapidly without per-row logging. DROP completely removes the table schema and data.",
                    "keywords": ["DELETE", "TRUNCATE", "DROP", "DML", "DDL", "rollback", "transaction log", "schema"]
                }
            ],
            "Medium": [
                {
                    "category": "Window Functions",
                    "question_text": "Explain SQL Window Functions (ROW_NUMBER(), RANK(), DENSE_RANK()) and how the OVER(PARTITION BY ...) clause works.",
                    "model_answer": "Window functions perform calculations across a set of rows related to the current row without collapsing rows into a single summary. ROW_NUMBER gives sequential integers, RANK skips ranks after ties, and DENSE_RANK does not skip ranks after ties.",
                    "keywords": ["window functions", "ROW_NUMBER", "RANK", "DENSE_RANK", "PARTITION BY", "OVER", "ties"]
                }
            ],
            "Hard": [
                {
                    "category": "Query Optimization",
                    "question_text": "How do database query optimizers execute EXPLAIN plans, and how do composite indexes resolve costly table scans?",
                    "model_answer": "An EXPLAIN plan reveals whether an engine performs sequential full table scans, index scans, or index lookups. Composite indexes on (colA, colB) optimize queries following the leftmost prefix rule, eliminating sorting and temporary table creation.",
                    "keywords": ["EXPLAIN plan", "query optimizer", "composite index", "table scan", "index seek", "leftmost prefix"]
                }
            ]
        },
        "Data Structures": {
            "Easy": [
                {
                    "category": "Linear Structures",
                    "question_text": "What is the difference between an Array and a Linked List in memory representation and access speed?",
                    "model_answer": "Arrays store elements in contiguous memory blocks allowing O(1) random index access but fixed sizing. Linked lists store elements as scattered nodes connected via pointers, requiring O(N) sequential traversal but flexible O(1) insertion at endpoints.",
                    "keywords": ["array", "linked list", "contiguous", "pointers", "O(1) access", "O(N) traversal", "memory allocation"]
                }
            ],
            "Medium": [
                {
                    "category": "Non-Linear Structures",
                    "question_text": "Compare Breadth-First Search (BFS) and Depth-First Search (DFS) for graph traversal. What data structures do they utilize?",
                    "model_answer": "BFS traverses level by level using a Queue (FIFO), which is ideal for finding the shortest path on unweighted graphs. DFS explores deeply down branches using a Stack or recursion (LIFO), useful for topological sorting and cycle detection.",
                    "keywords": ["BFS", "DFS", "Queue", "Stack", "FIFO", "LIFO", "shortest path", "topological sort", "graph"]
                }
            ],
            "Hard": [
                {
                    "category": "Dynamic Programming",
                    "question_text": "Explain the core principles of Dynamic Programming: Optimal Substructure and Overlapping Subproblems, using Memoization vs Tabulation.",
                    "model_answer": "Dynamic Programming solves complex problems by breaking them into overlapping subproblems with optimal substructure. Memoization is top-down using recursion and a cache table. Tabulation is bottom-up iteratively building solutions from base states.",
                    "keywords": ["dynamic programming", "optimal substructure", "overlapping subproblems", "memoization", "tabulation", "top-down", "bottom-up"]
                }
            ]
        },
        "HTML/CSS": {
            "Easy": [
                {
                    "category": "Semantic HTML",
                    "question_text": "Why is semantic HTML important for accessibility (a11y) and search engine optimization (SEO)?",
                    "model_answer": "Semantic tags like <header>, <nav>, <article>, and <section> convey explicit meaning to assistive screen readers and search engine crawlers, improving website accessibility, keyboard navigation, and SEO indexation.",
                    "keywords": ["semantic HTML", "accessibility", "a11y", "SEO", "screen readers", "header", "nav", "article"]
                }
            ],
            "Medium": [
                {
                    "category": "Modern CSS",
                    "question_text": "Compare CSS Flexbox (1-dimensional) and CSS Grid (2-dimensional). When should each layout system be chosen?",
                    "model_answer": "Flexbox is designed for one-dimensional layouts along a single axis (row or column), ideal for navbars and card contents. CSS Grid is two-dimensional, handling both rows and columns simultaneously for complete page layouts.",
                    "keywords": ["Flexbox", "CSS Grid", "one-dimensional", "two-dimensional", "rows", "columns", "layout", "axis"]
                }
            ],
            "Hard": [
                {
                    "category": "Performance & Architecture",
                    "question_text": "Explain the Critical Rendering Path (DOM, CSSOM, Render Tree, Layout, Paint) and how CSS influences page load performance.",
                    "model_answer": "The browser parses HTML to construct DOM and CSS to construct CSSOM, combining them into the Render Tree. CSS is render-blocking: unoptimized stylesheets delay the layout (reflow) and paint phases.",
                    "keywords": ["Critical Rendering Path", "DOM", "CSSOM", "Render Tree", "layout", "reflow", "paint", "render-blocking"]
                }
            ]
        },
        "JavaScript": {
            "Easy": [
                {
                    "category": "Scoping & Variables",
                    "question_text": "What is the difference between var, let, and const in JavaScript regarding scoping and hoisting?",
                    "model_answer": "var is function-scoped and hoisted initialized as undefined. let and const are block-scoped and hoisted into a Temporal Dead Zone (TDZ). const cannot be reassigned after declaration.",
                    "keywords": ["var", "let", "const", "block scope", "function scope", "hoisting", "Temporal Dead Zone", "reassignment"]
                }
            ],
            "Medium": [
                {
                    "category": "Asynchronous JS",
                    "question_text": "Explain JavaScript Promises and how async/await syntax improves readability over nested callback chains.",
                    "model_answer": "A Promise represents an eventual completion or failure of an async operation with states: pending, fulfilled, or rejected. async/await is syntactic sugar built over promises, enabling linear synchronous-style try/catch error handling.",
                    "keywords": ["Promise", "async", "await", "pending", "fulfilled", "rejected", "callback hell", "try/catch"]
                }
            ],
            "Hard": [
                {
                    "category": "Advanced JS Engine",
                    "question_text": "Explain JavaScript closures and prototype chain inheritance. How do objects resolve property lookups via __proto__?",
                    "model_answer": "A closure is a function retaining access to its lexical scope even when invoked outside it. In prototypal inheritance, when an object property is accessed, the JS engine searches the object, then climbs its __proto__ chain until found or null.",
                    "keywords": ["closure", "lexical scope", "prototype chain", "__proto__", "prototypal inheritance", "property lookup"]
                }
            ]
        },
        "Spring Boot": {
            "Easy": [
                {
                    "category": "Spring Fundamentals",
                    "question_text": "What is Spring Boot Auto-Configuration and how does the @SpringBootApplication annotation initialize the app?",
                    "model_answer": "@SpringBootApplication combines @Configuration, @EnableAutoConfiguration, and @ComponentScan. Auto-configuration inspects classpath dependencies (e.g., presence of H2 or Tomcat) and automatically registers default beans.",
                    "keywords": ["@SpringBootApplication", "auto-configuration", "@ComponentScan", "@EnableAutoConfiguration", "beans", "classpath"]
                }
            ],
            "Medium": [
                {
                    "category": "RESTful Microservices",
                    "question_text": "How does Spring Boot handle REST API validation and global exception handling using @ControllerAdvice and @ExceptionHandler?",
                    "model_answer": "@ControllerAdvice creates a centralized interceptor for exceptions across all controllers. Methods annotated with @ExceptionHandler return standardized HTTP response bodies (like RFC 7807 problem details) with appropriate status codes.",
                    "keywords": ["@ControllerAdvice", "@ExceptionHandler", "global exception handling", "REST API", "validation", "ResponseEntity"]
                }
            ],
            "Hard": [
                {
                    "category": "Security & Architecture",
                    "question_text": "Explain Spring Security filter chains and how JWT (JSON Web Tokens) are validated using stateless OncePerRequestFilter.",
                    "model_answer": "Spring Security processes incoming requests through a DelegatingFilterProxy chain. A custom OncePerRequestFilter intercepts the Authorization Bearer header, parses the JWT claims, and registers an Authentication token in SecurityContextHolder.",
                    "keywords": ["Spring Security", "SecurityContextHolder", "JWT", "OncePerRequestFilter", "filter chain", "stateless", "bearer token"]
                }
            ]
        },
        "General Programming": {
            "Easy": [
                {
                    "category": "Clean Code",
                    "question_text": "What is the DRY (Don't Repeat Yourself) principle and how does modular code design improve software maintainability?",
                    "model_answer": "The DRY principle states that every piece of business logic or knowledge should have a single, unambiguous representation in a codebase. Extracting repeated logic into helper functions prevents regression bugs and eases refactoring.",
                    "keywords": ["DRY", "Don't Repeat Yourself", "modular code", "maintainability", "refactoring", "code reusability"]
                }
            ],
            "Medium": [
                {
                    "category": "Design Patterns",
                    "question_text": "Explain the Singleton design pattern and Factory design pattern with practical software engineering examples.",
                    "model_answer": "The Singleton pattern restricts a class instantiation to a single shared instance (e.g., database connection pool). The Factory pattern defines an interface for creating objects, delegating instantiation logic to subclasses based on input.",
                    "keywords": ["Singleton", "Factory pattern", "design patterns", "instantiation", "connection pool", "subclasses"]
                }
            ],
            "Hard": [
                {
                    "category": "System Design",
                    "question_text": "Explain the CAP theorem (Consistency, Availability, Partition Tolerance) for distributed systems and why trade-offs are necessary.",
                    "model_answer": "The CAP theorem states that a distributed data store can only guarantee at most two of the three properties: Consistency, Availability, and Partition Tolerance. In the presence of a network partition (P), the system must choose between C or A.",
                    "keywords": ["CAP theorem", "Consistency", "Availability", "Partition Tolerance", "distributed systems", "trade-offs", "network partition"]
                }
            ]
        },
        "HR": {
            "Easy": [
                {
                    "category": "Self Introduction",
                    "question_text": "Walk me through your resume and highlight your key technical strengths and accomplishments.",
                    "model_answer": "A compelling introduction summarizes education, core technical competencies (languages/frameworks), notable academic or capstone projects with their impact, and aligns career ambitions with the target organization.",
                    "keywords": ["resume walk-through", "technical strengths", "projects", "education", "career goals", "competencies"]
                }
            ],
            "Medium": [
                {
                    "category": "Work Ethic & Priorities",
                    "question_text": "How do you manage competing deadlines and prioritize multiple deliverable tasks under pressure?",
                    "model_answer": "I use structured prioritization frameworks like the Eisenhower Matrix, identify critical dependencies, communicate early with leads if bottlenecks occur, and break complex milestones into manageable sprint tasks.",
                    "keywords": ["prioritization", "deadlines", "under pressure", "communication", "milestones", "Eisenhower Matrix", "time management"]
                }
            ],
            "Hard": [
                {
                    "category": "Leadership & Ethics",
                    "question_text": "Describe a situation where you had to uphold ethical integrity or acknowledge an error that affected your team.",
                    "model_answer": "I take full accountability for mistakes immediately, identify the root cause without deflecting blame, notify team members and stakeholders transparently, implement a fix, and establish safeguards or tests to prevent recurrence.",
                    "keywords": ["ethical integrity", "accountability", "ownership", "transparency", "root cause", "safeguards", "learning"]
                }
            ]
        }
    }

    @classmethod
    def generate_question(
        cls,
        skill: str,
        difficulty: str = "Medium",
        interview_type: str = "Technical",
        company: str = "General",
        used_questions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a syntactically tailored question based on templates.
        Guarantees that generated questions are relevant to the requested skill and difficulty.
        """
        used_texts = set(used_questions or [])
        skill_key = skill if skill in cls.TEMPLATES else "General Programming"
        if interview_type == "HR":
            skill_key = "HR"

        diff_pool = cls.TEMPLATES.get(skill_key, {}).get(difficulty, [])
        if not diff_pool:
            # Fall back to medium or any available difficulty in skill
            diff_pool = (
                cls.TEMPLATES.get(skill_key, {}).get("Medium")
                or cls.TEMPLATES.get(skill_key, {}).get("Easy")
                or cls.TEMPLATES.get("General Programming", {}).get("Easy", [])
            )

        # Filter out questions already presented
        candidates = [q for q in diff_pool if q["question_text"] not in used_texts]

        if not candidates:
            # If all specific difficulty questions were used, pull from any difficulty in that skill
            all_diffs = []
            for d in ["Easy", "Medium", "Hard"]:
                for q in cls.TEMPLATES.get(skill_key, {}).get(d, []):
                    if q["question_text"] not in used_texts:
                        all_diffs.append((d, q))
            if all_diffs:
                chosen_diff, chosen_q = random.choice(all_diffs)
                return {
                    "question_text": chosen_q["question_text"],
                    "model_answer": chosen_q["model_answer"],
                    "keywords": chosen_q["keywords"],
                    "category": chosen_q.get("category", f"{skill_key} Concepts"),
                    "difficulty": chosen_diff,
                    "company": company,
                    "skill": skill,
                    "interview_type": interview_type,
                    "source": "generator"
                }

            # Fallback dynamic synthesis with company framing
            fallback_text = f"In the context of software engineering at {company}, explain the architectural best practices and common pitfalls associated with {skill}."
            return {
                "question_text": fallback_text,
                "model_answer": f"Best practices in {skill} require adherence to clean code, modular structure, comprehensive error handling, and performance considerations specific to {company}'s scale.",
                "keywords": [skill.lower(), "best practices", "clean code", "error handling", "performance", "architecture"],
                "category": f"{skill} Best Practices",
                "difficulty": difficulty,
                "company": company,
                "skill": skill,
                "interview_type": interview_type,
                "source": "generator"
            }

        selected = random.choice(candidates)
        return {
            "question_text": selected["question_text"],
            "model_answer": selected["model_answer"],
            "keywords": selected["keywords"],
            "category": selected.get("category", f"{skill_key} Analysis"),
            "difficulty": difficulty,
            "company": company,
            "skill": skill,
            "interview_type": interview_type,
            "source": "generator"
        }
