const Chainx = require('chainx.js').default;
const account = process.argv[2];

(async () => {
  // 目前只支持 websocket 链接
  const chainx = new Chainx('wss://w1.chainx.org/ws');

  // 等待异步的初始化
  await chainx.isRpcReady();
  chainx.on('disconnected', () => {process.exit()}) // websocket 链接断开
  // 查询某个账户的资产情况
  const fromAssets = await chainx.asset.getAssetsByAccount(account, 0, 10);

  console.log('bobAssets: ', JSON.stringify(fromAssets));

  // 构造交易参数（同步）
  process.exit();
  // chainx.provider.websocket.close();
})();

