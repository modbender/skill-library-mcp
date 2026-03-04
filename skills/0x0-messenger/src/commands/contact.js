import chalk from 'chalk'
import { parseUri } from '../core/uri.js'
import * as contactsStore from '../storage/contacts.js'

function log(msg) {
  console.log(chalk.gray(msg))
}

function formatContact(c) {
  const short = c.id.slice(0, 8)
  const label = c.label ? `  [${c.label}]` : ''
  const key = c.peerPublicKey ? `  key:${c.peerPublicKey.slice(0, 8)}…` : ''
  return `${short}  ${c.theirNumber}/${c.theirPin}${label}${key}`
}

export function cmdContactAdd(uriOrNumber, pin, opts = {}) {
  const parsed = parseUri(uriOrNumber)
  const theirNumber = parsed ? parsed.number : uriOrNumber
  const theirPin = parsed ? parsed.pin : pin

  if (!theirNumber || !theirPin) {
    log('// usage: contact add <uri> or contact add <number> <pin>')
    return
  }

  const contact = contactsStore.create({
    theirNumber,
    theirPin,
    label: opts.label || ''
  })

  log(`// saved: ${formatContact(contact)}`)
}

export function cmdContactList() {
  const contacts = contactsStore.loadAll()
  if (contacts.length === 0) {
    log('// no contacts')
    return
  }

  log(`// ${contacts.length} contact${contacts.length === 1 ? '' : 's'}`)
  for (const c of contacts) {
    log(formatContact(c))
  }
}

export function cmdContactLabel(id, label) {
  if (!contactsStore.updateLabel(id, label)) {
    log(`// not found: ${id}`)
    return
  }
  log(`// updated: ${id.slice(0, 8)}  label → ${label}`)
}

export function cmdContactRemove(id) {
  if (!contactsStore.findById(id)) {
    log(`// not found: ${id}`)
    return
  }
  contactsStore.remove(id)
  log(`// removed: ${id.slice(0, 8)}`)
}
