/**
 * Basic usage examples for Office to Markdown Skill
 * 
 * These examples show how to use the skill in OpenClaw sessions
 */

// Example 1: Simple conversion
async function example1() {
  console.log('=== Example 1: Simple Document Conversion ===');
  
  const filePath = '/path/to/your/document.doc';
  const cmd = `node /root/.openclaw/workspace/office-to-md-v2/office-to-md/openclaw-skill.js "${filePath}"`;
  
  const result = await exec(cmd, {
    workdir: '/root/.openclaw/workspace',
    timeout: 60000
  });
  
  if (result.exitCode === 0) {
    console.log('✅ Conversion successful!');
    console.log('Output:', result.stdout.substring(0, 200) + '...');
  } else {
    console.error('❌ Conversion failed:', result.stderr);
  }
}

// Example 2: Convert and analyze
async function example2() {
  console.log('\n=== Example 2: Convert and Analyze ===');
  
  const filePath = '/path/to/your/document.docx';
  const cmd = `node /root/.openclaw/workspace/office-to-md-v2/office-to-md/openclaw-skill.js "${filePath}"`;
  
  const result = await exec(cmd, {
    workdir: '/root/.openclaw/workspace',
    timeout: 60000
  });
  
  if (result.exitCode === 0) {
    // Parse the JSON output
    try {
      const output = JSON.parse(result.stdout);
      if (output.success) {
        console.log('✅ Conversion successful!');
        console.log(`Output file: ${output.outputPath}`);
        console.log(`File type: ${output.fileType}`);
        console.log(`Stats: ${output.stats.lines} lines, ${output.stats.words} words`);
        console.log(`Preview: ${output.preview.substring(0, 100)}...`);
        
        // Now you can read the Markdown file
        const markdownContent = await read(output.outputPath);
        console.log(`First 500 chars: ${markdownContent.substring(0, 500)}...`);
      }
    } catch (e) {
      console.log('Raw output:', result.stdout.substring(0, 500));
    }
  }
}

// Example 3: Error handling
async function example3() {
  console.log('\n=== Example 3: Error Handling ===');
  
  // Try to convert a non-existent file
  const filePath = '/path/to/nonexistent.pdf';
  const cmd = `node /root/.openclaw/workspace/office-to-md-v2/office-to-md/openclaw-skill.js "${filePath}"`;
  
  const result = await exec(cmd, {
    workdir: '/root/.openclaw/workspace',
    timeout: 30000
  });
  
  if (result.exitCode !== 0) {
    console.log('✅ Correctly detected error (as expected)');
    console.log('Error message:', result.stderr.substring(0, 200));
  }
}

// Example 4: Batch processing
async function example4() {
  console.log('\n=== Example 4: Batch Processing ===');
  
  const documents = [
    '/path/to/doc1.pdf',
    '/path/to/doc2.doc',
    '/path/to/doc3.docx',
    '/path/to/doc4.pptx'
  ];
  
  const results = [];
  
  for (const doc of documents) {
    console.log(`Processing: ${doc}`);
    
    const cmd = `node /root/.openclaw/workspace/office-to-md-v2/office-to-md/openclaw-skill.js "${doc}"`;
    
    try {
      const result = await exec(cmd, {
        workdir: '/root/.openclaw/workspace',
        timeout: 45000
      });
      
      if (result.exitCode === 0) {
        results.push({ file: doc, success: true });
        console.log('  ✅ Success');
      } else {
        results.push({ file: doc, success: false, error: result.stderr });
        console.log('  ❌ Failed:', result.stderr.substring(0, 100));
      }
    } catch (error) {
      results.push({ file: doc, success: false, error: error.message });
      console.log('  ❌ Error:', error.message);
    }
  }
  
  // Summary
  const successful = results.filter(r => r.success).length;
  console.log(`\nBatch processing complete: ${successful}/${results.length} successful`);
}

// Example 5: Using the module directly
async function example5() {
  console.log('\n=== Example 5: Direct Module Usage ===');
  
  // Note: This requires the module to be in the require path
  try {
    const { convertOfficeToMarkdown } = require('/root/.openclaw/workspace/office-to-md-v2/office-to-md/openclaw-skill.js');
    
    const result = await convertOfficeToMarkdown('/path/to/document.pdf');
    
    if (result.success) {
      console.log('✅ Direct module usage successful!');
      console.log(`Output: ${result.outputPath}`);
      console.log(`Preview: ${result.preview.substring(0, 150)}...`);
    } else {
      console.error('❌ Direct module usage failed:', result.error);
    }
  } catch (error) {
    console.error('❌ Failed to load module:', error.message);
  }
}

// Main function to run examples
async function runExamples() {
  console.log('Office to Markdown Skill - Usage Examples\n');
  
  // Uncomment the examples you want to run
  // await example1();
  // await example2();
  // await example3();
  // await example4();
  // await example5();
  
  console.log('\n=== Examples Complete ===');
  console.log('Remember to update file paths in the examples before running!');
}

// Export for testing
module.exports = {
  example1,
  example2,
  example3,
  example4,
  example5,
  runExamples
};