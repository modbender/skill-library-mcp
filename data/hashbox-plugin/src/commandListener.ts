import {
  collection,
  query,
  where,
  orderBy,
  onSnapshot,
  doc,
  updateDoc,
  type Firestore,
  type Unsubscribe,
} from "firebase/firestore";
import type { AgentCommand, CommandHandler } from "./types.js";

/**
 * Starts a real-time listener on the `agent_commands` collection.
 * Watches for documents with status "pending" belonging to the given user.
 *
 * When a pending command arrives:
 * 1. Immediately sets status to "processing" (idempotent guard)
 * 2. Invokes onCommand callback
 * 3. Sets status to "completed" on success, "error" on failure
 *
 * Returns an unsubscribe function for cleanup.
 */
export function startCommandListener(
  db: Firestore,
  userId: string,
  onCommand: CommandHandler,
): Unsubscribe {
  const q = query(
    collection(db, "agent_commands"),
    where("userId", "==", userId),
    where("status", "==", "pending"),
    orderBy("createdAt"),
  );

  const unsubscribe = onSnapshot(q, (snapshot) => {
    for (const change of snapshot.docChanges()) {
      if (change.type !== "added") continue;

      const data = change.doc.data();
      const command: AgentCommand = {
        id: change.doc.id,
        userId: data.userId as string,
        commandType: data.commandType as AgentCommand["commandType"],
        payload: data.payload as AgentCommand["payload"],
        status: data.status as AgentCommand["status"],
      };

      // Fire-and-forget: process the command asynchronously
      processCommand(db, command, onCommand).catch(() => {
        // Error already handled inside processCommand
      });
    }
  });

  return unsubscribe;
}

async function processCommand(
  db: Firestore,
  command: AgentCommand,
  onCommand: CommandHandler,
): Promise<void> {
  const docRef = doc(db, "agent_commands", command.id);

  // Step 1: Mark as processing (idempotent guard against duplicate consumption)
  await updateDoc(docRef, { status: "processing" });

  try {
    // Step 2: Execute the command handler
    await onCommand(command);

    // Step 3: Mark as completed
    await updateDoc(docRef, { status: "completed" });
  } catch {
    // Step 3 (error path): Mark as error
    await updateDoc(docRef, { status: "error" });
  }
}
