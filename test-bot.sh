source ~/Py3Venv/qqbot-venv/bin/activate

echo 请等待 QQBot 启动成功...
read -n 1

echorun qq help
echorun qq list buddy
echorun qq list group
echorun qq list discuss

echorun qq send buddy hcj nihao 你好 wohao
echorun qq send group connie wohao 我好 wohao
echorun qq send discuss "Eva、hcj" tahao 他好 tahao

echorun qq get buddy hcj
echorun qq get group connie
echorun qq get discuss "Eva、hcj"

echorun qq member group connie
echorun qq member discuss "Eva、hcj"

echorun qq restart

echorun qq stop
