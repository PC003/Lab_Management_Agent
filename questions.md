# Fundamental Questions for Pathology Laboratory Management System

## Core System Understanding
1. What is the primary goal of this system? Who are the main users (patients, lab technicians, doctors, administrators)?

2. You mentioned the system should interact with users via LLM - what specific LLM do you plan to use (Claude, GPT, etc.) and how will it be integrated?

3. When you say "User can ask for available tests (lab/home/hospital) or request reports", what exactly does this mean? Are these predefined test categories or dynamic based on what's available?

4. For the test confirmation node that checks supplies availability - what specific supplies/inventory are we tracking, and where is this data stored?

5. You mentioned max 3 tries for test confirmation and 2 tries for asking LLM - what happens after these limits are exceeded? What's the user experience?

6. When the Pathology Doctor (John) verifies output, what specific criteria does he use for verification? Is this automated or manual?

7. For report delivery - what delivery methods are supported (email, SMS, portal download, etc.)?

8. You mentioned referral by doctor - how does the system identify when a test is referred by a doctor vs. self-requested?

## Langraph Implementation Details
9. What specific Langraph components are you planning to use (StateGraph, Nodes, Edges, etc.)?

10. How do you plan to structure the state in your Langraph implementation?

11. What programming language/framework are you using for this implementation?

12. How will you handle persistence/checkpointing in Langraph?

## Business Rules Clarification
13. What defines a "test" in your system? Is it a specific medical test (like CBC, glucose test, etc.)?

14. What happens if a user asks for something that's not a test or report request? Does the LLM give a specific response or just not answer?

15. For the "Lab test node which produces output" - what does this output look like? Is it raw test results or something else?

16. When the doctor doesn't verify and you "try to redo test" - what does redoing entail? Is it the same test or different parameters?

17. What happens in the refund process when tests can't be done after max tries?

18. How does the system handle concurrent users or multiple test requests?

## Technical Architecture
19. What external systems or databases does this need to integrate with?

20. Are there any specific security or compliance requirements (HIPAA, etc.) for this pathology lab system?

21. What is the expected scale of this system (number of tests per day, users, etc.)?

22. How will you test this Langraph implementation?