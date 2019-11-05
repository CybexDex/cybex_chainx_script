const { ApiBase, HttpProvider, WsProvider } = require('chainx.js');

(async () => {
  // 使用 http 连接
  // const api = new ApiBase(new HttpProvider('https://w1.chainx.org.cn/rpc'));
  // 使用 websocket 连接
  const api = new ApiBase(new WsProvider('wss://w1.chainx.org.cn/ws'))

  await api.isReady;

  const transferCallIndex = Buffer.from(api.tx.xAssets.transfer.callIndex).toString('hex');

  async function getTransfers(blockNumber) {
    const blockHash = await api.rpc.chain.getBlockHash(blockNumber);
    const block = await api.rpc.chain.getBlock(blockHash);
    const estrinsics = block.block.extrinsics;
    const transfers = [];
    // console.log(blockHash.toString('hex'));
    // console.log(JSON.stringify(block));
    for (let i = 0; i < estrinsics.length; i++) {
      const e = estrinsics[i];
      // if (Buffer.from(e.method.callIndex).toString('hex') === transferCallIndex) {
      if (true) {
        const allEvents = await api.query.system.events.at(blockHash);
        events = allEvents
          //.filter(({ phase }) => phase.type === 'ApplyExtrinsic' && phase.value.eqn(i))
          .map(event => {
            const o = event.toJSON();
            o.method = event.event.data.method;
            return o;
          });
        result = events[events.length - 1].method;

        transfers.push({
          index: i,
          blockHash: blockHash.toHex(),
          blockNumber: blockNumber,
          result,
          tx: {
            signature: e.signature.toJSON(),
            method: e.method.toJSON(),
          },
          events: events,
          txHash: e.hash.toHex(),
        });
      }
    }

    return transfers;
  }

  const transfers = await getTransfers(6772050);

  console.log(JSON.stringify(transfers));
  process.exit();
})();
