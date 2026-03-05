#!/usr/bin/env node

/**
 * Mei Hua Yi Shu (Plum Blossom Divination) - Time-based
 * Logic:
 * 1. Upper Gua = Hour / 8 (remainder, 0=8)
 * 2. Lower Gua = Minute / 8 (remainder, 0=8)
 * 3. Moving Yao = (Hour + Minute) / 6 (remainder, 0=6)
 */

const GUA_NAMES = ["", "乾 (Qián)", "兑 (Duì)", "离 (Lí)", "震 (Zhèn)", "巽 (Xùn)", "坎 (Kǎn)", "艮 (Gèn)", "坤 (Kūn)"];
const GUA_SYMBOLS = ["", "☰", "☱", "☲", "☳", "☴", "☵", "☶", "☷"];
// Binary representation for Gua: 1=Yang, 0=Yin (from bottom to top)
const GUA_BINARY = ["", "111", "011", "101", "001", "110", "010", "100", "000"];

function getGuaInfo(index) {
  return { name: GUA_NAMES[index], symbol: GUA_SYMBOLS[index], binary: GUA_BINARY[index] };
}

function getBinaryFromIndex(index) {
  return GUA_BINARY[index];
}

function getIndexFromBinary(bin) {
  return GUA_BINARY.indexOf(bin);
}

function flip(bit) {
  return bit === '1' ? '0' : '1';
}

function main() {
  const args = process.argv.slice(2);
  let date = new Date();
  if (args.length > 0) {
    date = new Date(args.join(' '));
  }

  const hour = date.getHours();
  const minute = date.getMinutes();

  // 1. Upper Gua
  let upperIndex = hour % 8;
  if (upperIndex === 0) upperIndex = 8;

  // 2. Lower Gua
  let lowerIndex = minute % 8;
  if (lowerIndex === 0) lowerIndex = 8;

  // 3. Moving Yao
  let movingYao = (hour + minute) % 6;
  if (movingYao === 0) movingYao = 6;

  const upper = getGuaInfo(upperIndex);
  const lower = getGuaInfo(lowerIndex);

  // Full hexagram binary (bottom to top, Yao 1 to 6)
  let hexBin = lower.binary + upper.binary;

  // 4. Ben Gua (Original)
  const benGua = {
    upper: upper,
    lower: lower,
    full: hexBin
  };

  // 5. Bian Gua (Changed)
  let bianBinArr = hexBin.split('');
  bianBinArr[movingYao - 1] = flip(bianBinArr[movingYao - 1]);
  let bianBin = bianBinArr.join('');
  const bianGua = {
    upper: getGuaInfo(getIndexFromBinary(bianBin.substring(3, 6))),
    lower: getGuaInfo(getIndexFromBinary(bianBin.substring(0, 3))),
    full: bianBin,
    movingYao: movingYao
  };

  // 6. Hu Gua (Mutual)
  // Yao 2,3,4 as lower; Yao 3,4,5 as upper
  let huLowerBin = hexBin.substring(1, 4);
  let huUpperBin = hexBin.substring(2, 5);
  const huGua = {
    upper: getGuaInfo(getIndexFromBinary(huUpperBin)),
    lower: getGuaInfo(getIndexFromBinary(huLowerBin))
  };

  // 7. Cuo Gua (Opposite/Wrong)
  let cuoBin = hexBin.split('').map(flip).join('');
  const cuoGua = {
    upper: getGuaInfo(getIndexFromBinary(cuoBin.substring(3, 6))),
    lower: getGuaInfo(getIndexFromBinary(cuoBin.substring(0, 3)))
  };

  // 8. Zong Gua (Inverted/Reversed)
  let zongBin = hexBin.split('').reverse().join('');
  const zongGua = {
    upper: getGuaInfo(getIndexFromBinary(zongBin.substring(3, 6))),
    lower: getGuaInfo(getIndexFromBinary(zongBin.substring(0, 3)))
  };

  const result = {
    time: date.toLocaleString(),
    hour,
    minute,
    ben: benGua,
    bian: bianGua,
    hu: huGua,
    cuo: cuoGua,
    zong: zongGua
  };

  console.log(JSON.stringify(result, null, 2));
}

main();
