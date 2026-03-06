import { getMiNA } from "@mi-gpt/miot";
import dotenv from "dotenv";

dotenv.config();

const config = {
  userId: process.env.MI_USER_ID,
  passToken: process.env.MI_PASS_TOKEN,
  password: process.env.MI_PASSWORD,
  did: process.env.MI_DEVICE_ID,
  debug: true,
};

const mina = await getMiNA(config);
if (!mina) {
  console.error("登录失败");
  process.exit(1);
}

console.log("\n获取最近对话记录：");
const conversations = await mina.getConversations({ limit: 5 });

if (conversations?.records) {
  console.log(`\n共 ${conversations.records.length} 条记录：\n`);
  for (const record of conversations.records) {
    console.log(`时间: ${new Date(record.time).toLocaleString()}`);
    console.log(`用户: ${record.query}`);
    console.log(`---`);
  }
} else {
  console.log("没有对话记录");
}
