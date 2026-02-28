// SearchId值作成
function createSearchId() {
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

console.log(createSearchId())
