import Hyperswarm from 'hyperswarm'
import { channelSecret } from './channel.js'

export function createSwarm() {
  return new Hyperswarm()
}

// 相手の番号とPINでチャンネルに参加
export function joinChannel(swarm, recipientNumber, pin, opts = {}) {
  const topic = channelSecret(recipientNumber, pin)
  return swarm.join(topic, { server: true, client: true, ...opts })
}
