import fs from 'fs';

const data = JSON.parse(fs.readFileSync('output.json', 'utf8').replace("Generating logo...", "").replace("Result: ", ""));
const imageUrl = data.choices[0].messages?.[0]?.images?.[0]?.image_url?.url || data.choices[0].message?.content;
// Actually the structure seems: choices[0].message.images[0].image_url ? or content link?
// Let's re-read the structure from the truncated output.
// "images": [ { "type": "image_url", "image_url": { ... } } ] inside message or just choices?

// Based on output: `choices[0].message.images[0].image_url` is an object?
// Or maybe it is `image_url` string.
// Let's inspect the `output.json` structure properly first.

const raw = fs.readFileSync('output.json', 'utf8');
const jsonPart = raw.substring(raw.indexOf('{'));
const json = JSON.parse(jsonPart);

// Check if image is in content (markdown) or in a special field
// The log showed "images": [ ... ] inside message?
// Ah, the output log showed:
// "message": { ... "images": [ { "type": "image_url", "image_url": { ... } } ] }

// Start by dumping keys to see where the data is
const choice = json.choices[0];
const msg = choice.message;

if (msg.images && msg.images.length > 0) {
   const imgObj = msg.images[0];
   let url = imgObj.image_url;
   if (typeof url === 'object') url = url.url; // handle nested object
   
   if (url.startsWith('data:image')) {
     const base64Data = url.split(',')[1];
     fs.writeFileSync('logo.png', base64Data, 'base64');
     console.log('Saved directly from base64 to logo.png');
   } else {
     console.log('Image is a URL:', url);
   }
} else {
  console.log('No images found in message object.');
}
