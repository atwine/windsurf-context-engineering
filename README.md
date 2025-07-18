# Context Engineering Framework for Windsurf & Cascade

A structured approach to AI-assisted development that replaces "vibe coding" with comprehensive context engineering.

## 🎯 What is Context Engineering?

Context engineering is the practice of providing comprehensive, structured context to AI coding assistants to achieve better, more reliable results. Instead of relying on intuition and repetition ("vibe coding"), we create engineered context that includes:

- **Structured Planning**: Comprehensive project requirements and architecture
- **Examples & Patterns**: Reference implementations and coding standards
- **Documentation**: Current API references and best practices
- **Human Validation**: Review checkpoints to ensure quality

## 🚀 Quick Start

### For New Projects:
1. **Initialize**: `/init-context` - Load the context engineering framework
2. **Define**: Copy `initial-prompt-template.md` and fill out your project requirements
3. **Plan**: `/generate-plan ./your-project-prompt.md` - Generate comprehensive implementation plan
4. **Review**: Manually review and edit the generated plan in `plans/` directory
5. **Execute**: `/execute-plan ./plans/your-plan.md` - Autonomous implementation

### For Existing Projects:
1. **Initialize**: `/init-context` - Load framework in any new chat
2. **Continue**: Reference existing plans and context from memory

## 📁 Directory Structure

```
windsurf-context-engineering/
├── .windsurf/
│   └── workflows/           # Windsurf workflow definitions
│       ├── init-context.md
│       ├── generate-plan.md
│       └── execute-plan.md
├── _workflow_definitions/
│   └── rules/
│       └── project-guidelines.md  # Global coding standards
├── examples/                # Code patterns and reference implementations
├── plans/                   # Generated implementation plans
├── initial-prompt-template.md  # Template for new projects
└── README.md
```

## 🔄 The Context Engineering Process

### Step 1: Initialize Context
**Command**: `/init-context`

- Loads project guidelines and coding standards
- Scans available examples and patterns
- Prepares the context engineering framework
- Creates project memory for persistence

### Step 2: Define Your Project
**Action**: Create detailed project prompt

1. Copy `initial-prompt-template.md` to `my-project-prompt.md`
2. Fill out all sections:
   - High-level goals
   - Core features & requirements
   - Technology stack
   - Code examples (add to `examples/` folder)
   - Documentation references
   - Success criteria

### Step 3: Generate Implementation Plan
**Command**: `/generate-plan ./my-project-prompt.md`

- Analyzes your project requirements
- Reviews examples and documentation
- Creates comprehensive architecture plan
- Breaks down into sequential tasks
- Saves plan to `plans/` directory

### Step 4: Human Review & Validation
**Action**: Manual plan review

- Open the generated plan file
- Review architecture and approach
- Make any necessary edits
- Approve for execution

### Step 5: Execute the Plan
**Command**: `/execute-plan ./plans/your-plan.md`

- Autonomous implementation following the plan
- Creates files and directory structure
- Writes code with proper testing
- Handles dependencies and configuration
- Provides completion report

## 💡 Key Benefits

- **Reduced Hallucinations**: Comprehensive context prevents AI guessing
- **Better Architecture**: Upfront planning creates better structure
- **Consistent Quality**: Standardized guidelines and patterns
- **Time Savings**: Less debugging and iteration
- **Scalable Process**: Repeatable framework for any project

## 🔧 Usage Tips

1. **Always start with `/init-context`** in new chats
2. **Be specific in your initial prompt** - detail drives quality
3. **Use the examples folder** for patterns you want followed
4. **Review plans carefully** - human validation is crucial
5. **Iterate on the process** - refine your templates over time
