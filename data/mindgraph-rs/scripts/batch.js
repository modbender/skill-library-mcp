/**
 * skills/mindgraph/batch.js
 * 
 * Utility to perform multiple MindGraph operations (resolve, create, link) 
 * in a single execution to avoid gateway timeouts.
 * 
 * Updated to use the 18 Cognitive Layer Tools API.
 */

const mg = require('../../mindgraph-client.js');

async function run() {
    const input = process.argv[2];
    if (!input) {
        console.error("No input JSON provided.");
        process.exit(1);
    }

    try {
        const ops = JSON.parse(input);
        const results = {};

        for (const op of ops) {
            console.log(`Executing: ${op.type} - ${op.label || op.from}`);
            
            try {
                let node;
                switch (op.type) {
                    case 'ingest':
                    case 'addNode': // Compat
                        node = await mg.ingest(op.label, op.props?.content || op.summary || '', op.nodeType || 'observation', op.props);
                        results[op.id] = node;
                        break;
                    
                    case 'manageEntity':
                        node = await mg.manageEntity({ action: 'create', label: op.label, entityType: op.entityType });
                        results[op.id] = node;
                        break;
                    
                    case 'addCommitment':
                    case 'addGoal': // Compat
                        node = await mg.addCommitment(op.label, op.props?.content || op.summary || op.label, op.nodeType || 'goal', op.props);
                        results[op.id] = node;
                        break;

                    case 'deliberate':
                    case 'addDecision': // Compat
                        node = await mg.deliberate({ action: 'open_decision', label: op.label, description: op.props?.content || op.summary || op.label, ...op.props });
                        results[op.id] = node;
                        break;

                    case 'plan':
                    case 'addTask': // Compat
                        node = await mg.plan({ action: 'create_task', label: op.label, description: op.props?.content || op.summary || op.label, ...op.props });
                        results[op.id] = node;
                        break;

                    case 'link':
                        const fromUid = op.from.startsWith('$') ? results[op.from.substring(1)]?.uid : op.from;
                        const toUid = op.to.startsWith('$') ? results[op.to.substring(1)]?.uid : op.to;
                        if (fromUid && toUid) {
                            results[op.id] = await mg.link(fromUid, toUid, op.edgeType || 'RELEVANT_TO');
                        } else {
                            console.error(`Failed to link: ${fromUid} -> ${toUid}`);
                        }
                        break;

                    case 'evolve':
                    case 'updateNode': // Compat
                        const uid = op.uid.startsWith('$') ? results[op.uid.substring(1)]?.uid : op.uid;
                        results[op.id] = await mg.evolve('update', uid, { propsPatch: op.updates || op.propsPatch });
                        break;

                    case 'tombstone':
                    case 'deleteNode': // Compat
                        const delUid = op.uid.startsWith('$') ? results[op.uid.substring(1)]?.uid : op.uid;
                        results[op.id] = await mg.evolve('tombstone', delUid, { reason: op.reason || 'batch delete' });
                        break;

                    case 'resolve':
                        results[op.id] = await mg.search(op.text, { limit: 1 });
                        break;

                    default:
                        console.error(`Unknown op type: ${op.type}`);
                }
            } catch (err) {
                console.error(`Op ${op.id} failed: ${err.message}`);
                results[op.id] = { error: err.message };
            }
        }
        console.log("\nFinal Results:", JSON.stringify(results, null, 2));
    } catch (e) {
        console.error("Batch failed:", e.message);
        process.exit(1);
    }
}

run();
