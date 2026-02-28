function createSearchId1() {
    window = global;
    if (!(null === (e = window) || void 0 === e ? void 0 : e.BigInt)) {
        var e, t = Date.now(), n = Math.ceil(0x7ffffffe * Math.random());
        return Number.parseInt(t.toString() + n.toString(), 10).toString(36)
    }
    var r = BigInt(Date.now())
      , o = BigInt(Math.ceil(0x7ffffffe * Math.random()));
    return r <<= BigInt(64),
    (r += o).toString(36)
}

function createSearchId() {
    const crypto = require('crypto-js');
    // 安全随机数生成（兼容旧浏览器）
    const getRandom = () => {
        if (crypto?.getRandomValues) {
            const array = new Uint32Array(1);
            crypto.getRandomValues(array);
            return array[0] % 0x7ffffffe + 1; // [1, 2147483646]
        } else {
            return Math.ceil(0x7ffffffe * Math.random());
        }
    };

    if (typeof BigInt !== 'undefined') {
        const timestamp = BigInt(Date.now());
        const random = BigInt(getRandom());
        const combined = (timestamp << BigInt(64)) + random;
        return combined.toString(36);
    } else {
        // 降级方案：时间戳 + 随机数的字符串拼接（Base36）
        const timestamp = Date.now().toString(36).padStart(8, '0'); // 固定8位
        const random = getRandom().toString(36).padStart(8, '0');    // 固定8位
        return timestamp + random; // 总长度16位（如 "0000001k5v3q+00000fh7"）
    }
}

console.log(createSearchId1())
