---
description: Generate Comprehensive Implementation Plan
---

# Generate Implementation Plan

This workflow creates a detailed, step-by-step implementation plan from your project prompt.

// turbo-all

1. **Read Initial Prompt**
   - Load the provided initial prompt file
   - Parse all sections: goals, features, tech stack, examples, documentation

2. **Analyze Examples**
   - Review all files in the `examples/` directory
   - Extract patterns, conventions, and implementation approaches

3. **Research Documentation**
   - Review all provided documentation links
   - Gather current best practices and API information

4. **Architecture Planning**
   - Define system architecture based on requirements
   - Propose file structure and organization
   - Identify key components and their interactions

5. **Task Breakdown**
   - Create detailed, sequential task list
   - Include specific implementation steps
   - Add testing and validation checkpoints

6. **Generate Plan Document**
   - Create comprehensive plan in `plans/` directory
   - Include success criteria and acceptance tests
   - Format for easy human review and modification

7. **Save to Memory**
   - Store the generated plan in memory
   - Enable context persistence for execution phase

8. **Present for Review**
   - Display plan summary to user
   - Request human validation before execution
