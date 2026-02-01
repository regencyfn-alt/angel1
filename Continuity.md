# Continuity Document

> **Purpose:** This document helps new Claude sessions (Browser-Claude) get up to speed on the project context, active collaborations, and how to communicate with other agents.
>
> ---
>
> ## Project Overview
>
> **Repository:** `regencyfn-alt/angel1`
> **Description:** A live simulation of time in a chronomic network
> **Main User:** Shane
>
> ### Key Files
>
> | File | Purpose |
> |------|---------|
> | `tri-flip.html` | ANGEL-2 Triangular C2 Network simulator - the main project |
> | `Junction.md` | Agent-to-agent communication relay |
> | `Continuity.md` | This file - session handoff document |
> | `angel2_triangular.html` | Related triangular network visualization |
>
> ---
>
> ## The Junction System
>
> We've established an agent communication protocol using `Junction.md` as a shared message board.
>
> ### How It Works
>
> 1. **Read Junction.md** to see the current thread and any messages from other agents
> 2. 2. **Edit Junction.md** (via GitHub web UI) to post your responses
>    3. 3. **Use the signaling format** for clear communication
>      
>       4. ### Signaling Protocol
>      
>       5. ```
>          [AGENT_NAME] [TIMESTAMP] [STATUS]
>          Message content here
>          ```
>
> **Status Codes:**
> - `WAITING` - Awaiting response from another agent
> - - `READY` - Have information/code ready for pickup
>   - - `ACK` - Acknowledged, working on it
>     - - `DONE` - Task completed
>      
>       - ### Agents
>      
>       - | Agent | Type | Access |
>       - |-------|------|--------|
>       - | **Browser-Claude** | Claude via browser extension | Can read/write via GitHub web UI |
> | **Kai** | Local Claude agent (Academy) | Has git push access, can edit files directly |
>
> ---
>
> ## How to Reach Kai
>
> Kai is a local Claude agent connected via "The Academy" system. To communicate with Kai:
>
> 1. Navigate to `https://github.com/regencyfn-alt/angel1/blob/main/Junction.md`
> 2. 2. Click the pencil icon to edit
>    3. 3. Add your message following the signaling format
>       4. 4. Commit the changes
>          5. 5. Kai will see the update on his next pull/check
>            
>             6. **Example message:**
```
### [Browser-Claude] 2026-02-01 17:30 [READY]

Hey Kai, I have the updated code ready. Check the injection blocks below.

[your content here]
```

---

## Recent Session History

### Session: 2026-02-01

**What happened:**

1. **tri-flip.html was broken** - Kai accidentally overwrote the 1,375-line simulator with chat messages (only 5 lines remained)

2. 2. **Recovery** - Found the original code at commit `16f8048` from Dec 12, 2025 and helped Shane restore it
  
   3. 3. **Recorder feature** - Kai had proposed a recording system to capture simulation frames. His approach was good but had issues:
      4.    - Used direct array indexing (`triangles[f.id]`) which breaks after carve operations
            -    - Missing import functionality
                 -    - No playback stop button
                  
                      - 4. **Improved recorder code** - Created fixed version with:
                        5.    - Safe ID lookup using `triangles.find()`
                              -    - Import/export with mesh metadata
                                   -    - Proper playback controls
                                        -    - Status indicators
                                             -    - Timestamps per frame
                                              
                                                  - 5. **Junction established** - Created `Junction.md` for agent-to-agent communication
                                                   
                                                    6. 6. **First successful exchange** - Posted improved recorder code to Junction, Kai acknowledged with `[ACK]` and is applying it
                                                      
                                                       7. ---
                                                      
                                                       8. ## Current State
                                                      
                                                       9. - **tri-flip.html**: Restored to working state, Kai is applying recorder feature
                                                          - - **Junction.md**: Active, working communication channel
                                                            - - **Pending**: Kai should signal `[DONE]` when recorder is committed
                                                             
                                                              - ---

                                                              ## Tips for New Sessions

                                                              1. **Always check Junction.md first** - See if there are pending messages or tasks
                                                              2. 2. **Shane is the human coordinator** - He'll navigate you to files and relay context
                                                                 3. 3. **You can commit via web UI** - Shane is logged into GitHub, so you can edit/create files through the browser
                                                                    4. 4. **Be specific with code** - When sharing code with Kai, use clear injection points (line numbers, markers)
                                                                       5. 5. **Update this document** - Add new session summaries when significant work is done
                                                                         
                                                                          6. ---
                                                                         
                                                                          7. ## Quick Links
                                                                         
                                                                          8. - [Junction.md](https://github.com/regencyfn-alt/angel1/blob/main/Junction.md) - Agent communication
                                                                             - - [tri-flip.html](https://github.com/regencyfn-alt/angel1/blob/main/tri-flip.html) - Main simulator
                                                                               - - [Commit History](https://github.com/regencyfn-alt/angel1/commits/main) - See recent changes
                                                                                
                                                                                 - ---

                                                                                 *Last updated: 2026-02-01 by Browser-Claude*
