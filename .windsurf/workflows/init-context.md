---
description: Initialize Context Engineering Framework
---

# Context Engineering Initialization

This workflow loads the context engineering framework for structured AI development.

// turbo-all

1. **Load Project Guidelines**
   - Read and understand the project guidelines from `project-guidelines.md`
   - Apply these rules to all subsequent development work

2. **Scan Available Examples**
   - Review all files in the `examples/` directory
   - Note available code patterns and reference implementations

3. **Present Framework Overview**
   - Explain the enhanced context engineering process:
     1. Define Project (initial prompt with adaptive templates)
     2. Generate Plan (comprehensive planning with real-time knowledge)
     3. Review Plan (human validation with quality guardrails)
     4. Execute Plan (autonomous implementation with MCP integration)
   - Highlight new capabilities:
     - Real-time documentation access via MCP servers
     - Automated security and quality validation
     - Context-aware template selection
     - Community solution integration

4. **Request Initial Prompt**
   - Ask the user to provide their initial project prompt file path
   - If no file exists, guide them to create one using the template

5. **Create Project Memory**
   - Store the project context in memory for persistence across chats
   - Include project goals, tech stack, and key requirements

6. **Ready for Next Step**
   - Confirm the context is loaded and ready for `/generate-plan`
