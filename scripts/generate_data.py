"""
Synthetic dataset generator for the Prerequisite & Career Consequence Explorer.
Run this once to (re)build all CSV files inside data/.
This is provided for transparency/reproducibility -- the data/ folder already
ships with generated CSVs, so running this script is optional.
"""
import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(BASE, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. COURSES  (38 courses: 10 foundational + 28 electives/specializations)
# ---------------------------------------------------------------------------
courses = [
    # course_id, course_name, description, credits, category, skills_gained
    ("C001", "Java Programming", "Core Java syntax, OOP basics, collections and exception handling.", 4, "Foundational", "Java"),
    ("C002", "Object Oriented Programming", "Principles of OOP: encapsulation, inheritance, polymorphism, abstraction.", 4, "Foundational", "OOP"),
    ("C003", "Data Structures and Algorithms", "Arrays, linked lists, trees, graphs, sorting/searching, complexity analysis.", 4, "Foundational", "DSA;Problem Solving"),
    ("C004", "Database Management Systems", "Relational model, SQL, normalization, transactions and indexing.", 4, "Foundational", "DBMS;SQL"),
    ("C005", "Computer Networks", "OSI/TCP-IP model, routing, switching, protocols.", 3, "Foundational", "Networking"),
    ("C006", "Operating Systems", "Processes, threads, scheduling, memory management, concurrency.", 3, "Foundational", "OS Concepts"),
    ("C007", "Python Programming", "Python syntax, data structures, scripting and libraries.", 3, "Foundational", "Python"),
    ("C008", "Statistics and Probability", "Descriptive/inferential statistics, probability distributions, hypothesis testing.", 3, "Foundational", "Statistics"),
    ("C009", "Linear Algebra", "Vectors, matrices, eigenvalues - the math backbone of ML and cryptography.", 3, "Foundational", "Linear Algebra"),
    ("C010", "Web Development Fundamentals", "HTML, CSS, JavaScript basics and the DOM.", 3, "Foundational", "HTML/CSS/JS"),

    ("C011", "Spring Boot Development", "Building REST backends with Spring Boot, dependency injection, JPA.", 4, "Elective", "Spring Boot;Java;REST API"),
    ("C012", "Full Stack Web Development", "End-to-end web apps combining frontend, backend and databases.", 4, "Elective", "Full Stack Development;DBMS;REST API"),
    ("C013", "React.js Frontend Development", "Component-based UI development with React, hooks and state management.", 3, "Elective", "React;HTML/CSS/JS"),
    ("C014", "Machine Learning", "Supervised/unsupervised learning, model evaluation, scikit-learn.", 4, "Elective", "Machine Learning;Python"),
    ("C015", "Deep Learning", "Neural networks, CNNs, RNNs, training with TensorFlow/PyTorch.", 4, "Elective", "Deep Learning;Machine Learning"),
    ("C016", "Data Visualization", "Communicating data insights with Matplotlib, Seaborn and dashboards.", 3, "Elective", "Data Visualization;Python"),
    ("C017", "Big Data Analytics", "Distributed data processing with Spark/Hadoop ecosystems.", 4, "Elective", "Big Data;DBMS"),
    ("C018", "Cloud Computing Fundamentals", "IaaS/PaaS/SaaS models, virtualization, core cloud concepts.", 3, "Elective", "Cloud Computing"),
    ("C019", "AWS Cloud Architecture", "Designing scalable systems on AWS: EC2, S3, RDS, IAM.", 4, "Elective", "AWS;Cloud Computing"),
    ("C020", "DevOps and CI/CD", "Automated pipelines, Jenkins/GitHub Actions, infrastructure as code.", 3, "Elective", "DevOps;Cloud Computing"),
    ("C021", "Kubernetes and Containerization", "Docker containers and Kubernetes orchestration at scale.", 3, "Elective", "Kubernetes;Docker;Cloud Computing"),
    ("C022", "Network Security", "Firewalls, VPNs, intrusion detection, secure network design.", 3, "Elective", "Network Security;Networking"),
    ("C023", "Ethical Hacking", "Penetration testing methodology, vulnerability assessment tools.", 4, "Elective", "Ethical Hacking;Network Security"),
    ("C024", "Cryptography", "Symmetric/asymmetric encryption, hashing, digital signatures.", 3, "Elective", "Cryptography;Linear Algebra"),
    ("C025", "Cybersecurity Risk Management", "Risk assessment frameworks, compliance, incident response.", 3, "Elective", "Risk Management;Network Security"),
    ("C026", "Mobile App Development - Android", "Building native Android apps with Kotlin/Java.", 4, "Elective", "Android Development;Java;OOP"),
    ("C027", "iOS App Development", "Building native iOS apps with Swift.", 4, "Elective", "iOS Development;OOP"),
    ("C028", "Microservices Architecture", "Designing decoupled, independently deployable services.", 4, "Elective", "Microservices;Spring Boot;DBMS"),
    ("C029", "RESTful API Design", "Designing clean, versioned, secure REST APIs.", 3, "Elective", "REST API;DBMS"),
    ("C030", "NoSQL Databases", "Document, key-value and graph databases: MongoDB, Redis, Neo4j.", 3, "Elective", "NoSQL;DBMS"),
    ("C031", "Distributed Systems", "Consistency, consensus, fault tolerance in large-scale systems.", 4, "Elective", "Distributed Systems;Networking;OS Concepts"),
    ("C032", "Software Testing and QA", "Unit/integration testing, test automation, QA processes.", 3, "Elective", "Software Testing;OOP"),
    ("C033", "Agile Software Development", "Scrum, Kanban, sprint planning and iterative delivery.", 2, "Elective", "Agile;Project Management"),
    ("C034", "Natural Language Processing", "Text processing, embeddings, transformers for language tasks.", 4, "Elective", "NLP;Machine Learning"),
    ("C035", "Computer Vision", "Image processing, CNNs for detection/classification/segmentation.", 4, "Elective", "Computer Vision;Machine Learning"),
    ("C036", "Blockchain Fundamentals", "Distributed ledgers, consensus mechanisms, smart contracts.", 3, "Elective", "Blockchain;Cryptography"),
    ("C037", "IT Project Management", "Planning, scheduling, stakeholder management for IT projects.", 2, "Elective", "Project Management"),
    ("C038", "UI/UX Design Principles", "User research, wireframing, prototyping and usability testing.", 2, "Elective", "UI/UX Design;HTML/CSS/JS"),
]
courses_df = pd.DataFrame(courses, columns=[
    "course_id", "course_name", "description", "credits", "category", "skills_gained"
])
courses_df.to_csv(os.path.join(BASE, "courses.csv"), index=False)

# ---------------------------------------------------------------------------
# 2. PREREQUISITES  (course_id requires prerequisite_id)
# ---------------------------------------------------------------------------
prereq_pairs = [
    ("C011", "C001"), ("C011", "C002"),                       # Spring Boot <- Java, OOP
    ("C012", "C010"), ("C012", "C004"),                       # Full Stack <- WebDev, DBMS
    ("C013", "C010"),                                          # React <- WebDev
    ("C014", "C007"), ("C014", "C008"), ("C014", "C009"),      # ML <- Python, Stats, LinAlg
    ("C015", "C014"),                                          # Deep Learning <- ML
    ("C016", "C007"), ("C016", "C008"),                        # Data Viz <- Python, Stats
    ("C017", "C004"), ("C017", "C007"),                        # Big Data <- DBMS, Python
    ("C018", "C005"), ("C018", "C006"),                        # Cloud Fund <- Networks, OS
    ("C019", "C018"),                                          # AWS <- Cloud Fund
    ("C020", "C018"), ("C020", "C006"),                        # DevOps <- Cloud Fund, OS
    ("C021", "C018"),                                          # K8s <- Cloud Fund
    ("C022", "C005"),                                          # Network Security <- Networks
    ("C023", "C022"), ("C023", "C006"),                        # Ethical Hacking <- NetSec, OS
    ("C024", "C009"), ("C024", "C005"),                        # Crypto <- LinAlg, Networks
    ("C025", "C022"),                                          # Cyber Risk <- NetSec
    ("C026", "C001"), ("C026", "C002"),                        # Android <- Java, OOP
    ("C027", "C002"),                                          # iOS <- OOP
    ("C028", "C011"), ("C028", "C004"),                        # Microservices <- Spring Boot, DBMS
    ("C029", "C010"), ("C029", "C004"),                        # REST API <- WebDev, DBMS
    ("C030", "C004"),                                          # NoSQL <- DBMS
    ("C031", "C005"), ("C031", "C006"), ("C031", "C003"),      # Distributed Sys <- Networks, OS, DSA
    ("C032", "C002"),                                          # Testing <- OOP
    ("C034", "C014"),                                          # NLP <- ML
    ("C035", "C014"),                                          # CV <- ML
    ("C036", "C024"), ("C036", "C005"),                        # Blockchain <- Crypto, Networks
]
prereq_df = pd.DataFrame(prereq_pairs, columns=["course_id", "prerequisite_id"])
prereq_df.to_csv(os.path.join(BASE, "prerequisites.csv"), index=False)

# ---------------------------------------------------------------------------
# 3. COURSE OUTCOMES  (multiple outcomes per course)
# ---------------------------------------------------------------------------
outcomes_map = {
    "C001": ["Write robust Java programs using OOP concepts", "Use Java collections and exception handling effectively"],
    "C002": ["Apply encapsulation, inheritance and polymorphism in design", "Design class hierarchies for real-world problems"],
    "C003": ["Select appropriate data structures for a problem", "Analyze time/space complexity of algorithms"],
    "C004": ["Design normalized relational schemas", "Write efficient SQL queries and transactions"],
    "C005": ["Explain the OSI and TCP/IP models", "Configure basic routing and switching"],
    "C006": ["Explain process scheduling and memory management", "Reason about concurrency and synchronization"],
    "C007": ["Write Python scripts using core data structures", "Use Python libraries for automation"],
    "C008": ["Apply probability distributions to real data", "Perform hypothesis testing"],
    "C009": ["Perform matrix operations relevant to ML/crypto", "Compute eigenvalues/eigenvectors"],
    "C010": ["Build static web pages with HTML/CSS", "Add interactivity using JavaScript"],
    "C011": ["Build REST backends using Spring Boot", "Use Spring Data JPA for persistence"],
    "C012": ["Build an end-to-end web application", "Integrate frontend, backend and database layers"],
    "C013": ["Build component-based UIs with React", "Manage application state with hooks"],
    "C014": ["Train and evaluate supervised ML models", "Apply unsupervised learning techniques"],
    "C015": ["Design and train neural networks", "Apply CNNs/RNNs to real datasets"],
    "C016": ["Create insightful charts and dashboards", "Communicate data findings visually"],
    "C017": ["Process large datasets with distributed frameworks", "Design big-data pipelines"],
    "C018": ["Explain IaaS/PaaS/SaaS cloud models", "Compare major cloud providers"],
    "C019": ["Design scalable architectures on AWS", "Configure core AWS services (EC2, S3, RDS)"],
    "C020": ["Build CI/CD pipelines", "Apply infrastructure-as-code practices"],
    "C021": ["Containerize applications with Docker", "Orchestrate services with Kubernetes"],
    "C022": ["Configure firewalls and VPNs", "Detect and mitigate network intrusions"],
    "C023": ["Perform structured penetration tests", "Identify and report vulnerabilities"],
    "C024": ["Apply symmetric and asymmetric encryption", "Explain hashing and digital signatures"],
    "C025": ["Apply a security risk assessment framework", "Design an incident response plan"],
    "C026": ["Build native Android applications", "Manage Android app lifecycle and UI"],
    "C027": ["Build native iOS applications with Swift", "Design iOS UI using standard patterns"],
    "C028": ["Decompose a monolith into microservices", "Handle inter-service communication"],
    "C029": ["Design versioned, secure REST APIs", "Document APIs using OpenAPI/Swagger"],
    "C030": ["Model data for NoSQL databases", "Choose the right NoSQL store for a use case"],
    "C031": ["Reason about consistency and consensus", "Design fault-tolerant distributed systems"],
    "C032": ["Write unit and integration tests", "Apply test automation frameworks"],
    "C033": ["Run Scrum ceremonies effectively", "Plan and track iterative sprints"],
    "C034": ["Build text-processing pipelines", "Apply transformer models to language tasks"],
    "C035": ["Build image classification/detection models", "Apply CV techniques to real images"],
    "C036": ["Explain blockchain consensus mechanisms", "Write basic smart contracts"],
    "C037": ["Create IT project plans and schedules", "Manage stakeholders and IT project risk"],
    "C038": ["Conduct user research and usability tests", "Create wireframes and prototypes"],
}
rows = []
for cid, outs in outcomes_map.items():
    for o in outs:
        rows.append((cid, o))
outcomes_df = pd.DataFrame(rows, columns=["course_id", "outcome"])
outcomes_df.to_csv(os.path.join(BASE, "course_outcomes.csv"), index=False)

# ---------------------------------------------------------------------------
# 4. SCHEDULES  (day, start, end, room) -- deliberately includes conflicts
# ---------------------------------------------------------------------------
schedules = [
    ("C001", "Monday", "09:00", "11:00", "Room 101"),
    ("C002", "Tuesday", "09:00", "11:00", "Room 101"),
    ("C003", "Wednesday", "09:00", "11:00", "Room 102"),
    ("C004", "Monday", "11:00", "13:00", "Room 103"),
    ("C005", "Monday", "09:00", "11:00", "Room 104"),   # conflicts with C001 (Java)
    ("C006", "Thursday", "09:00", "11:00", "Room 104"),
    ("C007", "Tuesday", "11:00", "13:00", "Room 105"),
    ("C008", "Wednesday", "11:00", "13:00", "Room 105"),
    ("C009", "Friday", "09:00", "11:00", "Room 105"),
    ("C010", "Thursday", "11:00", "13:00", "Room 106"),
    ("C011", "Monday", "14:00", "16:00", "Room 201"),
    ("C012", "Tuesday", "14:00", "16:00", "Room 201"),
    ("C013", "Monday", "14:00", "16:00", "Room 202"),  # conflicts with C011 (Spring Boot)
    ("C014", "Wednesday", "14:00", "16:00", "Room 203"),
    ("C015", "Thursday", "14:00", "16:00", "Room 203"),
    ("C016", "Friday", "14:00", "16:00", "Room 203"),
    ("C017", "Tuesday", "16:00", "18:00", "Room 204"),
    ("C018", "Monday", "16:00", "18:00", "Room 205"),
    ("C019", "Wednesday", "16:00", "18:00", "Room 205"),
    ("C020", "Thursday", "16:00", "18:00", "Room 205"),
    ("C021", "Friday", "16:00", "18:00", "Room 205"),
    ("C022", "Monday", "09:00", "11:00", "Room 301"),   # also conflicts with C001/C005
    ("C023", "Tuesday", "09:00", "11:00", "Room 301"),
    ("C024", "Wednesday", "09:00", "11:00", "Room 301"),
    ("C025", "Thursday", "09:00", "11:00", "Room 301"),
    ("C026", "Friday", "09:00", "11:00", "Room 302"),
    ("C027", "Monday", "11:00", "13:00", "Room 302"),   # conflicts with C004 (DBMS)
    ("C028", "Tuesday", "11:00", "13:00", "Room 302"),
    ("C029", "Wednesday", "11:00", "13:00", "Room 302"),
    ("C030", "Thursday", "11:00", "13:00", "Room 302"),
    ("C031", "Friday", "11:00", "13:00", "Room 302"),
    ("C032", "Monday", "13:00", "14:00", "Room 106"),
    ("C033", "Tuesday", "13:00", "14:00", "Room 106"),
    ("C034", "Wednesday", "13:00", "14:00", "Room 106"),
    ("C035", "Thursday", "13:00", "14:00", "Room 106"),
    ("C036", "Friday", "13:00", "14:00", "Room 106"),
    ("C037", "Monday", "18:00", "19:30", "Room 107"),
    ("C038", "Tuesday", "18:00", "19:30", "Room 107"),
]
schedules_df = pd.DataFrame(schedules, columns=["course_id", "day", "start_time", "end_time", "room"])
schedules_df.to_csv(os.path.join(BASE, "schedules.csv"), index=False)

# ---------------------------------------------------------------------------
# 5. CAREER PATHWAYS  (career_role, course_id, relevance_score)
# ---------------------------------------------------------------------------
def rows_for(role, mapping):
    return [(role, cid, score) for cid, score in mapping.items()]

backend = {
    "C001": 85, "C002": 85, "C003": 80, "C004": 90, "C011": 95, "C028": 90,
    "C029": 90, "C030": 75, "C031": 80, "C032": 65, "C006": 60, "C005": 55,
    "C007": 40, "C013": 30, "C038": 20,
}
fullstack = {
    "C010": 90, "C012": 95, "C013": 90, "C004": 80, "C029": 80, "C038": 70,
    "C002": 60, "C001": 50, "C011": 55, "C030": 55, "C032": 50,
}
data_scientist = {
    "C007": 90, "C008": 90, "C009": 85, "C014": 95, "C015": 90, "C016": 85,
    "C017": 80, "C034": 80, "C035": 80, "C004": 55, "C037": 20,
}
cloud_engineer = {
    "C005": 85, "C006": 85, "C018": 95, "C019": 95, "C020": 90, "C021": 90,
    "C031": 80, "C022": 55, "C004": 45, "C007": 35,
}
cyber_analyst = {
    "C005": 85, "C006": 80, "C022": 95, "C023": 95, "C024": 85, "C025": 90,
    "C036": 55, "C031": 40, "C004": 30,
}
software_dev = {
    "C002": 90, "C003": 90, "C001": 80, "C007": 75, "C032": 85, "C033": 85,
    "C037": 70, "C004": 65, "C029": 55, "C038": 40,
}

career_rows = []
career_rows += rows_for("Backend Developer", backend)
career_rows += rows_for("Full Stack Developer", fullstack)
career_rows += rows_for("Data Scientist", data_scientist)
career_rows += rows_for("Cloud Engineer", cloud_engineer)
career_rows += rows_for("Cybersecurity Analyst", cyber_analyst)
career_rows += rows_for("Software Developer", software_dev)

career_df = pd.DataFrame(career_rows, columns=["career_role", "course_id", "relevance_score"])
career_df.to_csv(os.path.join(BASE, "career_pathways.csv"), index=False)

# required skill sets per role (used for skill-gap analysis)
required_skills = {
    "Backend Developer": "Java;OOP;DBMS;SQL;Spring Boot;Microservices;REST API;NoSQL;OS Concepts;Distributed Systems",
    "Full Stack Developer": "HTML/CSS/JS;DBMS;React;Full Stack Development;REST API;UI/UX Design",
    "Data Scientist": "Python;Statistics;Linear Algebra;Machine Learning;Deep Learning;Data Visualization;Big Data;NLP;Computer Vision",
    "Cloud Engineer": "Networking;OS Concepts;Cloud Computing;AWS;DevOps;Kubernetes;Distributed Systems",
    "Cybersecurity Analyst": "Networking;OS Concepts;Network Security;Ethical Hacking;Cryptography;Risk Management",
    "Software Developer": "OOP;DSA;Java;Python;Software Testing;Agile;Project Management;DBMS",
}
req_df = pd.DataFrame(
    [(role, skills) for role, skills in required_skills.items()],
    columns=["career_role", "required_skills"],
)
req_df.to_csv(os.path.join(BASE, "career_required_skills.csv"), index=False)

# ---------------------------------------------------------------------------
# 6. STUDENTS  (sample profiles covering the required test scenarios)
# ---------------------------------------------------------------------------
students = [
    ("S001", "Aditi Sharma", "Backend Developer", "C001;C002;C004", "Java;OOP;SQL", "Backend Developer"),
    ("S002", "Rohan Verma", "Data Scientist", "C007;C008", "Python;Statistics", "Data Scientist"),
    ("S003", "Priya Nair", "Cloud Engineer", "C005;C006;C018", "Networking;OS Concepts;Cloud Computing", "Cloud Engineer"),
    ("S004", "Karan Mehta", "Cybersecurity Analyst", "C005;C006", "Networking;OS Concepts", "Cybersecurity Analyst"),
    ("S005", "Sneha Iyer", "Full Stack Developer", "C010;C004;C002", "HTML/CSS/JS;DBMS;OOP", "Full Stack Developer"),
    ("S006", "Arjun Rao", "Software Developer", "", "", "Software Developer"),  # no completed courses (edge case)
]
students_df = pd.DataFrame(students, columns=[
    "student_id", "name", "career_goal", "completed_courses", "skills", "preferred_job_role"
])
students_df.to_csv(os.path.join(BASE, "students.csv"), index=False)

print("All CSV files generated successfully in:", os.path.abspath(BASE))
for f in sorted(os.listdir(BASE)):
    print(" -", f)
