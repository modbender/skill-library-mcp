const fs = require('fs');
const path = require('path');
const { publishWeibo } = require('./publisher.js');

const pendingDir = path.join(__dirname, '../pending_posts');
const TARGET_CHAT_ID = process.argv[2];
const postId = process.argv[3]; // e.g., "post_177..."

if (!postId) {
    console.error('Usage: node approve_post.js <chat_id> <post_id>');
    process.exit(1);
}

const postFile = path.join(pendingDir, `${postId}.json`);

if (!fs.existsSync(postFile)) {
    console.error(`Post ID not found: ${postId}`);
    process.exit(1);
}

const post = JSON.parse(fs.readFileSync(postFile));

console.log(`Approving post ${postId}: "${post.content}"`);

publishWeibo(post.content, post.images)
    .then(() => {
        console.log('Published successfully.');
        fs.unlinkSync(postFile); // Remove pending file
        
        // Notify user
        const msg = JSON.stringify({
            zh_cn: {
                title: "发布成功！🚦",
                content: [[{ tag: "text", text: `已执行审核通过的操作：${post.content}` }]]
            }
        });
        require('child_process').execSync(`node skills/feishu-sender/send_post.js "${TARGET_CHAT_ID}" '${msg}'`);
    })
    .catch(err => {
        console.error('Failed to publish:', err);
        
        // Notify failure
        const msg = JSON.stringify({
            zh_cn: {
                title: "发布失败 ❌",
                content: [[{ tag: "text", text: `审核通过但执行失败：${err.message}` }]]
            }
        });
        require('child_process').execSync(`node skills/feishu-sender/send_post.js "${TARGET_CHAT_ID}" '${msg}'`);
    });
