/**
 * Demo Task - 并行数据处理
 * 
 * 使用: node ../../bin/weave run -m demo -w 5 -t task-demo.js
 */

// 模拟输入数据
const inputs = Array(100).fill(0).map((_, i) => ({
  id: i,
  value: Math.random() * 1000,
  category: ['A', 'B', 'C', 'D'][Math.floor(Math.random() * 4)]
}));

// Map 函数 - 处理单个数据块
async function mapFunction(dataChunk, worker) {
  console.log(`  [Worker] 处理 ${dataChunk.length} 条数据...`);
  
  // 模拟耗时计算
  await new Promise(r => setTimeout(r, 100 + Math.random() * 200));
  
  // 计算统计
  const result = {
    count: dataChunk.length,
    sum: dataChunk.reduce((a, b) => a + b.value, 0),
    avg: dataChunk.reduce((a, b) => a + b.value, 0) / dataChunk.length,
    categories: dataChunk.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + 1;
      return acc;
    }, {}),
    worker: worker ? worker.name : 'unknown'
  };
  
  return result;
}

// Reduce 函数 - 汇总所有结果
async function reduceFunction(allResults) {
  console.log(`\n[Reduce] 汇总 ${allResults.length} 个 Worker 的结果...`);
  
  const total = allResults.reduce((acc, r) => ({
    count: acc.count + r.count,
    sum: acc.sum + r.sum,
    categories: Object.entries(r.categories).reduce((a, [k, v]) => {
      a[k] = (a[k] || 0) + v;
      return a;
    }, acc.categories)
  }), { count: 0, sum: 0, categories: {} });
  
  return {
    workers: allResults.length,
    totalCount: total.count,
    totalSum: Math.round(total.sum * 100) / 100,
    average: Math.round((total.sum / total.count) * 100) / 100,
    categoryDistribution: total.categories,
    workerDetails: allResults.map(r => ({
      worker: r.worker,
      count: r.count,
      avg: Math.round(r.avg * 100) / 100
    }))
  };
}

module.exports = {
  inputs,
  mapFunction,
  reduceFunction
};
