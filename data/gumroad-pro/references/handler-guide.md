# AI Guide: Gumroad Pro Handler Interaction

This guide explains how an AI agent should interact with the interactive state machine in `handler.js`.

## 🚀 Initializing the Handler
To start the interactive merchant experience, the agent should evoke the **Main Menu**:
- **Option 1**: Call the command `/gp-main` or `main.menu` if available.
- **Option 2**: In response to a general prompt, send a message that triggers the main view generator (e.g., "Open Gumroad Pro dashboard").

## 🔄 State Machine & Navigation

### 1. Button Logic
The handler communicates predominantly through **Buttons**:
- **Protocol**: When the user clicks a button, the agent receives a `callback_data`.
- **Action**: Use the `callback_data` string prefixed with `gp:` to transition states.
- **Navigation**: Always respect "Back" buttons to return to parent menus without breaking the session flow.

### 📉 Reduced Spam Strategy
The handler logic is designed to minimize chat noise:
- **Reuse Context**: Use `action: 'edit'` for all transitions. `ctx.messageId` is used internally to target the correct message for replacement.
- **State Cleanup**: Always clear or update `ctx.session.gpPendingInput` to prevent stale input loops.
- **Interrupt Mode**: Use `interrupt: true` to prevent other skills from hijacking the conversation during multi-step flows.

### 2. Multi-Step State (`ctx.session`)
Certain actions (e.g., Marking a product as Shipped or Refunding a specific amount) require user input *after* a button is clicked.

**Workflow**:
1. User clicks a button (e.g., "Mark Shipped").
2. Handler sets `ctx.session.gpPendingInput = { action: 'mark_shipped', sid: '...' }`.
3. Handler sends a message asking for input: *"Please provide the tracking URL."*
4. **Agent Action**: The next user message is intercepted. The agent must:
   - Identify that a session state is active.
   - Process the user's text as the required input for that specific action.
   - Submit the action using the logic defined in `onMessage`.

### 3. Digit Fallback
On channels without native buttons (e.g., some terminals or SMS), the handler appends `[1]`, `[2]` labels to the text.
- **Agent Action**: Accept digits as valid navigation inputs corresponding to the labels provided.

## 🛑 Critical Constraints
- **Session Scoping**: Never assume state persists beyond a few minutes of inactivity.
- **Confirmation**: For destructive actions (Deletion/Refunds), always use the "Confirm" button flow provided by the view generator.
- **Error Recovery**: If a transition fails or state is lost, return the user to the Main Menu (`gp:main`).

## 🛠️ Debugging Interactions
If the UI seems stuck:
1. Verify `ctx.session` contents.
2. Clear `ctx.session.gpPendingInput` to reset the flow.
3. Call `renderResponse(ctx, getMainMenu())` to force a reset.
