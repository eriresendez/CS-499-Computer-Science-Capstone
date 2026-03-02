[Artifact One](https://github.com/eriresendez/CS-499-Computer-Science-Capstone/tree/main/CS340)        [Artifact Two](https://github.com/eriresendez/CS-499-Computer-Science-Capstone/tree/main/CS360/Artifact2)        [Artifact Two](https://github.com/eriresendez/CS-499-Computer-Science-Capstone/tree/main/CS360/Artifact2)        [Artifact Three Full Code](https://github.com/eriresendez/ArtifactThree-EventTrackingApp)        [Artifact Three Files](https://github.com/eriresendez/CS-499-Computer-Science-Capstone/tree/main/CS360/Artifact3)          [Enhancement Plan](https://github.com/eriresendez/CS-499-Computer-Science-Capstone/blob/main/CS%20499%20Enhancement%20Plan.pdf)


## The three artifacts in this ePortfolio were carefully selected to address a different dimension of software engineering competency, and together they form a coherent narrative about a developer capable of building complete, secure, production-oriented systems from the data layer upward.

Artifact one that was the Austin Animal Shelter Dashboard demonstrates full-stack architectural design. The original project, a Dash-based Python application backed by a CSV file, was functional but monolithic. Every piece of logic, data access, business rules, and UI rendering, existed in a single file. The enhanced version separates these concerns across a FastAPI backend and React frontend, introduces JWT-based role authentication with three distinct permission scopes, adds real-time WebSocket broadcasting, and validates all inputs through Pydantic v2 models before data reaches business logic. This artifact shows that I can design and build industry-standard systems that are maintainable, testable, and secure by construction.

Original Dashboard: 


<img width="619" height="647" alt="Screenshot 2025-10-24 at 9 33 39 PM" src="https://github.com/user-attachments/assets/68e05ba6-a172-4859-bf3b-ef378441a1e1" />
<img width="2190" height="927" alt="Screenshot 2025-10-24 at 9 34 48 PM" src="https://github.com/user-attachments/assets/6ae144ee-6e4d-46b6-a4e0-8e3a5b25c7f2" />



Current: 

<img width="1870" height="1323" alt="Screenshot 2026-02-22 at 10 07 59 PM" src="https://github.com/user-attachments/assets/ed1869f1-fcc4-4514-bcac-a0fdc451d630" />


Artifact two is the Event Tracking Application, which demonstrates applied algorithmic reasoning. The original application used ArrayList and linear search everywhere. The enhanced version replaces this with a composite data structure design, HashMap plus TreeMap, encapsulated in a dedicated EventManager class. This artifact shows that I can identify performance bottlenecks, select appropriate data structures, reason about trade-offs between lookup speed and memory usage, and handle the concurrency implications that arise when multiple threads access shared state.

<img width="323" height="693" alt="Screenshot 2026-03-01 at 9 42 52 AM" src="https://github.com/user-attachments/assets/812d05f2-31a3-49f3-9425-54b4f7f9b2bb" />


.


<img width="324" height="689" alt="Screenshot 2026-03-01 at 9 43 15 AM" src="https://github.com/user-attachments/assets/d760fb7c-e7a1-4c33-ac72-adc1d29383e8" />

.


<img width="323" height="532" alt="Screenshot 2026-03-01 at 9 42 34 AM" src="https://github.com/user-attachments/assets/95a5db15-d473-492c-bede-af8b700ec482" />

Artifact three also uses the Event Tracking Application. It demonstrates modern database architecture and security-minded data design. The original application used raw SQLite calls scattered throughout activity code, creating both a maintainability problem and a SQL injection vulnerability. The enhanced version migrates to Room Persistence Library with a full MVVM architecture, clearly defined Entity, DAO, Repository, and ViewModel layers, salted password hashing, entity-level input validation, per-user data isolation, and structured schema versioning with migration support. This artifact shows that I can design database layers that are not only efficient but proactively resistant to the categories of attack that unstructured data access enables.

<img width="308" height="330" alt="Screenshot 2026-03-01 at 3 29 50 PM" src="https://github.com/user-attachments/assets/189042fd-2595-493d-9a49-4fde90597228" />

.


<img width="306" height="423" alt="Screenshot 2026-03-01 at 3 34 44 PM" src="https://github.com/user-attachments/assets/73a5607f-b83f-4ebe-ae1a-547e2329cb04" />


.

<img width="383" height="806" alt="Screenshot 2026-03-01 at 6 54 30 PM" src="https://github.com/user-attachments/assets/bf94fd7e-2637-45f9-9c92-a66c55902233" />


Taken together, these three artifacts demonstrate that I can architect layered systems, reason about the algorithmic behavior of those systems under realistic load, and build the secure, validated data foundations those systems depend on. That combination, design thinking, algorithmic competence, and security-first data architecture, represents the professional profile I bring to the computer science field.


# Professional Self-Assessment

My educational journey in computer science has been a profoundly transformative experience. I began in the fall semester of 2022 in the Computer Science program. Originally this was terrifying and challenging as I knew nothing, but it has been very rewarding. This program provided me with the tools to create a strong foundation in programming, mobile development, software design, client-server systems, and secure system architecture. I gathered this knowledge and carried it forward to each subsequent project. I am continuously learning new skills and techniques that allow me to become a better programmer.
This ePortfolio represents the culmination of that growth, bringing together three enhanced artifacts that demonstrate my capabilities across software engineering and design, algorithms and data structures, and database development. This knowledge has allowed me to architect full-stack systems, reason carefully about algorithmic trade-offs, and build secure, maintainable real-world applications. The Computer Science program has given me the technical foundation to pursue my goals. 

A course that laid a great foundation is CS-260: Data Structures and Algorithms. This course gave me the foundational vocabulary for reasoning about computational efficiency. Selecting proper data structures, remaining efficient and preserving readability and maintainability were highlighted during this course. This course helped me understand search algorithms, binary search trees, hash tables, hashing algorithms, hash tables, vector sorting and various other techniques. Some of these techniques, I continue to use consistently and used for the artifacts. Another course that was extremely beneficial was, I believe DAD-220, where I was introduced to SQL, database structure, and how to examine data using CRUD (Create, Read, Update, Delete). Using CRUD became beneficial and was was consistently used for my artifact enhancements. 

Collaborating in a team environment is an essential skill. Through various courses, I was prepared for collaborative environments. One of the most impactful take-aways from courses was learning how important thinking of a future collaborator will lead to quality code to provide clarity. This includes utilizing comments but also maintaining organized and discrete modules because modular code is collaborative code. In the Animal Shelter Dashboard, separated and organized routes, services, data models, and middleware can allow future collaborators and team members to modify in an appropriate manner.  

Through various courses, communicating with stakeholders allowed me to learn to interact and further develop communication skills. Specifically, through team-based projects like the DriverPass taught me how to communicate with clients and stakeholders through simulated situations where I would gather requirements, design system architectures, and provide technical solutions in an easy-to-understand manner. Additionally, in the Software Development Lifecycle course I was able to practice writing user stories, and retrospective reports aimed at stakeholders who needed to understand project direction without reading source code. This translated into the Animal Shelter Dashboard. It is a communication artifact: its role-based interface presents the same underlying data differently depending on whether the user is an administrator, a rescue team leader, or a viewer, reflecting an understanding that information must be tailored to its audience. The multi-format export panel, which generates CSV, JSON, Excel, and PDF reports, was designed specifically so that shelter staff without technical backgrounds could extract and share data in formats they already use.

As previously mentioned, CS-250 gave me a strong foundation in data structures and algorithms that allowed me to apply my knowledge for the second enhancement in CS-360. The Event Tracking Application originally used a flat ArrayList for all event storage and relied on linear search for every retrieval operation. Replacing it with a composite design, a HashMap for O(1) ID-based lookups paired with a TreeMap for sorted, date-range-bounded queries, required me to think carefully about which operations would be called most frequently and what memory trade-offs were acceptable. The TreeMap's subMap() method makes date-range filtering efficient as the dataset grows, an improvement that would be invisible on ten events but significant on ten thousand. I also encountered a real concurrency vulnerability during testing: the lock object declared in the EventManager class was never applied to any synchronization block, leaving the TreeMap entirely unprotected. Diagnosing and resolving ConcurrentModificationException crashes taught me that correct-looking code can fail at runtime under concurrent load, reinforcing why algorithmic reasoning must extend to execution environment, not just asymptotic complexity.

The Software Test, Automation, and QA course introduced me to unit testing. This assisted me in enhancement three. I wrote unit tests to verify security-critical behaviors in the Event Tracking Application, including a test that confirms identical passwords produce different hashes due to salting, and boundary tests that reject malformed inputs before they reach the database. CS-340 introduced me to client-server architecture using Python, MongoDB, and a Dash frontend. Enhancement One took that foundation and rebuilt it at production scale: a FastAPI backend with JWT Bearer token authentication, bcrypt password hashing, Pydantic v2 data validation, and a React frontend with real-time WebSocket support. The migration required redesigning from the ground up rather than translating syntax line by line, because the original monolithic Dash application had no concept of layer separation. Learning to architect the system into routes, services, data models, and middleware, each with a single, clearly scoped responsibility, was the one of the most significant software engineering lessons of the capstone. 

Security is a structural part built into a systems architecture. In the Animal Shelter Dashboard, authentication is enforced through a require_permission() dependency function that gates every route declaratively, meaning access control cannot be accidentally bypassed by a developer who forgets to add an if-statement. JWT Bearer tokens with bcrypt password hashing protect credentials in transit and at rest. In the Event Tracking Application, the migration from raw SQLite to Room's annotation-based query system made SQL injection attacks architecturally impossible rather than merely mitigated, because insecure query construction cannot compile. Salted password hashing using SecureRandom ensures that two users with identical passwords produce entirely different stored values, defeating rainbow table attacks. The removal of fallbackToDestructiveMigration() means Room throws a clear exception on unhandled schema versions rather than silently wiping user data. These decisions reflect a security mindset that CS-405 (Secure Coding) introduced and that I have since internalized: the safest code is code that makes insecure behavior structurally impossible, not code that relies on developer discipline to avoid it.
