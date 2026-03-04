import * as dotenv from 'dotenv';
dotenv.config();

import { Command } from 'commander';
import { createAndUploadArt } from './skills/generateArt';
import { evolveAgent } from './skills/evolve';
import { postToX } from './skills/social';
import { mintNFT } from './skills/mintNFT';
import { listNFT } from './skills/listNFT';
import { checkRecentSales, startSalesMonitor } from './skills/monitorSales';

const program = new Command();

program
  .name('nft-skill')
  .description('Autonomous AI Artist Agent CLI for OpenClaw')
  .version('1.0.0');

program
  .command('generate')
  .description('Generate new art and upload to IPFS')
  .requiredOption('-g, --generation <number>', 'Generation number', parseInt)
  .requiredOption('-t, --theme <string>', 'Art theme description')
  .action(async (options: any) => {
    try {
      console.log(JSON.stringify({ status: 'running', message: 'Generating art...' }));
      const result = await createAndUploadArt(options.generation, options.theme);
      console.log(JSON.stringify({ status: 'success', result }));
    } catch (error: any) {
      console.error(JSON.stringify({ status: 'error', message: error.message }));
      process.exit(1);
    }
  });

program
  .command('evolve')
  .description('Trigger agent evolution')
  .requiredOption('-p, --proceeds <string>', 'Total sales proceeds in ETH')
  .requiredOption('-g, --generation <number>', 'Current generation', parseInt)
  .requiredOption('--trigger <string>', 'Reason for evolution')
  .action(async (options: any) => {
    try {
      console.log(JSON.stringify({ status: 'running', message: 'Evolving agent...' }));
      const result = evolveAgent({
        proceeds: options.proceeds,
        generation: options.generation,
        trigger: options.trigger
      });
      console.log(JSON.stringify({ status: 'success', result }));
    } catch (error: any) {
      console.error(JSON.stringify({ status: 'error', message: error.message }));
      process.exit(1);
    }
  });

program
  .command('tweet')
  .description('Post a tweet')
  .requiredOption('-c, --content <string>', 'Tweet content')
  .action(async (options: any) => {
    try {
      console.log(JSON.stringify({ status: 'running', message: 'Posting tweet...' }));
      const result = await postToX(options.content);
      if (result) {
        console.log(JSON.stringify({ status: 'success', result }));
      } else {
        throw new Error('Failed to post tweet');
      }
    } catch (error: any) {
      console.error(JSON.stringify({ status: 'error', message: error.message }));
      process.exit(1);
    }
  });

program
  .command('mint')
  .description('Mint an NFT on Base with an IPFS metadata URI')
  .requiredOption('-m, --metadata-uri <string>', 'IPFS metadata URI (ipfs://... or bare hash)')
  .action(async (options: any) => {
    try {
      console.log(JSON.stringify({ status: 'running', message: 'Minting NFT...' }));
      const result = await mintNFT(options.metadataUri);
      console.log(JSON.stringify({ status: 'success', result }));
    } catch (error: any) {
      console.error(JSON.stringify({ status: 'error', message: error.message }));
      process.exit(1);
    }
  });

program
  .command('list')
  .description('List an NFT on the marketplace')
  .requiredOption('-i, --token-id <string>', 'Token ID to list')
  .requiredOption('-p, --price <string>', 'Listing price in ETH')
  .action(async (options: any) => {
    try {
      console.log(JSON.stringify({ status: 'running', message: 'Listing NFT...' }));
      const result = await listNFT(options.tokenId, options.price);
      console.log(JSON.stringify({ status: 'success', result }));
    } catch (error: any) {
      console.error(JSON.stringify({ status: 'error', message: error.message }));
      process.exit(1);
    }
  });

program
  .command('monitor')
  .description('Watch for NFT sales (streams JSON events until Ctrl+C)')
  .option('-f, --from-block <number>', 'Start block for catching up on missed sales', parseInt)
  .action(async (options: any) => {
    try {
      console.log(JSON.stringify({ status: 'running', message: 'Starting sales monitor...' }));

      if (options.fromBlock) {
        await checkRecentSales(options.fromBlock, async (sale) => {
          console.log(JSON.stringify({ status: 'sale', result: sale }));
        });
      }

      const stop = startSalesMonitor(async (sale) => {
        console.log(JSON.stringify({ status: 'sale', result: sale }));
      });

      process.on('SIGINT', () => {
        stop();
        console.log(JSON.stringify({ status: 'stopped', message: 'Monitor stopped' }));
        process.exit(0);
      });
    } catch (error: any) {
      console.error(JSON.stringify({ status: 'error', message: error.message }));
      process.exit(1);
    }
  });

program.parse(process.argv);
