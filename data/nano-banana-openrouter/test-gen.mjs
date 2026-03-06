import fetch from 'node-fetch';

const apiKey = "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";

async function generate() {
  console.log("Generating logo...");
  try {
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "OpenClaw Agent"
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash-image",
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Design a professional minimalist logo for a consulting firm named 'Luyu Consulting' (Shanghai Luyu Consulting Co., Ltd.). The name 'Luyu' references a deer in the forest and a guide ('Yu'). The logo should feature a stylized deer or deer antlers combined with a compass or star element, symbolizing guidance. Colors: Deep Navy Blue and Champagne Gold. Professional, trustworthy, elegant, modern vector style. White background."
              }
            ]
          }
        ],
        modalities: ["image"]
      })
    });

    if (!response.ok) {
      console.error("Error:", await response.text());
      return;
    }

    const data = await response.json();
    console.log("Result:", JSON.stringify(data, null, 2));
  } catch (e) {
    console.error(e);
  }
}

generate();
