import chalk from 'chalk'
import open from 'open'
import { startWebServer, getLanIps } from '../web/server.js'
import * as identityStore from '../storage/identity.js'

export async function cmdWeb({ port = 3000, noOpen = false, lan = false } = {}) {
  const identity = identityStore.load()
  if (!identity) {
    console.log(chalk.gray('// not initialized. run: 0x0 init'))
    process.exit(1)
  }

  console.log(chalk.gray('// starting 0x0 web...'))

  const { port: actualPort } = await startWebServer(port, { lan })
  const localhost = `http://localhost:${actualPort}`

  console.log()
  console.log(chalk.gray('// local'))
  console.log(chalk.white(`   ${localhost}`))

  if (lan) {
    const lanIps = getLanIps()
    if (lanIps.length > 0) {
      console.log()
      console.log(chalk.gray('// mobile (same wifi) — lan mode enabled'))
      for (const ip of lanIps) {
        console.log(chalk.white(`   http://${ip}:${actualPort}`))
      }
    }
  }

  console.log()
  console.log(chalk.gray('// ctrl+c to stop'))

  if (!noOpen) {
    await open(localhost)
  }
}
