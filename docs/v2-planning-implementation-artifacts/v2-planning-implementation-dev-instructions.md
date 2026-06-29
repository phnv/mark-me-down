# MARK-ME-DOWN V2 Enhancement Plan 
Lets make a plan to enhance this app to a v2, by implementing an adk workflow from the current refactor single llm agent

Our primary goal is to develop a adk agent workflow to automatically select a template given users rough draft note and the other current inputs;

Secondary goals:
- provide users a 'auto' select template option:
- adapt UI to plug to new adk workflow and correctly route to full workflow (NoteProfiler Agent -> RAG Template Engine -> NoteRefactor Agent ) 
or directly to a single call NoteRefactor v2 Agent;     
- adapt UI to have auto template option as default 
- adapt UI to have a select button to accept either Gemini or Openai api keys (by the side of current)

### New Use case flow
1 - user selects provider option: Gemini | Openai , and inputs API_KEY
2 - user selects refactor mode , writing style and frontmatter option
3 - user inputs rough messy note
4 - user selects template annd submits request:

   4.1 - selection == 'auto' (new default option)
   
   4.1.1
   - if user selects auto then first workflow node is the NoteProfiler agent node,
   - this node will output  from user inputs a semantic profile (NoteProfile) for RAG search
   4.1.2
   - Simialrity RAG engine will compose a document in yaml, vectorize it and use match_template sql function in supabase to retrieve templates ordered by similarity   
   * further NoteProfiler agent and NoteProfile dataclass specs, RAG and yaml style formatting references in annex 
   
   4.1.3
   - These fields will be forwarded to NoteRefactor Agent v2 :
      highest similarity ranking template template_model field,
      along with user original inputs: rewrite_style_mode, refactor_mode, frontmatter, text (rough note)
      plus NoteProfiler generated: instructions

   4.1.4
   - proceed to (4.2) Route to NoteRefactor Agent v2 with inputs enriched by NoteProfiler agent v2

   4.2 - selection != 'auto' (existing options from templates table)
   - route directly to NoteRefactor agent v2 node; 
   - implement same current NoteRefactor agent behaviour, logic and prompt but implement it as new adk workflow node

5 - app returns: box with similarity scores ((template_name, score) pairs) and below it  the current text box/preview widget with refactored markdown note below 

Files in annex provide:
- the implementation details and prompt to be consumed by the first node: NoteProfile agent 
- jupyter notebook with RAG search and retrieval code references
      + Build Semantic doc (embedding_text)
      + Vectorize
      + Search Similarity and Retrival Engine
       
- references for dataclasses (you may alter and rename them as strictly needed)

Architectural decisions:
- use appropriate adk workflow
- use gemini builtin resource or LiteLLM adapter for openai according to user selection 
   + both for agents llm and embedding vectorizer provider (references in annexed jupyter)
- the first note, NoteProfiler agent, must not directly feed its output model to the next node NoteRefactorAgent v2,
   since the second node also needs the origina user inputs - use session.state to handle this. 

- use after_agent_callbacks to make transformation from one node the other
- adapt data models as needed especially to replicate naming convention
- use your google-agents adk skills for this plan 
- keep model implementation flexible to accept either builtin gemini hardcoded model or litellm adapter for hardcoded openai model.  
- be concise and avoid creating unnecessary abstractions
- current agents in agents folder (note_refactor and note_profiler) must be kept as early experiments,  
   + so keep current agent files untouched, implement the new adk agent scaffold at mark-me-down/agents folder, make it independent from existing agents and plug it into the ui. 

                 ┌──────────────────────────┐
                 │ UserRefactorRequest      │
                 │                          │
                 │ • Raw note              │
                 │ • Refactor mode         │
                 │ • Writing style         │
                 │ • Template selection    │
                 └─────────────┬────────────┘
                               │
                               ▼
                     Is Template = Auto?
                               │
              ┌────────────────┴────────────────┐
              │                                 │
             Yes                               No
              │                                 │
              ▼                                 │
      +--------------------+                    │
      |   NoteProfiler     |                    │
      +--------------------+                    │
              │                                 │
              ▼                                 │
        Semantic NoteProfile                    │
              │                                 │
              ▼                                 │
      +--------------------+                    │
      |  Template RAG      |                    │
      +--------------------+                    │
              │                                 │
              ▼                                 │
      Retrieved Template                        │
              └─────────────────┬───────────────┘
                                │
                                ▼
                     +----------------------+
                     |    NoteFormatter     |
                     +----------------------+
                                │
                                ▼
                        Markdown Document