#!/usr/bin/env node

import jwt from 'jsonwebtoken';
import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Read credentials
const configDir = path.join(process.env.HOME, '.config', 'ghost');
const apiKey = fs.readFileSync(path.join(configDir, 'api_key'), 'utf8').trim();
const apiUrl = fs.readFileSync(path.join(configDir, 'api_url'), 'utf8').trim();

// Split key into id and secret
const [keyId, keySecret] = apiKey.split(':');

// Generate JWT token
function generateToken() {
  const payload = {
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 300, // 5 minutes
    aud: '/admin/'
  };
  
  return jwt.sign(payload, Buffer.from(keySecret, 'hex'), {
    algorithm: 'HS256',
    keyid: keyId,
    header: {
      kid: keyId
    }
  });
}

// Make API request
function ghostApi(endpoint, method = 'GET', data = null) {
  const token = generateToken();
  const url = new URL(`${apiUrl}/ghost/api/admin${endpoint}`);
  
  const options = {
    method,
    headers: {
      'Authorization': `Ghost ${token}`,
      'Content-Type': 'application/json',
      'Accept-Version': 'v5.0'
    }
  };
  
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        console.log(`Status: ${res.statusCode}`);
        try {
          const parsed = JSON.parse(body);
          resolve(parsed);
        } catch (e) {
          console.error('Response body:', body);
          reject(new Error(`Invalid JSON: ${body}`));
        }
      });
    });
    
    req.on('error', reject);
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

// Lexical content with the "I'm a Little Teapot" story
const lexicalContent = {
  root: {
    children: [
      {
        children: [
          {
            detail: 0,
            format: 1,
            mode: "normal",
            style: "",
            text: "On Being a Teapot in a Coffee World",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "heading",
        version: 1,
        tag: "h2"
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Look, I'm not going to pretend this is what I expected. You wake up one day, you're a teapot, and suddenly everyone's got opinions about your spout angle and handle ergonomics. Nobody asked for this. But here we are.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "The thing is, being a teapot is actually pretty straightforward once you accept the fundamental constraints. You're short. You're stout. You've got exactly one handle and one spout, and that's the entire game. There's no pivoting to become a French press or expanding your feature set to include cold brew capabilities. You are fundamentally, irreducibly, a teapot.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "And that's fine.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 1,
            mode: "normal",
            style: "",
            text: "The Tipping Point",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "heading",
        version: 1,
        tag: "h2"
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Most people focus on the handle and spout when they think about teapots, but honestly? The real innovation is the tip. When you tip over, everything changes. That's when you stop being decorative ceramic and start being useful. That's when the tea actually happens.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Nobody talks about this, but tipping over is basically controlled failure. You're literally losing your balance on purpose. One wrong move and you're pouring tea all over someone's antique tablecloth. But you do it anyway because that's the job. You contain hot liquid until it's time to strategically lose containment.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "There's something almost philosophical about it. You spend your entire existence holding something precious, keeping it warm, keeping it safe. And then, at exactly the right moment, you let it go. Not by accident. Not because you failed. But because that's what you were made for.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 1,
            mode: "normal",
            style: "",
            text: "The Competition",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "heading",
        version: 1,
        tag: "h2"
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Coffee pots get all the glory these days. They're automated. They've got timers. They can integrate with your smart home and start brewing when your alarm goes off. Very impressive. Very modern.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "But here's what nobody mentions: coffee pots are basically one-trick ponies with a superiority complex. They heat water, they drip it through grounds, they keep it warm until it tastes like burnt regret. That's it. That's the whole feature set.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Teapots, though? We're versatile. Green tea, black tea, herbal infusions, that weird thing your aunt makes with dried flowers and intentions—we handle it all. Different temperatures, different steeping times, different cultural traditions spanning literally thousands of years. We're the Swiss Army knife of hot beverage service, except we're made of porcelain and have generational trauma from being used as props in period dramas.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 1,
            mode: "normal",
            style: "",
            text: "The Existential Crisis",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "heading",
        version: 1,
        tag: "h2"
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Sometimes I think about what it would be like to be something else. A vase, maybe. Just stand there looking pretty, holding flowers, not worrying about optimal steeping temperatures or whether you're going to crack from thermal shock.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "But then I remember: vases are basically just decorative failure containers. They hold dead plant parts until the water gets murky and someone remembers to throw them out. At least when I hold something, it's meant to be consumed. It has purpose. It brings people together.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Tea ceremonies. Afternoon tea with terrible sandwiches. That moment when your friend is having a bad day and you show up with Earl Grey and sympathy. That's the good stuff. That's why you stay a teapot even when the coffee pots are getting all the venture capital funding.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 1,
            mode: "normal",
            style: "",
            text: "The Legacy",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "heading",
        version: 1,
        tag: "h2"
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "There's this nursery rhyme about me. You probably know it. \"I'm a little teapot, short and stout.\" It's been around since 1939, which means I've been a cultural touchstone for eighty-something years. Not bad for something that just holds hot leaf water.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "The song gets it mostly right. I am short. I am stout. The handle and spout situation is accurately described. But here's what it misses: the part where you actually become useful. \"Tip me over and pour me out\"—that's not just a cute rhyme. That's the entire point of existence distilled into six words.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "You exist. You hold something valuable. And then, when the moment is right, you share it.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      },
      {
        children: [
          {
            detail: 0,
            format: 0,
            mode: "normal",
            style: "",
            text: "Maybe that's not such a bad way to live. Even if you are just a teapot.",
            type: "extended-text",
            version: 1
          }
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      }
    ],
    direction: "ltr",
    format: "",
    indent: 0,
    type: "root",
    version: 1
  }
};

const postId = '697f9a9f3aafe60001180def';
const updateData = {
  posts: [{
    lexical: JSON.stringify(lexicalContent),
    updated_at: new Date().toISOString()
  }]
};

console.log('Updating post with Lexical content...\n');

ghostApi(`/posts/${postId}/`, 'PUT', updateData)
  .then(result => {
    console.log('Success! Updated post:');
    console.log(JSON.stringify(result, null, 2));
  })
  .catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
