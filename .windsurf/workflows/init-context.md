---
description: Initialize Context Engineering Framework with Environment Analysis
---

# Context Engineering Initialization

This workflow loads the context engineering framework for structured AI development with comprehensive environment analysis and preparation.

// turbo-all

1. **Load Project Guidelines**
   - Read and understand the project guidelines from `project-guidelines.md`
   - Apply these rules to all subsequent development work

2. **Environment Analysis & Preparation**
   - **Project Type Detection**: Analyze project structure to determine technology stack
   - **Python Environment Assessment**: Use VirtualEnvironmentManager to detect Python projects
     - Check for requirements.txt, setup.py, or Python files
     - Assess current virtual environment status
     - Prepare recommendations for environment setup
   - **Git Repository Analysis**: Use GitOperationsManager to analyze repository state
     - Check Git repository status and health
     - Analyze commit history and collaboration patterns
     - Prepare intelligent Git operation recommendations
   - **Development Environment Validation**: Ensure all required tools are available

3. **Scan Available Examples with Environment Context**
   - Review all files in the `examples/` directory
   - Note available code patterns and reference implementations
   - **Environment-Specific Examples**: Identify examples relevant to detected project type
   - **Best Practice Patterns**: Highlight environment management and Git workflow examples

4. **Present Enhanced Framework Overview**
   - Explain the enhanced context engineering process:
     1. **Define Project** (initial prompt with adaptive templates and environment analysis)
     2. **Generate Plan** (comprehensive planning with real-time knowledge and environment considerations)
     3. **Review Plan** (human validation with quality guardrails and environment readiness)
     4. **Execute Plan** (autonomous implementation with automatic environment management and intelligent Git integration)
   - Highlight new capabilities:
     - **Automatic Virtual Environment Management**: Seamless Python environment isolation
     - **Intelligent Git Operations**: Smart commit and push recommendations
     - **Real-time documentation access** via MCP servers
     - **Automated security and quality validation**
     - **Context-aware template selection** with environment considerations
     - **Community solution integration**

5. **Request Initial Prompt with Environment Context**
   - Ask the user to provide their initial project prompt file path
   - If no file exists, guide them to create one using the template
   - **Environment Recommendations**: Provide suggestions based on detected project type
   - **Git Workflow Suggestions**: Recommend Git practices based on repository analysis

6. **Create Enhanced Project Memory**
   - Store the project context in memory for persistence across chats
   - Include project goals, tech stack, and key requirements
   - **Environment Context**: Store virtual environment status and recommendations
   - **Git Context**: Store repository analysis and collaboration patterns
   - **Development Setup**: Record tool availability and configuration recommendations

7. **Environment Readiness Validation**
   - **Virtual Environment Status**: Report current Python environment state
   - **Git Repository Health**: Summarize repository status and recommendations
   - **Tool Availability**: Confirm all required development tools are accessible
   - **Next Steps Preparation**: Prepare environment-specific recommendations for plan generation

8. **Ready for Next Step**
   - Confirm the context is loaded and ready for `/generate-plan`
   - **Environment Summary**: Display environment analysis results
   - **Optimization Suggestions**: Provide recommendations for improved development workflow
