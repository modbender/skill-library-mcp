/**
 * @file concurrency.js
 * @author kelexine <https://github.com/kelexine>
 * @description Bounded concurrency pool — runs at most `limit` async tasks
 *              simultaneously. Queues excess work until capacity is free.
 *              Fully results-ordered: output indices match input indices.
 */

export class ConcurrencyPool {
	/**
	 * @param {number} limit - Max simultaneous in-flight tasks
	 */
	constructor(limit) {
		if (!Number.isInteger(limit) || limit < 1) {
			throw new RangeError(`ConcurrencyPool limit must be a positive integer, got: ${limit}`);
		}
		this.limit  = limit;
		this._active = 0;
		this._queue  = [];
	}

	/**
	 * Schedule `fn` to run as soon as a slot is available.
	 * @template T
	 * @param {() => Promise<T>} fn
	 * @returns {Promise<T>}
	 */
	run(fn) {
		return new Promise((resolve, reject) => {
			const task = async () => {
				this._active++;
				try {
					resolve(await fn());
				} catch (err) {
					reject(err);
				} finally {
					this._active--;
					this._drain();
				}
			};

			if (this._active < this.limit) {
				task();
			} else {
				this._queue.push(task);
			}
		});
	}

	_drain() {
		if (this._queue.length > 0 && this._active < this.limit) {
			this._queue.shift()();
		}
	}

	/** Current queue depth (waiting tasks). */
	get pending() {
		return this._queue.length;
	}

	/** Current in-flight task count. */
	get running() {
		return this._active;
	}

	/**
	 * Map over an array with bounded concurrency.
	 * Results are returned in the same order as input.
	 *
	 * @template T, R
	 * @param {T[]}                              items
	 * @param {(item: T, i: number) => Promise<R>} fn
	 * @param {number}                           limit
	 * @returns {Promise<R[]>}
	 */
	static map(items, fn, limit) {
		const pool = new ConcurrencyPool(limit);
		return Promise.all(items.map((item, i) => pool.run(() => fn(item, i))));
	}

	/**
	 * Like `map` but uses `Promise.allSettled` — never throws, returns
	 * `{ status, value?, reason? }[]` in input order.
	 *
	 * @template T, R
	 * @param {T[]}                              items
	 * @param {(item: T, i: number) => Promise<R>} fn
	 * @param {number}                           limit
	 * @returns {Promise<PromiseSettledResult<R>[]>}
	 */
	static mapSettled(items, fn, limit) {
		const pool = new ConcurrencyPool(limit);
		return Promise.allSettled(items.map((item, i) => pool.run(() => fn(item, i))));
	}
}
